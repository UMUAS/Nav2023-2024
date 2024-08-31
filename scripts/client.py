"""A test script for interacting with a server using UNIX domain sockets."""

import socket

# Set the path for the Unix socket.
SOCKET_PATH = "/tmp/umuas_socket"

# Create the Unix socket client.
client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

# Connect to the server.
client.connect(SOCKET_PATH)

# Send a message to the server.
message = "FT WAYPOINT"
client.send(message.encode())

# Receive a response from the server.
response = client.recv(1024)
print(f"Received response: {response.decode()}")

# Close the connection.
client.close()


# import socket
# import sys

# HOST = "127.0.0.1"
# PORT = 10001
# s = socket.socket()
# s.connect((HOST, PORT))

# while 1:
#     msg = input("Command To Send: ")
#     msg = msg.encode()
#     if msg == b"close":
#         s.close()
#         sys.exit(0)
#     s.send(msg)


# server.py

# import socket
# from threading import Thread

# MAX_LENGTH = 4096


# def handle(clientsocket):
#     while 1:
#         buf = clientsocket.recv(MAX_LENGTH)
#         if buf == "":
#             return  # client terminated connection
#         print(buf)


# serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# PORT = 10001
# HOST = "127.0.0.1"

# serversocket.bind((HOST, PORT))
# serversocket.listen(10)

# while 1:
#     # accept connections from outside
#     (clientsocket, address) = serversocket.accept()

#     ct = Thread(target=handle, args=(clientsocket,))
#     ct.start()
