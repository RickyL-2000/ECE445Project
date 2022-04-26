
import utils.log as log
from utils.channel import Channel
import time
import socket

bala = "abcdefghijklmnopqrstuvwxyz"

if __name__=="__main__":
    c = Channel("CentralClient")
    c.becomeClient("192.168.31.7", 12345)
    for i in range(100):
        c.send(str((i,i+1,i+2,i+3,i+4)))
        time.sleep(0.01)
        # c.send("msg"+str(i)+": "+bala*10*abs(i-5))
    c.close()
