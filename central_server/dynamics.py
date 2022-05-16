from utils.channel import Channel
from utils.config import PC_IP, DYNAMICS_PORT
from threading import Thread, Lock
import math
import parse
from queue import Queue
from utils.circular_queue import CircularQueue

ORIGIN_UPPER = 180
PITCH_REMAP = 90
ROLL_REMAP = 135


class Dynamics:
    """
    This the dynamics subsystem. Preprocessing the posture data sequence from the joysticks,
    do the spatial and temporal remapping.
    Note: The angle variable: (pitch,roll) will only be unpacked in this subsystem!
        All other parts should take them as a whole posture data tuple.
    """

    def __init__(self) -> None:
        self.channel = Channel("Dynamics")
        self.channel.becomeServer(PC_IP, DYNAMICS_PORT, self.recv)
        self.listen_t = Thread(target=self.channel.listen, daemon=True)
        self.listen_t.start()

        # self.joystick_queue = Queue(10)
        self.joystick_lock = Lock()
        self._joystick_data = ((0, 0), (0, 0, 0, 0))
        self.updated = False
        self.last_buffer_len = 20
        self.last_pitch = [0] * self.last_buffer_len
        self.last_roll = [0] * self.last_buffer_len
        self.count = 1

    @property
    def joystick_data(self):
        self.joystick_lock.acquire(blocking=True)
        data = self._joystick_data
        self.updated = False
        self.joystick_lock.release()
        return data

    @joystick_data.setter
    def joystick_data(self, value):
        self.joystick_lock.acquire(blocking=True)
        self._joystick_data = value
        self.updated = True
        self.joystick_lock.release()

    def recv(self, msg):
        # print(msg)
        pitch, roll, move, color, record, play = parse.parse("{:f}, {:f}, {:d}, {:d}, {:d}, {:d}", msg)

        pitch, roll = Dynamics.spatial_remap(pitch, roll)
        pitch, roll = self.temporal_remap(pitch, roll)

        data = ((-pitch, roll), (move, color, record,play))  # (posture,buttons)

        self.joystick_data = data

    @classmethod
    def nonlinear_cut(cls, value, origin_upper, remap_upper):
        return remap_upper * math.sin(value * math.pi / origin_upper / 2)

    @classmethod
    def spatial_remap(cls, pitch, roll):
        pitch = Dynamics.nonlinear_cut(pitch, ORIGIN_UPPER, PITCH_REMAP)
        roll = Dynamics.nonlinear_cut(roll, ORIGIN_UPPER, ROLL_REMAP)
        return pitch, roll

    def temporal_remap(self, pitch, roll):
        # when shake severely, the value will be it's opposite for a few sample data, we need to handle it here
        self.last_pitch[self.count] = pitch
        self.last_roll[self.count] = roll
        sign_pitch = 1 if sum(self.last_pitch) > 0 else -1
        sign_roll = 1 if sum(self.last_roll) > 0 else -1
        self.count = (self.count + 1) % self.last_buffer_len

        return sign_pitch * abs(pitch), sign_roll * abs(roll)


if __name__ == "__main__":
    d = Dynamics()
