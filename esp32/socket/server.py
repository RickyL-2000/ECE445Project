import log
import config
import usocket as socket
import network


def listen():
    port = config.PORT  # 端口号
    buffer_size = config.BUFFER_SIZE  # socket缓存区，决定每次从硬件缓存区取多少数据
    backlog = config.BACKLOG

    # 注意：线连接到WiFi网络！
    # 如果未连接到网络，以下是连接到网络的代码
    # Wifi.connect()
    wifi = network.WLAN(network.STA_IF)
    ip = wifi.ifconfig()[0]  # 获取IP地址
    server = socket.socket()  # 创建套接字
    server.bind((ip, port))  # 绑定地址和端口号
    server.listen(backlog)  # 监听套接字, 最多允许backlog个连接
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 设置套接字
    log.info('server host at {}:{}'.format(ip, port))
    log.info('tcp waiting...')

    try:
        while True:
            log.info("accepting.....")
            conn, addr = server.accept()  # 接收连接请求，返回收发数据的套接字对象和客户端地址
            log.success("{} connected".format(addr))

            while True:
                data = conn.recv(buffer_size).decode("utf-8")  # 接收数据（1024字节大小）
                if (len(data) == 0):  # 判断客户端是否断开连接
                    log.warning("close socket")
                    conn.close()  # 关闭套接字
                    break
                if data == 'server quit':
                    conn.send("byebye~")
                    server.close()
                    log.warning("server quit")
                    return
                ret = conn.send(data.upper())  # 发送数据
    except Exception as e:
        log.error(e)
        server.close()
        log.error("server quit abnormally!")
        return


if __name__ == "__main__":
    listen()
