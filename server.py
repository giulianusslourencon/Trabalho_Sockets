import socket

HEADERSIZE = 10

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((socket.gethostname(), 9999))
s.listen(5)

while True:
    clientSocket, address = s.accept()
    print(f"Conexão recebida por {address}")

    msg = "Aehoooo ta conectado agr irmao, sua alma eh minha heuheue"
    msg = f'{len(msg):<{HEADERSIZE}}' + msg

    clientSocket.send(bytes(msg, "utf-8"))
