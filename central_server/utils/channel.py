import utils.log as log
from utils.config import BACKLOG, BUFFER_SIZE

try:
    import usocket as socket
    import ustruct as struct
    import ujson as json

    CENTRAL_SERVER = False
except:
    CENTRAL_SERVER = True
    import socket
    import struct
    import json
    from multiprocessing import Process
    from threading import Thread


class Channel:
    unconnected = 0
    connected = 1
    connecting = 2

    def __init__(self, name, verbose=False) -> None:
        self.name = name
        self.is_server = False
        self.verbose = verbose

        # server
        self.is_server = False
        self.local_host = None
        self.local_port = None
        self.recv_callback = None
        self.s = None
        self.connections = None

        # client
        self.connect_flag = False
        self.server_host = None
        self.server_port = None
        self.s = None

    def close(self):

        self.s.shutdown(socket.SHUT_WR)
        self.s.close()

    # ======================================  server method start  ========================================

    def becomeServer(self, local_host, local_port, recv_callback):
        self.is_server = True
        self.local_host = local_host
        self.local_port = local_port
        self.recv_callback = recv_callback
        self.s = socket.socket()  # 创建套接字

        self.connections = {}

        self.s.bind((self.local_host, self.local_port))  # 绑定地址和端口号
        self.s.listen(BACKLOG)  # 监听套接字, 最多允许backlog个连接
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 设置套接字
        log.success('server host at {}:{}'.format(self.local_host, self.local_port))
        if self.verbose: log.info('tcp waiting...')

    def listen(self) -> None:
        if not self.is_server:
            log.error(
                    "only server can listen, set as server by calling becomeServer()")
            return
        while True:
            if self.verbose:
                if self.verbose: log.info("accepting.....")
            conn, addr = self.s.accept()  # 接收连接请求，返回收发数据的套接字对象和客户端地址
            log.success("{} connected".format(addr))
            if CENTRAL_SERVER:
                if addr[0] not in self.connections:
                    self.connections[addr[0]] = conn
                else:
                    self.connections[addr[0]].close()
                    self.connections[addr[0]] = conn
                listen_t = Thread(target=self.client_listen, args=(conn, addr), daemon=True)
                listen_t.start()
            else:
                self.client_listen(conn, addr)

    def client_listen(self, conn, addr):
        try:
            while True:
                chunk = conn.recv(BUFFER_SIZE)
                if len(chunk) < BUFFER_SIZE:
                    break
                slen = struct.unpack('<L', chunk)[0]
                chunk = conn.recv(slen)
                while len(chunk) < slen:
                    chunk = chunk + conn.recv(slen - len(chunk))
                obj = chunk.decode("ascii")
                if self.verbose: log.info(f"recv from {addr}: {obj}")

                self.recv_callback(obj)

        except Exception as e:
            log.error(e)
            conn.close()
            log.error("server quit abnormally!")
            return

    # ======================================  server method end  ========================================

    # ======================================  client method start  ========================================

    def becomeClient(self, server_host, server_port):
        self.is_server = False
        self.connect_flag = Channel.unconnected
        self.server_host = server_host
        self.server_port = server_port
        self.s = None
        self.connect_to_server()
        return self

    def connect_to_server(self):
        # check the connection flag
        if self.connect_flag == Channel.unconnected:
            self.connect_flag = Channel.connecting
        else:
            return

        if self.s is not None:
            # self.s.shutdown(socket.SHUT_RDWR)
            self.s.close()
        try:
            self.s = socket.socket()  # 创建套接字
            self.s.connect((self.server_host, self.server_port))
            log.success("connect to {}:{}".format(self.server_host, self.server_port))
            self.connect_flag = Channel.connected
        except Exception as e:
            log.error("Fail to connect to {}:{}. Because: {}".format(self.server_host, self.server_port, e))
            self.connect_flag = Channel.unconnected

        return self.connect_flag

    def send(self, msg):

        if Channel.connected != self.connect_flag:
            if Channel.unconnected != self.connect_to_server():
                return

        s = msg.encode("ascii")
        slen = struct.pack("<L", len(s))

        try:
            # self.s.send(s)
            self.s.send(slen + s)
            if self.verbose: log.info("send to {}: {}".format(self.server_host, msg))
        except Exception as e:
            log.error(e)
            self.connect_flag = False
            self.connect_to_server()

    # ======================================  client method end  ========================================
