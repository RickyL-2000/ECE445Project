from utils.channel import Channel
from utils.config import PC_IP, DYNAMICS_PORT
from threading import Thread
import numpy as np
import math
import parse
import queue

ORIGIN_UPPER = 360
THETA_REMAP = 240
PHI_REMAP = 240


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

        self.joystick_queue = queue.Queue(100)

    def recv(self, msg):
        theta, phi, move, color, record = parse.parse("fptich:{:f}, froll:{:f}, move:{:d}, color:{:d}, record:{:d}",
                                                      msg)
        # theta, phi = parse.parse("fptich:{:f}, froll:{:f}", msg)
        theta, phi = self.spatial_remap(theta, phi)
        theta, phi = self.temporal_remap(theta, phi)
        joystick_data = ((theta, phi), (move, color, record))  # (posture,buttons)

        self.joystick_queue.put(joystick_data)

    @classmethod
    def nonlinear_cut(cls, value, origin_upper, remap_upper):
        return remap_upper * math.log(value) / math.log(origin_upper)

    def spatial_remap(self, theta, phi):
        theta = Dynamics.nonlinear_cut(theta, ORIGIN_UPPER, THETA_REMAP)
        phi = Dynamics.nonlinear_cut(phi, ORIGIN_UPPER, PHI_REMAP)
        return theta, phi

    def temporal_remap(self, theta, phi):
        # TODO: Interpolation
        return theta, phi


if __name__ == "__main__":
    d = Dynamics()
