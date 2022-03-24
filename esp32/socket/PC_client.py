import sys
import os
sys.path.append(
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
        "utils")
)
import log

import config
import socket  # 导入 socket 模块
import time

host = config.PC_IP
port = config.PORT  # 设置端口号
buffer_size = config.BUFFER_SIZE  # socket 缓存区，决定每次给硬件缓存区多少数据

with socket.socket() as client:  # 创建 socket 对象

    log.info("try to connect to {}:{}".format(host, port))
    client.connect((host, port))
    log.success("success")

    while True:
        msg = input("send to \t{}:\t".format(host)).strip()
        if not msg:
            continue
        if msg == "quit":
            break
        client.sendall(msg.encode("utf-8"))
        data = client.recv(buffer_size)
        log.info("receive from \t{}:\t".format(host) + data.decode("utf-8"))

