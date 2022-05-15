import queue
import random
import time
import pygame
from threading import Thread, Lock

from transitions import Machine
import math
from utils.channel import Channel
from utils.circular_queue import CircularQueue
from dynamics import PITCH_REMAP,ROLL_REMAP


PERIOD = 0.009  # s


class Gimbal:
    states = ["mimic", "repeat", "random", "record"]

    transitions = [
            {'trigger':'move_button_press', 'source':'mimic', 'dest':'repeat'},
            {'trigger':'move_button_press', 'source':'repeat', 'dest':'random'},
            {'trigger':'move_button_press', 'source':'random', 'dest':'mimic'},

            {'trigger':'record_button_change', 'source':'mimic', 'dest':'record'},
            {'trigger':'record_button_change', 'source':'record', 'dest':'mimic'}
    ]

    def __init__(self) -> None:
        self.machine = Machine(
                model=self, states=Gimbal.states, transitions=Gimbal.transitions, initial='mimic',
                ignore_invalid_triggers=True)


class Color:
    states = ["music", "random"]
    transitions = [
            {'trigger':'color_button_press', 'source':'music', 'dest':'random'},
            {'trigger':'color_button_press', 'source':'random', 'dest':'music'},
    ]

    def __init__(self) -> None:
        self.machine = Machine(
                model=self, states=Color.states, transitions=Color.transitions, initial='music',
                ignore_invalid_triggers=True)


class RandomGenerator:
    def __init__(self):
        self.random_seed = 12345

    def random_posture(self,hsv):
        h,s,v = hsv
        return math.cos(h/180*math.pi) * PITCH_REMAP, math.sin(h/180*math.pi) * ROLL_REMAP

    def random_color(self,hsv):
        return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)


class Control:
    def __init__(self, dynamics, music_player, lights_config, ):
        """
        :param lights_config: socket client information of light arrays, with form
                { "lightA":
                    {"host":"192.168.31.77",
                     "port":1234},
                  "lightB":{...},
                  ...
                }
        :return:
        """
        self.gimbal_fsm = Gimbal()
        self.color_fsm = Color()
        self.random_gene = RandomGenerator()
        self.dynamics = dynamics
        self.music_player = music_player

        # buttons
        self.last_button_state = [0, 0, 0,0]

        self.light_connections = {}

        # record buffer for repeat move mode
        # self.record_buffer = CircularQueue(1000)
        self.record_buffer = []
        self.repeat_count = 0

        # shared data for command
        self._cur_command = ""
        self.cur_command_lock = Lock()
        self.command_updated = False

        light_conn_ts = []
        for light_id in lights_config:
            light_conn_ts.append(
                    Thread(target=self.connect_lights, args=(light_id, lights_config[light_id]), daemon=True))
        for t in light_conn_ts:
            t.start()
        for t in light_conn_ts:
            t.join()

    @property
    def cur_command(self):
        self.cur_command_lock.acquire(blocking=True)
        data = self._cur_command
        self.command_updated = False
        self.cur_command_lock.release()
        return data

    @cur_command.setter
    def cur_command(self, value):
        self.cur_command_lock.acquire(blocking=True)
        self._cur_command = value
        self.command_updated = True
        self.cur_command_lock.release()

    def __repr__(self):
        return f"{time.time():.3f} | gimbal:{self.gimbal_fsm.state}, command_len:{self.command_queue.qsize()}, record_len:{len(self.record_buffer)} command:{self.cur_command}"

    def connect_lights(self, light_id, light_config):
        self.light_connections[light_id] = Channel(light_id).becomeClient(light_config["host"], light_config["port"])

    def button_trigger(self, buttons):
        move, color, record, play = tuple([x == 1 for x in buttons])

        # when move button is changed from 0 to 1
        if move == True and move != self.last_button_state[0]:
            self.gimbal_fsm.trigger("move_button_press")

        # when color is button changed from 0 to 1
        if color == True and color != self.last_button_state[1]:
            self.color_fsm.trigger("color_button_press")

        # when record button is different from the inner state
        if record != self.gimbal_fsm.is_record():
            self.gimbal_fsm.trigger("record_button_change")
            if self.gimbal_fsm.is_record():
                self.record_buffer = []

        if play !=self.last_button_state[3]:
            if play:
                self.music_player.unpause()
            else:
                self.music_player.pause()
            


        self.last_button_state = (move, color, record,play)

    def filter(self, dynamics_posture, music_analysis_color,hsv):
        if self.gimbal_fsm.state == "mimic":
            filtered_posture = dynamics_posture
        elif self.gimbal_fsm.state == "record":
            # let light mimic the joystick and record the posture data in the buffer
            filtered_posture = dynamics_posture
            self.record_buffer.append(dynamics_posture)
        elif self.gimbal_fsm.state == "random":
            filtered_posture = self.random_gene.random_posture(hsv)
        elif self.gimbal_fsm.state == "repeat":
            # take a recorded command from buffer, than restore it.
            filtered_posture = self.record_buffer[self.repeat_count]
            self.repeat_count = (self.repeat_count + 1) % len(self.record_buffer)
        else:
            raise Exception("Unknown state for gimbal FSM")

        if self.color_fsm.state == "music":
            filtered_color = music_analysis_color
        elif self.color_fsm.state == "random":
            filtered_color = self.random_gene.random_color(hsv)
        else:
            raise Exception("Unknown state for color FSM")

        return filtered_posture, filtered_color

    def recv(self):
        """receive command data from other subsystem in the central server,
        apply the finite state machine filter and store the string command
        to the command queue

        interface:
            self.dynamics.joystick_queue: posture data queue,
                format: tuple(theta, phi), tuple(move, color, record)
            self.music_analysis.color_queue: led color data queue
                format: tuple(R, G, B)
        output:
            self.command_queue: string type command for the light arrays
                format: "(theta, phi), (R, G, B)"
        """
        d_posture, buttons = (0.0, 0.0), (0, 0, 0,0)
        posture_cache = [(0, 0)]
        while True:
            # ============  get posture data from joystick
            if self.dynamics.updated:
                d_posture, buttons = self.dynamics.joystick_data
                # print(f"recv from dynamics {d_posture}")

            # ============  get color data from music analysis subsystem, according the play states
            m_color, hsv = self.music_player.get_color("both")
            if self.music_player.get_busy():
                # pure green indicates no music is playing
                m_color = (0, 255, 0)

            self.button_trigger(buttons)
            posture_command, color_command = self.filter(d_posture, m_color,hsv)
            # color_command = []
            self.cur_command = f"{posture_command[0]:.2f}, {posture_command[1]:.2f}, {color_command[0]}, {color_command[1]}, {color_command[2]}"
            # self.cur_command = f"{', '.join([f'{x:.2f}' for x in posture_command])}, {', '.join([f'{x}' for x in color_command])}"

            time.sleep(PERIOD)

    def send(self):
        """Periodly send the command from the command queue to the light tcp server"""
        command = ""
        while True:
            if self.command_updated:
                command = self.cur_command
                # try:
                #     # command = self.command_queue.get(block=True)
                #     # print(f"{time.time():.3f} | gimbal:{self.gimbal_fsm.state}, command_len:{self.command_queue.qsize()}, record_len:{self.record_buffer.qsize()} command:{command}")
                #     # self.cur_command = command
                # except queue.Empty as e:
                #     # FIXME: The queue should never be empty, as mentioned in recv and the maintainance of control subsystem
                #     #       here just do nothing to variable `command` to send the same command when crash
                #     pass
                # for id in self.light_connections:
                #     send_t = Thread(target=self.light_connections[id].send, args=(
                #             command,), daemon=True)
                #     send_t.start()
                for id in self.light_connections:
                    self.light_connections[id].send(command)
                # print("send" + command)
                # time.sleep(PERIOD / 2)

    def monitor(self):
        while True:
            print(self)
            time.sleep(PERIOD)

    def run(self):
        # self.music_player.play()
        recv_t = Thread(target=self.recv, daemon=True)
        send_t = Thread(target=self.send, daemon=True)
        player_t = Thread(target=self.music_player.run, daemon=True)
        monitor_t = Thread(target=self.monitor, daemon=True)

        recv_t.start()
        send_t.start()
        player_t.start()
        # monitor_t.start()

        recv_t.join()
        send_t.join()
        player_t.join()
        # monitor_t.join()
