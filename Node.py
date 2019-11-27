import datetime
import socket
import time
from threading import Thread


class HelloThread(Thread):
    hello_time = 30

    def __init__(self, ip, port):
        Thread.__init__(self)
        self._ip = ip
        self._port = port
        self.exit = False

    def run(self):
        while True:
            msg_list = ["random/file", "file1", "file2"]
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind(self._ip, self._port)
            sock.sendto(bytes(msg_list))
            print(datetime.datetime.now())
            time.sleep(secs=HelloThread.hello_time)
            print(datetime.datetime.now())
            if self.exit:
                break


class Node:
    def __init__(self):
        self._server_ip = SERVER_IP
        self._hello_port = SERVER_HELLO_PORT
        self._hello_thread = HelloThread(self._server_ip, self._hello_port)

    def start(self):
        # self._hello_thread.start()
        pass

    def cmdline(self):
        while True:
            cmd = input("Enter your command:\n")

            if cmd == "search":
                print("search")
                # TODO search
            elif cmd == "exit":
                self._hello_thread.exit = True
                break
            else:
                print("Not a valid cmd")


SERVER_IP = "127.0.0.1"
SERVER_HELLO_PORT = 4000


node = Node()
node.start()
node.cmdline()
