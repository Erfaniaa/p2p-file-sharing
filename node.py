import pickle
import socket
import time
from os import listdir
from threading import Thread


class HelloThread(Thread):
    hello_time = 30

    def __init__(self, ip, port, dir_to_share, receiver_port):
        Thread.__init__(self)
        self._ip = ip
        self._port = port
        self.exit = False
        self._dir_to_share = dir_to_share
        self._receiver_port = receiver_port

    def run(self):
        while True:
            file_list = get_files_list(self._dir_to_share)
            data = pickle.dumps({
                "files": file_list,
                "port": self._receiver_port
            })
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(data, (self._ip, self._port))
            time.sleep(HelloThread.hello_time)
            if self.exit:
                break


class ReceiverThread(Thread):
    def __init__(self):
        pass

    def run(self):
        while True:
            pass


class Node:
    def __init__(self, dir_to_share, receiver_port):
        self._server_ip = SERVER_IP
        self._hello_port = SERVER_HELLO_PORT
        self._search_port = SERVER_SEARCH_PORT
        self._dir_to_share = dir_to_share
        self._receiver_port = receiver_port
        self._hello_thread = HelloThread(self._server_ip, self._hello_port, dir_to_share, self._receiver_port)

    def start(self):
        self._hello_thread.start()

    def cmdline(self):
        while True:
            cmd = input("Enter your command:\n")
            if cmd == "search":
                print("search")
                file_name = input("\tEnter the filename:\n")
                containers = self.search(file_name)
                if containers:
                    chosen = self.show_choices(containers)
                    if chosen:
                        ip, port_str = chosen.split(":")
                        port = int(port_str)
                        file = self.get_file(ip, port, file_name)

            elif cmd == "exit":
                self._hello_thread.exit = True
                break
            else:
                print("Not a valid command")

    def show_choices(self, containers):
        if not containers:
            print("Sorry, no such file is available")
            return None
        print("Available containers:")
        while True:
            for i in range(len(containers)):
                print(i + 1, ".   ", containers[i])
            choice = input()
            if choice == "none":
                print("Canceled by user")
                return None
            choice_index = int(choice) - 1
            if choice_index in range(len(containers)):
                return containers[choice_index]
            print("Not a valid Choice, Please Re-enter your choice")

    def get_file(self, ip, port, file_name):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        sock.send(file_name)
        file = sock.recv(BUFFER_SIZE)
        print(file)
        return file

    def search(self, file_name):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((self._server_ip, self._search_port))
        except ConnectionRefusedError:
            print("can not connect, try later")
            return
        sock.send(file_name)
        data = pickle.load(sock.recv(BUFFER_SIZE))
        sock.close()
        print(type(data), data)
        return data.get("containers")


def get_files_list(shared_dir):
    files_list = listdir(shared_dir)
    return files_list


SERVER_IP = "127.0.0.1"
SERVER_HELLO_PORT = 4000
SERVER_SEARCH_PORT = 5000
BUFFER_SIZE = 1024

node = Node(".", 5005)
node.start()
node.cmdline()
