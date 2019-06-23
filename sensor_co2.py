""" Trabalho de redes 2019 - ICMC
    Codigo que faz o sensor de CO2 do ambiente

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
tipo = Tipo_Componente.COMP_SENSOR_NIVEL_CO2  # TIPO DO SENSOR
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

# Conecta ao ambiente com TCP IPv4
ambiente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ambiente_socket.connect((IP, PORTA_A))
header = f"{ID:<2}990".encode('utf-8') # ID -> ID atribuido pelo gerenciador
                                       # '99' -> ambiente
                                       #  0 -> mensagem de conexao de sensor
# manda mensagem de conexao com ID e tipo para o ambiente
ambiente_socket.send(header + f"{len(str(tipo.value)):<{TAMANHO_CABECALHO-5}}".encode('utf-8') + str(tipo.value).encode('utf-8'))

# loop principal do sensor
while True:
    time.sleep(TEMPO_ENTRE_LEITURAS) # tempo de espera entre leituras
    # requisita dados para o ambiente
    ambiente_socket.send(header + f"{len(str(tipo.value)):<{TAMANHO_CABECALHO-5}}".encode('utf-8') + str(tipo.value).encode('utf-8'))
    # recebe nivel de CO2
    mensagem = recebe_mensagem(ambiente_socket) # nivel de CO2
    # envia nivel de CO2 ao gerenciador
    if mensagem:
        mensagem_header = f"{ID:<2}0 1{len(mensagem['Dados']):<{TAMANHO_CABECALHO-5}}".encode("utf-8")
        client_socket.send(mensagem_header + mensagem['Dados'])
