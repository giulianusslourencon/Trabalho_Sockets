""" Trabalho de redes 2019 - ICMC
    Codigo que faz o atuador de irrigação do solo

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

# Cria o socket do sensor utilizando os protocolos TCP/IP
# AF_INET -> IPv4, SOCK_STREAM -> TCP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORTA_G)) # Conecta ao servidor do gerenciador
client_socket.setblocking(False)

# Mensagem de conexao para o gerenciador
tipo = Tipo_Componente.COMP_ATUADOR_RESFRIADOR  # TIPO DO ATUADOR
header = "0 0 2".encode('utf-8') # '0 ' (mais significante) -> neste momento o componente requisita seu ID
                                 # '0 ' -> gerenciador
                                 # 2 -> mensagem de conexao de atuador
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
header = f"{ID:<2}992".encode('utf-8') # ID -> ID atribuido pelo gerenciador
                                       # '99' -> ambiente
                                       #  2 -> mensagem de conexao de atuador
# manda mensagem de conexao com ID e tipo para o ambiente
ambiente_socket.send(header + f"{len(str(tipo.value)):<{TAMANHO_CABECALHO-5}}".encode('utf-8') + str(tipo.value).encode('utf-8'))

atuador_ligado = False

# loop principal do atuador
while True:
    # recebe pedido para ligar ou desligar do gerenciador
    mensagem = recebe_mensagem(client_socket)
    # avisa o ambiente seu estado {ligado, desligado}
    if mensagem:
        atuador_ligado = mensagem['Dados'].decode('utf-8')
        if atuador_ligado == str(True):
            # ID - '99': ambiente  - 3: mensagem de ativacao - tamanho da mesagem 
            mensagem_header = f"{ID:<2}993{len(mensagem['Dados'].decode('utf-8')):<{TAMANHO_CABECALHO-5}}".encode("utf-8")
            print("TO LIGADO")
        else:
            # ID - '99': ambiente  - 4: mensagem de desativacao - tamanho da mesagem 
            mensagem_header = f"{ID:<2}994{len(mensagem['Dados'].decode('utf-8')):<{TAMANHO_CABECALHO-5}}".encode("utf-8")
            print("TO DESLIGADO")
        ambiente_socket.send(mensagem_header + mensagem['Dados'])
