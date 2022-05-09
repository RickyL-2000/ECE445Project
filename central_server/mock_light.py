from utils.channel import Channel
from utils.config import PC_IP, DYNAMICS_PORT, LIGHT_MOCK, LIGHT_PORT
import time


def recv(msg):
    theta, phi = parse.parse("({:f}, {:f})", msg.split(", (")[0])
    print(f"{theta:.2f}, {phi:.2f}")


c = Channel("mock_light")
c.becomeServer(LIGHT_MOCK, LIGHT_PORT, recv)
c.listen()