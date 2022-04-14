import utils.log as log
from utils.config import BACKLOG, BUFFER_SIZE
try:
    import usocket as socket
    import ustruct as struct
    import ujson as json
except:
    import socket
    import struct
    import json


class Channel:
    def __init__(self, name) -> None:
        self.name = name
        self.is_server = False
        self.s = socket.socket()  # 创建套接字

    def becomeServer(self, local_host, local_port, recv_callback):
        self.local_host = local_host
        self.local_port = local_port
        self.recv_callback = recv_callback

        self.is_server = True
        self.s.bind((self.local_host, self.local_port))  # 绑定地址和端口号
        self.s.listen(BACKLOG)  # 监听套接字, 最多允许backlog个连接
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 设置套接字
        log.success('server host at {}:{}'.format(self.local_host, self.local_port))
        log.info('tcp waiting...')

    def becomeClient(self, server_host, server_port):
        self.is_server = False
        self.server_host = server_host
        self.server_port = server_port
        self.s.connect((self.server_host, self.server_port))
        log.success("connect to {}:{}".format(self.server_host, self.server_port))

    def listen(self):
        if not self.is_server:
            log.error(
                "only server can listen, set as server by calling becomeServer()")
            return
        try:
            while True:
                log.info("accepting.....")
                conn, addr = self.s.accept()  # 接收连接请求，返回收发数据的套接字对象和客户端地址
                log.success("{} connected".format(addr))

                while True:
                    chunk = conn.recv(BUFFER_SIZE)
                    if len(chunk) < BUFFER_SIZE:
                        break
                    slen = struct.unpack('>L', chunk)[0]
                    chunk = conn.recv(slen)
                    while len(chunk) < slen:
                        chunk = chunk + conn.recv(slen - len(chunk))
                    obj = json.loads(chunk.decode("utf-8"))

                    self.recv_callback(obj)

        except Exception as e:
            log.error(e)
            self.s.close()
            log.error("server quit abnormally!")
            return

    def send(self, msg):
        s = json.dumps(msg).encode("utf-8")
        slen = struct.pack(">L", len(s))
        self.s.send(slen + s)
        log.info("send to {}: {}".format(self.server_host,msg))
