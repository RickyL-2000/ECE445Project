from utils.channel import Channel
from utils.config import PC_IP, DYNAMICS_PORT
import time

c = Channel("mock_joystick")
c.becomeClient(PC_IP, DYNAMICS_PORT)
while True:
    for i in range(1, 180):
        move_button = 1 if (i % 10 == 0) else 0
        record_button = 1 if (i % 10 in [2, 3, 4, 5, 6, 7, 8]) else 0
        command = f"{0*1.0}, {0*1.0}, {0}, {0}, {0}, {0}"
        c.send(str(command))
        print(f"send {command}")
        time.sleep(0.001)
