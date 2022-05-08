import queue
import random
import time
from threading import Thread

from transitions import Machine

from utils.channel import Channel


class CircularQueue(queue.Queue):
    def __init__(self, maxsize):
        super().__init__(maxsize)

    def put(self, *arg, **kwarg):
        if self.full():
            self.get(block=False)
        super().put(*arg, kwarg)


class Gimbal:
    states = ["mimic", "repeat", "random", "record"]

    transitions = [
            {'trigger':'move_button_press', 'source':'mimic', 'dest':'repeat'},
            {'trigger':'move_button_press', 'source':'repeat', 'dest':'random'},
            {'trigger':'move_button_press', 'source':'random', 'dest':'mimic'},

            {'trigger':'record_button_change', 'source':'mimic','dest':'record'},
            {'trigger':'record_button_change', 'source':'record','dest':'mimic'}
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
    def __init__(self, dynamics, music_analysis, lights_config) -> None:
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
        self.music_analysis = music_analysis
        self.command_queue = queue.Queue(100)
        self.light_connections = {}
        self.record_buffer = CircularQueue(1000)

        light_conn_ts = []
        for light_id in lights_config:
            light_conn_ts.append(
                    Thread(target=self.connect_lights, args=(light_id, lights_config[light_id]), daemon=True))
        for t in light_conn_ts:
            t.start()
        for t in light_conn_ts:
            t.join()

    def __repr__(self):
        return f"{time.time():.3f} | gimbal:{self.gimbal_fsm.state}, command_len:{self.command_queue.qsize()}, record_len:{self.record_buffer.qsize()}"

    def connect_lights(self, light_id, light_config):
        self.light_connections[light_id] = Channel(light_id).becomeClient(light_config["host"], light_config["port"])

    # def channel_recv(self, msg):
    #     raise Exception(
    #             "method deprecated, all msg received in dynamics subsystem")
    #     record, move, color = parse.parse(
    #             "record:{:d}, move:{:d}, color:{:d}", msg)
    #     # TODO: zero mode

    def button_trigger(self, buttons):
        move, color, record = tuple([x == 1 for x in buttons])

        if move == True:
            self.gimbal_fsm.trigger("move_button_press")

        if color == True:
            self.color_fsm.trigger("color_button_press")

        if record != self.gimbal_fsm.is_record():
            self.gimbal_fsm.trigger("record_button_change")
            if self.gimbal_fsm.is_record():
                self.record_buffer.queue.clear()

    def filter(self, dynamics_posture, music_analysis_color):
        if self.gimbal_fsm.state == "mimic":
            filtered_posture = dynamics_posture
        elif self.gimbal_fsm.state == "record":
            # let light mimic the joystick and record the posture data in the buffer
            filtered_posture = dynamics_posture
            self.record_buffer.put(dynamics_posture)
        elif self.gimbal_fsm.state == "random":
            filtered_posture = self.random_gene.random_posture()
        elif self.gimbal_fsm.state == "repeat":
            # take a recorded command from buffer, than restore it.
            try:
                filtered_posture = self.record_buffer.get(block=False)
            except queue.Empty:
                filtered_posture = dynamics_posture
            self.record_buffer.put(filtered_posture)
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
        while True:
            try:
                d_posture, buttons = self.dynamics.joystick_queue.get(
                        block=False)
            except queue.Empty as e:
                # give repeated or random posture data
                # FIXME: The queue should never be empty with the temporal remap in the dynamic subsystem
                d_posture, buttons = (100.0, 100.0), (0, 0, 0)

            try:
                m_color = self.music_analysis.color_queue.get(block=False)
            except queue.Empty as e:
                # FIXME: The queue should never be empty with the as the color data is preprocessed in the dynamic subsystem
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
        """Periodly send the command from the command queue to the light tcp server"""
        command = ""
        while True:
            try:
                command = self.command_queue.get(block=False)
            except queue.Empty as e:
                # FIXME: The queue should never be empty, as mentioned in recv and the maintainance of control subsystem
                #       here just do nothing to variable `command` to send the same command when crash
                pass
            for id in self.light_connections:
                send_t = Thread(target=self.light_connections[id].send, args=(
                        command,), daemon=True)
                send_t.start()
            time.sleep(1)

    def monitor(self):
        while True:
            print(self)
            time.sleep(1)

    def run(self):
        recv_t = Thread(target=self.recv, daemon=True)
        send_t = Thread(target=self.send, daemon=True)
        monitor_t = Thread(target=self.monitor, daemon=True)

        recv_t.start()
        send_t.start()
        monitor_t.start()

        recv_t.join()
        send_t.join()
        monitor_t.join()
