import socket
from threading import Thread
import datetime
import pickle
import time


class UpdateConnectedNodes(Thread):

    def __init__(self, hostname_to_last_message_time, connected_nodes):
        Thread.__init__(self)
        self.hostname_to_last_message_time = hostname_to_last_message_time
        self.connected_nodes = connected_nodes

    def run(self):
        while True:
            now = datetime.datetime.now()
            keys = list(self.hostname_to_last_message_time.keys())
            for key in keys:
                if now - datetime.timedelta(seconds=90) < self.hostname_to_last_message_time[key]:
                    if self.hostname_to_last_message_time.get(key):
                    	del self.hostname_to_last_message_time[key]
                    if self.connected_nodes.get(key):
                    	del self.connected_nodes[key]


class HandleGetHostnameSocketConnection(Thread):

    def __init__(self, filename_to_hostname, connection):
        Thread.__init__(self)
        self.filename_to_hostname = filename_to_hostname
        self.connection = connection

    def run(self):
        while True:
            message = self.connection.recv(16)
            if not message:
                break
            message = str(message)
            if len(message) == 0:
                break
            print("GetHostname")
            print(message)
            self.connection.sendall(pickle.dumps({"containers": self.filename_to_hostname.get(message, [])}))
            print(pickle.dumps({"containers": self.filename_to_hostname.get(message, [])}))
            print({"containers": self.filename_to_hostname.get(message, [])})
        self.connection.close()


class HandleGetHostnameSocket(Thread):

    def __init__(self, get_hostname_socket, filename_to_hostname):
        Thread.__init__(self)
        self.get_hostname_socket = get_hostname_socket
        self.filename_to_hostname = filename_to_hostname

    def run(self):
        while True:
            connection, address = self.get_hostname_socket.accept()
            handle_get_hostname = HandleGetHostnameSocketConnection(self.filename_to_hostname, connection)
            handle_get_hostname.start()

class HandleRegistrationSocket(Thread):

    def __init__(self, registration_socket, get_hostname_socket, hostname_to_last_message_time, filename_to_hostname, connected_nodes):
        Thread.__init__(self)
        self.registration_socket = registration_socket
        self.get_hostname_socket = get_hostname_socket
        self.hostname_to_last_message_time = hostname_to_last_message_time
        self.filename_to_hostname = filename_to_hostname
        self.connected_nodes = connected_nodes
        
    def run(self):
        while True:
            data, address = self.registration_socket.recvfrom(4096)
            if not data:
                break
            received = pickle.loads(data)
            ip_port = address[0] + ":" + received["port"]
            self.hostname_to_last_message_time[ip_port] = datetime.datetime.now()
            self.connected_nodes[ip_port] = True
            print(received)
            for filename in received["files"]:
                self.filename_to_hostname[filename] = (*address, received["port"])
        self.registration_socket.close()


class IndexServer:

    def __init__(self):
        self.registration_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.get_hostname_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.registration_socket.bind(('localhost', 5000))
        self.get_hostname_socket.bind(('localhost', 5001))
        self.get_hostname_socket.listen(5)
        self.hostname_to_last_message_time = {}
        self.filename_to_hostname = {}
        self.connected_nodes = {}

    def start(self):
        update_connected_nodes = UpdateConnectedNodes(self.hostname_to_last_message_time, self.connected_nodes)
        handle_get_hostname_socket = HandleGetHostnameSocket(self.get_hostname_socket, self.filename_to_hostname)
        handle_registration_socket = HandleRegistrationSocket(self.registration_socket, self.get_hostname_socket, self.hostname_to_last_message_time, self.filename_to_hostname, self.connected_nodes)
        update_connected_nodes.start()
        handle_get_hostname_socket.start()
        handle_registration_socket.start()


index_server = IndexServer()
index_server.start()
