""" Trabalho de redes 2019 - ICMC
    Codigo que faz o sensor de temperatura

    Alexandre Norcia Medeiros - 10295583
    Gabriel Alfonso Nascimento Salgueiro - 10284368
    Giuliano Lourençon - 10295590
    Pedro Francisco Darela Neto - 10295624
"""

# Include de bibliotecas
from protocolo import *
import socket
import select
import errno
import time
import random

IP = "127.0.0.1"    # Endereco que representa o localhost

TEMPO_ENTRE_LEITURAS = 1

# Cria o socket do sensor utilizando os protocolos TCP/IP
# AF_INET -> IPv4, SOCK_STREAM -> TCP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORTA_G)) # Conecta ao servidor do gerenciador
client_socket.setblocking(False)

# Mensagem de conexao para o gerenciador
nome = Tipo_Componente.COMP_SENSOR_TEMPERATURA  # NOME DO SENSOR
header = "0 0 0".encode('utf-8') # '0 ' (mais significante) -> "gerenciador", neste momento o componente requisita seu ID
                                 # '0 ' -> gerenciador
                                 # 0 -> mensagem de conexao de sensor
client_socket.send(header + f"{len(str(nome.value)):<{TAMANHO_CABECALHO-5}}".encode('utf-8') + str(nome.value).encode('utf-8'))

ID = 0
while True:
    # espera confirmacao do servidor
    mensagem = recebe_mensagem(client_socket)
    if mensagem:
        ID = mensagem['ID_R']
        print(f"Mensagem recebida do servidor, meu ID é {ID}")
        break

# Conecta ao ambiente com TCP IPv4
ambiente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ambiente_socket.connect((IP, PORTA_A))
nome = Tipo_Componente.COMP_SENSOR_TEMPERATURA  # NOME DO SENSOR
header = f"{ID:<2}990".encode('utf-8') # ID -> ID atribuido pelo gerenciador
                                       # '99' -> ambiente
                                       #  0 -> mensagem de conexao de sensor
ambiente_socket.send(header + f"{len(str(nome.value)):<{TAMANHO_CABECALHO-5}}".encode('utf-8') + str(nome.value).encode('utf-8'))


while True:
    time.sleep(TEMPO_ENTRE_LEITURAS) # tempo de espera entre leituras

    print("Mandando mensagem para o ambiente")
    ambiente_socket.send(header + f"{len(str(nome.value)):<{TAMANHO_CABECALHO-5}}".encode('utf-8') + str(nome.value).encode('utf-8'))
    mensagem = recebe_mensagem(ambiente_socket)['Dados'] # temperatura

    # envia temperatura ao gerenciador
    if mensagem:
        print("Mensagem recebida, transferindo para o gerenciador")
        mensagem_header = f"{ID:<2}0 1{len(mensagem):<{TAMANHO_CABECALHO-5}}".encode("utf-8")
        client_socket.send(mensagem_header + mensagem)
