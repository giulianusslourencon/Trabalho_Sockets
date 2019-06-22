""" Trabalho de redes 2019 - ICMC
    Codigo que faz o servidor do 'gerenciador' da estufa inteligente

    Alexandre Norcia Medeiros - 10295583
    Gabriel Alfonso Nascimento Salgueiro - 10284368
    Giuliano Lourençon - 10295590
    P3dr0 Francisco Darela Neto - 10295624
"""
# Include de bibliotecas
import socket
import select
from enum import Enum
from _thread import *


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


########## CONSTANTES ##########


TAMANHO_CABECALHO = 8   # O cabecalho da mensagem sera do tipo:
                        # bytes 0 e 1 -> ID do emissor
                        # byte 2 e 3 -> ID do receptor
                        # byte 4 -> Tipo da mensagem
                        # bytes 5, 6 e 7 -> Tamanho da mensagem, ocupando 3 caracteres (de 0 ate 999)

IP = "127.0.0.1"    # Endereco que representa o localhost
PORTA = 9999        # Porta escolhida para usar no trabalho


########## FUNCOES ##########


def recebe_mensagem(socket_cliente):
    """ Funcao que verifica se um socket enviou alguma mensagem e, caso positivo,
        retorna um dicionario com os dados da mensagem
    """
    try:
        cabecalho_mensagem = socket_cliente.recv(TAMANHO_CABECALHO)
        if not len(cabecalho_mensagem): # cabecalho vazio
            return False

        cabecalho_mensagem = cabecalho_mensagem.decode("utf-8").strip() # tira espacos vazios do cabecalho
        id_emissor = cabecalho_mensagem[0:2]
        id_receptor = cabecalho_mensagem[2:4]
        tipo_mensagem = Tipo_Mensagem(int(cabecalho_mensagem[4]))
        tamanho_mensagem = int(cabecalho_mensagem[5:])
        return {"ID_E": id_emissor, "ID_R": id_receptor, "Tipo": tipo_mensagem, "Dados": socket_cliente.recv(tamanho_mensagem)}

    except:
        return False



def thread_sensor(socket_sensor):
    """ Funcao que ficara em thread tratando as mensagens de um sensor
    """
    while True:
        mensagem = recebe_mensagem(socket_sensor)
        if mensagem is False:
            break
        componente_sensor = componentes[socket_sensor]
        print(f"Mensagem recebida de {Tipo_Componente(int(componente_sensor['Dados'].decode('utf-8')))} ({componente_sensor['ID_E'].strip()}):\n\t{mensagem['Dados'].decode('utf-8')} ")
    
    print(f"Conexao encerrada de {Tipo_Componente(int(componente_sensor['Dados'].decode('utf-8')))}:{componente_sensor['ID_E'].strip()}")
    sockets_conectados.remove(socket_sensor)
    del componentes[socket_sensor]
    socket_sensor.close()


# Mapa para os diferentes tipos de componentes ligando as funcoes de thread correspondentes
tipo_thread = { Tipo_Componente.COMP_SENSOR_TEMPERATURA:    thread_sensor,
                Tipo_Componente.COMP_SENSOR_NIVEL_CO2:      thread_sensor,
                Tipo_Componente.COMP_SENSOR_UMIDADE_SOLO:   thread_sensor,
}


########## CODIGO PRINCIPAL ##########


# Cria o socket do servidor utilizando os protocolos TCP/IP
# AF_INET -> IPv4, SOCK_STREAM -> TCP
socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Vincula o socket do servidor ao IP e a porta definidos
socket_servidor.bind((IP, PORTA))
socket_servidor.listen()

# Lista com todos os sockets conectados ao servidor
sockets_conectados = [socket_servidor]

# Dicionario com os componentes conectados ao servidor
componentes = {}
ultimo_ID = 0

while True:
    # seleciona sockets modificados, sockets para escrita (nao usaremos), sockets com execoes
    sockets_modificados, _, sockets_excecao = select.select(sockets_conectados, [], sockets_conectados)

    for socket_modificado in sockets_modificados:
        # socket modificado eh o servidor (alguem quer se conectar)
        if socket_modificado == socket_servidor:
            # aceita nova conexao
            socket_cliente, endereco_cliente = socket_servidor.accept()
            
            componente = recebe_mensagem(socket_cliente) # mensagem de conexao
            if componente is False: # mensagem vazia ou com erro
                continue

            # adiciona novo cliente
            sockets_conectados.append(socket_cliente)
            componentes[socket_cliente] = componente
            # exibe conexao estabelecida
            print(f"Conexao estabelecida de {endereco_cliente[0]}:{endereco_cliente[1]} tipo:{Tipo_Componente(int(componente['Dados'].decode('utf-8')))}")

            ultimo_ID += 1
            socket_cliente.send(f"0 {ultimo_ID:<2}00  ".encode('utf-8'))
            componentes[socket_cliente]['ID_E'] = f"{ultimo_ID:<2}"
            
            start_new_thread(tipo_thread[Tipo_Componente(int(componente['Dados'].decode('utf-8')))], (socket_cliente,))
        
    # trata clientes com erro de execucao removendo sua coneccao   
    for socket_modificado in sockets_excecao:
        print(f"ERRO!!\nConexao encerrada de {Tipo_Componente(int(componentes[socket_modificado]['Dados'].decode('utf-8')))}:{componentes[socket_modificado]['ID_E'].strip()}")
        sockets_conectados.remove(socket_modificado)
        del componentes[socket_modificado]