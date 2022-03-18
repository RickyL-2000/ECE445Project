from time import sleep
from socket.client import listen as client_listen
from socket.server import listen as server_listen
from utils.wifi import blink_connect
from utils.uart import uart_loopback


print("start")

blink_connect()
sleep(1)
client_listen()
