from utils.channel import Channel
from utils.config import PC_IP, DYNAMICS_PORT
from threading import Thread, Lock
import math
import parse
from queue import Queue
from utils.circular_queue import CircularQueue

ORIGIN_UPPER = 180
THETA_REMAP = 135
PHI_REMAP = 135


class Dynamics:
    """
    This the dynamics subsystem. Preprocessing the posture data sequence from the joysticks,
    do the spatial and temporal remapping.
    Note: The angle variable: (theta,phi) will only be unpacked in this subsystem!
        All other parts should take them as a whole posture data tuple.
    """

    def __init__(self) -> None:
        self.channel = Channel("Dynamics")
        self.channel.becomeServer(PC_IP, DYNAMICS_PORT, self.recv)
        self.listen_t = Thread(target=self.channel.listen, daemon=True)
        self.listen_t.start()

        # self.joystick_queue = Queue(10)
        self.joystick_lock = Lock()
        self._joystick_data = ((0, 0), (0, 0, 0))
        self.updated = False

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
        theta, phi, move, color, record = parse.parse("{:f}, {:f}, {:d}, {:d}, {:d}", msg)
        # print(theta, phi)
        # theta, phi = parse.parse("fptich:{:f}, froll:{:f}", msg)
        theta, phi = Dynamics.spatial_remap(theta, phi)
        # theta, phi = self.temporal_remap(theta, phi)
        data = ((theta, phi), (move, color, record))  # (posture,buttons)
        # self.joystick_queue.put(data)
        self.joystick_data = data

    @classmethod
    def nonlinear_cut(cls, value, origin_upper, remap_upper):
        return remap_upper * math.sin(value * math.pi / origin_upper / 2)

    @classmethod
    def spatial_remap(cls, theta, phi):
        theta = Dynamics.nonlinear_cut(theta, ORIGIN_UPPER, THETA_REMAP)
        phi = Dynamics.nonlinear_cut(phi, ORIGIN_UPPER, PHI_REMAP)
        return theta, phi

    def temporal_remap(self, theta, phi):
        # TODO: Interpolation
        return theta, phi


if __name__ == "__main__":
    d = Dynamics()
