import socket
import threading


class IndexServer:

	def __init__(self):
		self.registration_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.get_hostname_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.registration_socket.bind(('localhost', 4000))
		self.get_hostname_socket.bind(('localhost', 4001))
		self.registration_socket.listen(10)
		self.get_hostname_socket.listen(10)
		self.filename_to_hostname = {}

	def start(self):
		threading.Thread(target=self._listen_on_registration_socket()).start()
		threading.Thread(target=self._listen_on_get_hostname_socket()).start()

	def _listen_on_registration_socket(self):
		while True:
			connection, address = self.registration_socket.accept()
			from_client = ""
			while True:
				data = connection.recv(4096)
				if not data:
					break
				filenames = list(data)
				for filename in filenames:
					self.filename_to_hostname[filename] = address
				connection.send("Received.".encode())
			connection.close()

index_server = IndexServer()
index_server.start()
