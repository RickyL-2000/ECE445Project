import time

from transitions import Machine
import random
from utils.channel import Channel
from utils.config import PC_IP, CONTROL_PORT
import queue
from threading import Thread


class Gimbal:
    states = ["mimic", "repeat", "random", "record"]

    transitions = [
        {'trigger': 'move_button_press', 'source': 'mimic', 'dest': 'repeat'},
        {'trigger': 'move_button_press', 'source': 'repeat', 'dest': 'random'},
        {'trigger': 'move_button_press', 'source': 'random', 'dest': 'mimic'},

        {'trigger': 'record_button_change', 'source': 'mimic',
            'dest': 'record', 'after': "recording_change"},
        {'trigger': 'record_button_change', 'source': 'record',
         'dest': 'mimic', 'after': "recording_change"}
    ]

    def __init__(self) -> None:
        self.is_recording = False

        self.machine = Machine(
            model=self, states=Gimbal.states, transitions=Gimbal.transitions, initial='mimic',
            ignore_invalid_triggers=True)

    def recording_change(self):
        self.is_recording = not self.is_recording


class Color:
    states = ["music", "random"]
    transitions = [
        {'trigger': 'color_button_press', 'source': 'music', 'dest': 'random'},
        {'trigger': 'color_button_press', 'source': 'random', 'dest': 'music'},
    ]

    def __init__(self) -> None:
        self.is_recording = False

        self.machine = Machine(
            model=self, states=Color.states, transitions=Color.transitions, initial='random',
            ignore_invalid_triggers=True)


class RandomGenerator:
    def __init__(self):
        self.random_seed = 12345

    def random_posture(self):
        return random.random() * 360, random.random() * 360

    def random_color(self):
        return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)


class Control:
    def __init__(self, dynamics, music_analysis,lights_config) -> None:
        self.gimbal_fsm = Gimbal()
        self.color_fsm = Color()
        self.random_gene = RandomGenerator()
        self.dynamics = dynamics
        self.music_analysis = music_analysis
        self.command_queue = queue.Queue(100)
        self.light_connections = {}
        self.connect_lights(lights_config)

    def connect_lights(self, lights_config):
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
        for light in lights_config:
            self.light_connections[light] = Channel(light).becomeClient(
                lights_config[light]["host"], lights_config[light]["port"])

    def channel_recv(self, msg):
        raise Exception(
            "method deprecated, all msg received in dynamics subsystem")
        record, move, color = parse.parse(
            "record:{:d}, move:{:d}, color:{:d}", msg)
        # TODO: zero mode

    def button_trigger(self, buttons):
        move, color, record = buttons
        if move == True:
            self.gimbal_fsm.trigger("move_button_press")

        if color == True:
            self.color_fsm.trigger("color_button_press")

        if record != self.gimbal_fsm.is_recording:
            self.gimbal_fsm.trigger("record_button_change")

    def filter(self, dynamics_posture, music_analysis_color):

        if self.gimbal_fsm.state == "mimic":
            filtered_posture = dynamics_posture
        elif self.gimbal_fsm.state == "random":
            filtered_posture = self.random_gene.random_posture()
        elif self.gimbal_fsm.state == "repeat":
            # TODO: record the posture data and send them repeatly
            pass
        else:
            raise Exception("Unknown state for gimbal FSM")

        if self.color_fsm.state == "music":
            filtered_color = music_analysis_color
        elif self.color_fsm.state == "random":
            filtered_color = self.random_gene.random_color()
        else:
            raise Exception("Unknown state for color FSM")

        return filtered_posture, filtered_color

    def recv(self):
        while True:
            print("recv rountine")
            try:
                d_posture, buttons = self.dynamics.joystick_queue.get(
                    block=False)
            except queue.Empty as e:
                # give repeated or random posture data
                d_posture, buttons = (100.0, 100.0), (0, 0, 0)

            try:
                m_color = self.music_analysis.color_queue.get(block=False)
            except queue.Empty as e:
                # give repeated or random posture data
                m_color = (0, 0, 0)
            except Exception as e:
                # give repeated or random posture data
                m_color = (0, 0, 0)

            self.button_trigger(buttons)
            posture_command, color_command = self.filter(d_posture, m_color)
            self.command_queue.put(
                f"{posture_command}, {color_command}", block=False)

            time.sleep(1)

    def send(self):
        command = ""
        while True:
            print("send rountine")
            try:
                command = self.command_queue.get(block=False)
            except queue.Empty as e:
                # give repeated or random posture data
                # command = "(0, 0, 0, 0, 0)" # this line is only for test
                pass
            for id in self.light_connections:
                send_t = Thread(target=self.light_connections[id].send, args=(
                    command,), daemon=True)
                send_t.start()
            time.sleep(1)

    def run(self):
        recv_t = Thread(target=self.recv, daemon=True)
        send_t = Thread(target=self.send, daemon=True)
        recv_t.start()
        send_t.start()
        recv_t.join()
        send_t.join()
