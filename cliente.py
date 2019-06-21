import socket

host = "127.0.0.1"
porta = 9999

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

cliente.connect((host, porta))



#cliente.send

resposta = cliente.recv(4896)

print(resposta)