import socket
import threading

def cliente(cliente_socket):
    resposta = cliente_socket.recv(1024)
    print ("Resposta = %s", resposta)

    cliente_socket.send("TA CHOVENDO AI??")
    cliente_socket.close()

##################################################################

ip = "0.0.0.0"
porta = 9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((ip, porta))
server.listen(9)

print ("Ouvindo em %s:%d", ip, porta)

while True:
    client, addr = server.accept()
    print ("Conexão recebida por %s:%d", addr[0], addr[1])

    cliente = threading.Thread(target=cliente, args=(client,))
    cliente.start()
