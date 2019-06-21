import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect((socket.gethostname(), 9999))

full_msg = ''
while True:
    msg = server.recv(8)
    if len(msg) <= 0:
        break
    full_msg += msg.decode("utf-8")
print(full_msg)