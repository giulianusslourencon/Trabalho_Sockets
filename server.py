import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((socket.gethostname(), 9999))
server.listen(5)

while True:
    clientSocket, address = server.accept()
    print(f"Conexão recebida por {address}")
    clientSocket.send(bytes("Aehoooo ta conectado agr irmao, sua alma eh minha heuheue", "utf-8"))
