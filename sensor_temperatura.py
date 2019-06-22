""" Trabalho de redes 2019 - ICMC
    Codigo que faz o sensor de temperatura

    Alexandre Norcia Medeiros - 10295583
    Gabriel Alfonso Nascimento Salgueiro - 10284368
    Giuliano Lourençon - 10295590
    P3dr0 Francisco Darela Neto - 10295624
"""

# Include de bibliotecas
import socket
import select
import errno
from enum import Enum
import time
import random

# Definicao dos tipos de mensagem
class Tipo_Mensagem(Enum):
    """ Enum para definir o tipo da mensagem """
    MEN_CONEXAO_SENSORES = 0      # sensor estabele conexao
    MEN_DADOS = 1                 # sensor envia dados
    MEN_CONEXAO_ATUADORES = 2     # atuador estabelece conexao
    MEN_ATIVACAO_ATUADORES = 3    # gerenciador ativa atuador
    MEN_DESATIVACAO_ATUADORES = 4 # gerenciador desativa atuador
    MEN_REQUISICAO_DADOS = 5      # cliente requisita os dados
    MEN_CONEXAO_CLIENTE = 6       # cliente estabelece conexao
    MEN_DEFINICAO_CONFIG = 7      # cliente define configuracao

class Tipo_Componente(Enum):
    """ Enum para definir o tipo de componente """
    COMP_SENSOR_TEMPERATURA = 0   # id do sensor de temperatura
    COMP_SENSOR_UMIDADE_SOLO = 1  # id sensor de umidade
    COMP_SENSOR_NIVEL_CO2 = 2     # id co2
    COMP_ATUADOR_AQUECEDOR = 3    # id aquecedor
    COMP_ATUADOR_RESFRIADOR = 4   # id resfriador
    COMP_ATUADOR_IRRIGACAO = 5    # id irrigacao
    COMP_ATUADOR_INJETOR_CO2 = 6  # id injetor
    COMP_CLIENTE = 7              # id cliente
    COMP_GERENCIADOR = 8          # id gerenciador
    COMP_AMBIENTE = 9             # id ambiente


def recebe_mensagem(socket_servidor):
    """ Funcao que verifica se um socket enviou alguma mensagem e, caso positivo,
        retorna um dicionario com os dados da mensagem
    """
    try:
        cabecalho_mensagem = socket_servidor.recv(TAMANHO_CABECALHO)
        if not len(cabecalho_mensagem): # cabecalho vazio
            return False

        cabecalho_mensagem = cabecalho_mensagem.decode("utf-8").strip() # tira espacos vazios do cabecalho
        id_emissor = cabecalho_mensagem[0:2]
        id_receptor = cabecalho_mensagem[2:4]
        tipo_mensagem = Tipo_Mensagem(int(cabecalho_mensagem[4]))
        tamanho_mensagem = int(cabecalho_mensagem[5:])
        return {"ID_E": id_emissor, "ID_R": id_receptor, "Tipo": tipo_mensagem, "Dados": socket_servidor.recv(tamanho_mensagem)}

    except:
        return False



TAMANHO_CABECALHO = 8   # O cabecalho da mensagem sera do tipo:
                        # bytes 0 e 1 -> ID do emissor
                        # byte 2 e 3 -> ID do receptor
                        # byte 4 -> Tipo da mensagem
                        # bytes 5, 6 e 7 -> Tamanho da mensagem, ocupando 3 caracteres (de 0 ate 999)
                        
IP = "127.0.0.1"    # Endereco que representa o localhost
PORTA_G = 9999        # Porta escolhida para o gerenciador
PORTA_A = 9998        # Porta escolhida para o ambiente

# Cria o socket do sensor utilizando os protocolos TCP/IP
# AF_INET -> IPv4, SOCK_STREAM -> TCP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORTA_G)) # Conecta ao servidor do gerenciador
client_socket.setblocking(False)

# Mensagem de conexao para o gerenciador
nome = Tipo_Componente.COMP_SENSOR_TEMPERATURA  # NOME DO SENSOR
header = "0 0 0".encode('utf-8')  # 0 (mais significante) -> "gerenciador", neste momento o componente requisita seu ID
                                # 0 -> gerenciador
                                # 0 -> mensagem de conexao de sensor
client_socket.send(header + f"{len(str(nome.value)):<{TAMANHO_CABECALHO-5}}".encode('utf-8') + str(nome.value).encode('utf-8'))

ID = 0
while True:
    mensagem = recebe_mensagem(client_socket)
    if mensagem:
        ID = mensagem['ID_R']
        print(f"Mensagem recebida do servidor, meu ID é {ID}")
        break

while True:
    time.sleep(1)
    mensagem = random.randint(10, 40) # temperatura
    
    if mensagem:
        mensagem = (f"Temperatura atual: {mensagem}ºC").encode("utf-8") # codifica para utf-8
        mensagem_header = f"{ID:<2}0 1{len(mensagem):<{TAMANHO_CABECALHO-5}}".encode("utf-8")
        client_socket.send(mensagem_header + mensagem)
