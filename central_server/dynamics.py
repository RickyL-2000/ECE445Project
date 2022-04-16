from utils.channel import Channel
from utils.config import PC_IP, DYNAMICS_PORT
import numpy as np

THETA_RANGE = 360
THETA_REMAP = 240
PHI_RANGE = 360
PHI_REMAP = 240


class Dynamics:
    def __init__(self) -> None:
        self.setup_channel()

    def setup_channel(self):
        self.c = Channel("Dynamics")
        self.c.becomeServer(PC_IP, DYNAMICS_PORT, self.recv)
        self.c.listen()

    def recv(self, msg):
        x, y, z = msg
        theta = np.arccos(z/np.sqrt(x**2+y**2+z**2))
        phi = np.arctan(y, z)
        theta, phi = self.spatial_remap(theta, phi)
        theta, phi = self.spatial_remap(theta, phi)

    def spatial_remap(self, theta, phi):
        theta = THETA_REMAP*np.log(theta)/np.log(THETA_RANGE)
        phi = PHI_REMAP*np.log(phi)/np.log(PHI_RANGE)
        return theta, phi
    
    def temporal_remap(self,theta,phi):
        pass


if __name__ == "__main__":
    d = Dynamics()
