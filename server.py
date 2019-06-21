import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((socket.gethostname(), 9999))
s.listen(5)

while True:
    clientSocket, address = s.accept()
    print(f"Conexão recebida por {address}")
    clientSocket.send(bytes("Aehoooo ta conectado agr irmao, sua alma eh minha heuheue", "utf-8"))
    clientSocket.close()
