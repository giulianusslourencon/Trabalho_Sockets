""" Trabalho de redes 2019 - ICMC
    Codigo que faz o sensor d.....................

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

TAMANHO_CABECALHO = 6   # O cabecalho da mensagem sera do tipo:
                        # byte 0 -> ID do emissor
                        # byte 1 -> ID do receptor
                        # byte 2 -> Tipo da mensagem
                        # bytes 3, 4 e 5 -> Tamanho da mensagem, ocupando 3 caracteres (de 0 ate 999)
                        
IP = "127.0.0.1"    # Endereco que representa o localhost
PORTA_G = 9999        # Porta escolhida para o gerenciador
PORTA_A = 9998        # Porta escolhida para o ambiente

# Cria o socket do sensor utilizando os protocolos TCP/IP
# AF_INET -> IPv4, SOCK_STREAM -> TCP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORTA_G)) # Conecta ao servidor do gerenciador
client_socket.setblocking(False)

# Mensagem de conexao para o gerenciador
nome = "Sensor de Temperatura".encode("utf-8")  # NOME DO SENSOR
header = "08022 ".encode('utf-8') # 0 (mais significante) -> temperatura
                                  # 8 -> gerenciador
                                  # 0 -> mensagem de conexao de sensor
                                  # '22 ' (menos significante) -> tamanho da mensagem
client_socket.send(header + nome)

while True:
    mensagem = input("Temperatura lida (digite): ") # temperatura
    
    if mensagem:
        mensagem = mensagem.encode("utf-8") # codifica para utf-8
        mensagem_header = f"080{len(mensagem):<{TAMANHO_CABECALHO-3}}".encode("utf-8")
        client_socket.send(mensagem_header + mensagem)

    """
    try:
        # recebe temperatura do ambiente
        while True:
            username_header = client_socket.recv(TAMANHO_CABECALHO)
            if not len(username_header):
                print("Conexao encerrada pelo servidor")
                sys.exit()
            username_length = int(username_header.decode("utf-8").strip())
            username = client_socket.recv(username_length).decode("utf-8")

            mensagem_header = client_socket.recv(TAMANHO_CABECALHO)
            mensagem_length = int(mensagem_header.decode("utf-8").strip())
            mensagem = client_socket.recv(mensagem_length).decode("utf-8")

            print(f"{username} > {mensagem}")

    except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Erro de leitura', str(e))
        continue

    except Exception as e:
        print('Erro', str(e))
        sys.exit()
    """