from utils.channel import Channel
from utils.config import PC_IP, DYNAMICS_PORT
import time

c = Channel("mock_joystick")
c.becomeClient(PC_IP, DYNAMICS_PORT)
for i in range(1, 360):
    command = f"{(i * 1.0, i * 2.0, 0 if i % 10 else 1, 0, 0)}"
    c.send(command)
    time.sleep(1)
