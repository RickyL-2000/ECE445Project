
import utils.log as log
from utils.channel import Channel
from utils.config import ESP_IP, PC_IP, BOARDCAST_IP, PORT

if __name__=="__main__":
    c = Channel("CentralClient")
    c.becomeClient(ESP_IP, PORT)
    for i in range(10):
        c.send("msg"+str(i))
