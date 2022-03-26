
from threading import Thread
import socket
import config
import sys
import os
sys.path.append(
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
        "utils")
)
import log

def main():
    # boardcast the service to LAN
    ip = socket.gethostbyname(socket.gethostname())
    port = config.PORT
    backlog = config.BACKLOG

    with socket.socket() as server:
        # setup socket
        server.bind((ip, port))
        server.listen(backlog)
        # server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # start thread for each connection
        while True:
            conn, addr = server.accept()
            new_event = Thread(target=connect, args=(conn, addr))
            new_event.start()


def connect(conn, addr):
    log.info("connected from {}".format(addr))
    while True:
        data = conn.recv(1024).decode("utf-8")
        log.info("from {}: {}".format(addr, data))
        if(len(data) == 0):  # 判断客户端是否断开连接
            print("close socket")
            conn.close()  # 关闭套接字
            return
        ret = conn.send(data.upper().encode("utf-8"))  # 发送数据


if __name__ == "__main__":
    main()
