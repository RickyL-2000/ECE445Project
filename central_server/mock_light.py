from utils.channel import Channel
from utils.config import PC_IP, DYNAMICS_PORT, LIGHT_MOCK, LIGHT_PORT
import time
import parse


def recv(msg):
    cmd = parse.parse("{:f}, {:f}, {:d}, {:d}, {:d}", msg.split(", (")[0])
    print(f"{', '.join([str(x) for x in cmd])}")


c = Channel("mock_light")
c.becomeServer(LIGHT_MOCK, LIGHT_PORT, recv)
c.listen()