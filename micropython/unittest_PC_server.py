import utils.log as log
from utils.channel import Channel
# from utils.config import ESP_IP, PC_IP, BOARDCAST_IP, PORT

if __name__=="__main__":
    def recv(msg):
        log.info(msg)
    c = Channel("CentralServer")
    c.becomeServer("192.168.31.177", 12345, recv)
    c.listen()
