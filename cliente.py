from protocolo import *
import socket
import select
import errno
import sys

########## CONSTANTS ##########
IP = "127.0.0.1"
PORTA = PORTA_G

# Cria o socket do sensor utilizando os protocolos TCP/IP
# AF_INET -> IPv4, SOCK_STREAM -> TCP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORTA_G)) # Conecta ao servidor do gerenciador
client_socket.setblocking(False)

# Mensagem de conexao para o gerenciador
tipo = Tipo_Componente.COMP_CLIENTE  # TIPO DO SENSOR
header = "0 0 0".encode('utf-8') # '0 ' (mais significante) -> neste momento o componente requisita seu ID
                                 # '0 ' -> gerenciador
                                 # 0 -> mensagem de conexao de sensor
# manda mensagem para o gerenciador
client_socket.send(header + f"{len(str(tipo.value)):<{TAMANHO_CABECALHO-5}}".encode('utf-8') + str(tipo.value).encode('utf-8'))

ID = 0
while True:
    # espera confirmacao do servidor do gerenciador
    mensagem = recebe_mensagem(client_socket)
    if mensagem:
        # recebe seu novo id
        ID = mensagem['ID_R']
        print(f"Mensagem recebida do servidor, meu ID é {ID}")
        break

while True:
    message = input("Tipo do pedido:\n 0 - Requisição de dados\n")

    if message:
        if int(message) == 0:
            message = input("\n  0 - Temperatura\n  1 - Nível de CO2\n  2 - Umidade do solo\n")
            if message:
                message = f"{ID:<2}0 5{len(message):<3}{message}".encode("utf-8")
                client_socket.send(message)
                print("Enviou")

    try:
        while True:
            resposta = recebe_mensagem(client_socket)
            if resposta is False:
                continue
            print(f"Mensagem recebida do servidor:\n  {resposta['Dados'].decode('utf-8')}")
            break

    except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Erro de leitura', str(e))
        continue

    except Exception as e:
        print('Erro', str(e))
        sys.exit()