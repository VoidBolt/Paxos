# server_node1.py
import socket

s = socket.socket()
s.bind(("10.10.0.1", 5000))   # bind to node1's IP
s.listen()
print("Server listening on 10.10.0.1:5000")

conn, addr = s.accept()
print("Connection from", addr)
data = conn.recv(1024)
print("Received:", data.decode())
conn.close()

