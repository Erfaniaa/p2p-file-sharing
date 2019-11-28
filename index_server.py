import socket
import threading
import datetime
import pickle
import time


class IndexServer:

    def __init__(self):
        self.registration_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.get_hostname_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.registration_socket.bind(('localhost', 4000))
        self.get_hostname_socket.bind(('localhost', 4001))
        self.get_hostname_socket.listen(5)
        self.hostname_to_last_message_time = {}
        self.filename_to_hostname = {}
        self.connected_nodes = {}

    def start(self):
        threading.Thread(target=self._handle_registration_socket()).start()
        threading.Thread(target=self._update_connected_nodes()).start()
        threading.Thread(target=self._handle_get_hostname_socket()).start()

    def _handle_get_hostname_socket_connection(self, connection, address):
        while True:
            message = connection.recv(16)
            if not message:
                break
            message = str(message)
            if len(message) == 0:
                break
            connection.sendall(pickle.dumps({"containers": self.filename_to_hostname.get(message, [])}))
        connection.close()

    def _handle_get_hostname_socket(self):
        while True:
            connection, address = self.accept()
            threading.Thread(target=self._handle_get_hostname_socket_connection(), args=(connection, address)).start()

    def _handle_registration_socket(self):
        while True:
            data, address = self.registration_socket.recvfrom(4096)
            ip_port = address[0]+":"+str(address[1])
            if not data:
                break
            self.hostname_to_last_message_time[ip_port] = datetime.datetime.now()
            self.connected_nodes[ip_port] = True
            received = pickle.loads(data)
            for filename in received["files"]:
                self.filename_to_hostname[filename] = (*address, received["port"])
        self.registration_socket.close()

    def _check_disconnect(self):
        while True:
            now = datetime.datetime.now()
            keys = self.hostname_to_last_message_time.keys()
            for key in keys:
                if now - datetime.timedelta(seconds=90) < self.hostname_to_last_message_time[key]:
                    del self.connected_nodes[key]
                    del self.hostname_to_last_message_time[key]
            time.sleep(1)

index_server = IndexServer()
index_server.start()
