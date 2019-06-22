""" Trabalho de redes 2019 - ICMC
    Codigo que faz o servidor do 'gerenciador' da estufa inteligente

    Alexandre Norcia Medeiros - 10295583
    Gabriel Alfonso Nascimento Salgueiro - 10284368
    Giuliano Lourençon - 10295590
    Dedro "Pedro" Alexandre Parela Neto dos san- 21
"""
# Include de bibliotecas
import socket
import select
from enum import Enum


# Definicao dos tipos de mensagem
class Tipo_Mensagem(Enum):
    """ Enum para definir o tipo da mensagem """
    MEN_CONEXAO_SENSORES = 0
    MEN_DADOS = 1
    MEN_CONEXAO_ATUADORES = 2
    MEN_ATIVACAO_ATUADORES = 3
    MEN_DESATIVACAO_ATUADORES = 4
    MEN_REQUISICAO_DADOS = 5
    MEN_CONEXAO_CLIENTE = 6
    MEN_DEFINICAO_CONFIG = 7

class Tipo_Componente(Enum):
    COMP_SENSOR_TEMPERATURA = 0
    COMP_SENSOR_UMIDADE_SOLO = 1
    COMP_SENSOR_NIVEL_CO2 = 2
    COMP_ATUADOR_AQUECEDOR = 3
    COMP_ATUADOR_RESFRIADOR = 4
    COMP_ATUADOR_IRRIGACAO = 5
    COMP_ATUADOR_INJETOR_CO2 = 6
    COMP_CLIENTE = 7


########## CONSTANTES ##########


TAMANHO_CABECALHO = 6   # O cabecalho da mensagem sera do tipo:
                        # byte 0 -> ID do emissor
                        # byte 1 -> ID do receptor
                        # byte 2 -> Tipo da mensagem
                        # bytes 3, 4 e 5 -> Tamanho da mensagem, ocupando 3 caracteres (de 0 ate 999)

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
        id_emissor = cabecalho_mensagem[0]
        id_receptor = cabecalho_mensagem[1]
        tipo_mensagem = Tipo_Mensagem(int(cabecalho_mensagem[2]))
        tamanho_mensagem = int(cabecalho_mensagem[3:])
        return {"ID_E": id_emissor, "ID_R": id_receptor, "Tipo": tipo_mensagem, "Dados": socket_cliente.recv(tamanho_mensagem)}

    except:
        return False


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
        # intera sobre os sockets que nao sao o servidor (novas mensagens dos clientes)
        else:
            mensagem = recebe_mensagem(socket_modificado)
            if mensagem is False: # mensagem vazia ou com erro
                print(f"Conexao encerrada de {Tipo_Componente(int(componentes[socket_modificado]['Dados'].decode('utf-8')))}:{componentes[socket_modificado]['ID_E'].decode('utf-8')}")
                sockets_conectados.remove(socket_modificado)
                del componentes[socket_modificado]
                continue
            
            # exibe nova mensagem
            componente = componentes[socket_modificado]
            print(f"Mensagem recebida de {Tipo_Componente(int(componentes[socket_modificado]['Dados'].decode('utf-8')))} ({componentes[socket_modificado]['ID_E'].decode('utf-8')}): {Tipo_Mensagem(int(mensagem['Tipo'].decode('utf-8')))}")
            #####
            #     TRATAMENTO DE MENSAGENS VEM AQUI
            #####

    # remove clientes que encerraram conexao    
    for socket_modificado in sockets_excecao:
        sockets_conectados.remove(socket_modificado)
        del componentes[socket_modificado]