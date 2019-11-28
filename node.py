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
    def __init__(self, ip, port, dir_to_share):
        Thread.__init__(self)
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind((ip, port))
        self._socket.listen(5)
        self._dir_to_share = dir_to_share

    def run(self):
        while True:
            conn, addr = self._socket.accept()
            print("receiver   connection ", addr)
            TransferThread(conn, self._dir_to_share).start()


class TransferThread(Thread):
    def __init__(self, con, dir_to_share):
        Thread.__init__(self)
        self._con = con
        self._dir_to_share = dir_to_share

    def run(self):
        data = self._con.recv(BUFFER_SIZE).decode()
        print(data)
        file_name = data
        files_list = get_files_list(self._dir_to_share)
        if file_name in files_list:
            file_to_open = self._dir_to_share + "/" + file_name
            file = open(file_to_open, 'rb')
            pkt = file.read(1024)
            while pkt:
                self._con.send(pkt)
                pkt = file.read(1024)
            file.close()
        self._con.close()



class Node:
    def __init__(self, dir_to_share, receiver_port):
        self._server_ip = SERVER_IP
        self._hello_port = SERVER_HELLO_PORT
        self._search_port = SERVER_SEARCH_PORT
        self._dir_to_share = dir_to_share
        self._receiver_port = receiver_port
        self._hello_thread = HelloThread(self._server_ip, self._hello_port, dir_to_share, self._receiver_port)
        self._receiver_thread = ReceiverThread('localhost', receiver_port, dir_to_share)

    def start(self):
        self._hello_thread.start()
        self._receiver_thread.start()

    def cmdline(self):
        while True:
            cmd = input("Enter your command:\n")
            if cmd == "search":
                file_name = input("\tEnter the filename:\n")
                containers = self.search(file_name)
                if containers:
                    chosen = self.show_choices(containers)
                    if chosen:
                        ip, port_str = chosen.split(":")
                        port = int(port_str)
                        file = self.get_file(ip, port, file_name)
                # file = self.get_file('localhost', 5002, "README.md")

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
        sock.send(pickle.dumps(file_name))
        with open(file_name, 'wb') as file:
            while True:
                data = sock.recv(BUFFER_SIZE)
                if not data:
                    break
                file.write(data)
        file.close()
        sock.close()
        return file

    def search(self, file_name):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((self._server_ip, self._search_port))
        except ConnectionRefusedError:
            print("can not connect, try later")
            return
        sock.send(pickle.dumps(file_name))
        data = pickle.loads(sock.recv(BUFFER_SIZE))
        sock.close()
        print(type(data), data)
        return data.get("containers")


def get_files_list(shared_dir):
    files_list = listdir(shared_dir)
    return files_list


SERVER_IP = "127.0.0.1"
SERVER_HELLO_PORT = 4000
SERVER_SEARCH_PORT = 4001
BUFFER_SIZE = 8192

port = input()
if port:
    node = Node(".", int(port))
else:
    node = Node(".", 6000)
node.start()
node.cmdline()
