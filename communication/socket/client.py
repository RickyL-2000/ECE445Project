import config
import usocket as socket
import log

msgs = {"1": "abc", "2": "123456789", "3": "qwertyuiopasdfghjklzxcvbnm"}


def listen():
    host = config.PC_IP
    port = config.PORT
    buffer_size = config.BUFFER_SIZE

    s = socket.socket()
    log.info("try to connect to {}:{}".format(host, port))
    s.connect((host, port))
    log.success("success")

    try:
        while True:
            msg = input("send to \t{}:\t".format(host)).strip()
            if msg in msgs:
                msg = msgs[msg]
            if not msg:
                continue
            if msg == "quit":
                break
            s.sendall(msg.encode("utf-8"))
            data = s.recv(buffer_size)
            log.info("receive from \t{}:\t".format(
                host) + data.decode("utf-8"))
    except:
        pass
    finally:
        s.close()


if __name__ == '__main__':
    listen()
