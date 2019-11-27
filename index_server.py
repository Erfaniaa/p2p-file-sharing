import socket
import threading


class IndexServer:

    def __init__(self):
        self.registration_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.get_hostname_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.registration_socket.bind(('localhost', 4000))
        self.get_hostname_socket.bind(('localhost', 4001))
        self.filename_to_hostname = {}

    def start(self):
        threading.Thread(target=self._listen_on_registration_socket()).start()
        # threading.Thread(target=self._listen_on_get_hostname_socket()).start()

    def _listen_on_registration_socket(self):
        while True:
            data, address = self.registration_socket.recvfrom(4096)
            if not data:
                break
            filenames = list(data)
            for filename in filenames:
                self.filename_to_hostname[filename] = address
            # self.registration_socket.send("Received.".encode())
        self.registration_socket.close()

index_server = IndexServer()
index_server.start()
