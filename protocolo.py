""" Trabalho de redes 2019 - ICMC
    Codigo que define o codigo de identificacao de mensagens e componentes
    do protocolo

    Alexandre Norcia Medeiros - 10295583
    Gabriel Alfonso Nascimento Salgueiro - 10284368
    Giuliano Lourençon - 10295590
    Pedro Francisco Darela Neto - 10295624
"""

from enum import Enum

# Definicao das portas dos servidores
PORTA_G = 9999        # Porta escolhida para o gerenciador
PORTA_A = 9998        # Porta escolhida para o ambiente
# Definicao do cabecalho
TAMANHO_CABECALHO = 8   # O cabecalho da mensagem sera do tipo:
                        # bytes 0 e 1 -> ID do emissor (0 a 99)
                        # byte 2 e 3 -> ID do receptor (0 a 99)
                        # byte 4 -> Tipo da mensagem
                        # bytes 5, 6 e 7 -> Tamanho da mensagem, ocupando 3 caracteres (de 0 ate 999)

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
    COMP_SENSOR_TEMPERATURA = 0   # tipo para mensagem de conexao do sensor de temperatura
    COMP_SENSOR_UMIDADE_SOLO = 1  # tipo para mensagem de conexao sensor de umidade
    COMP_SENSOR_NIVEL_CO2 = 2     # tipo para mensagem de conexao co2
    COMP_ATUADOR_AQUECEDOR = 3    # tipo para mensagem de conexao aquecedor
    COMP_ATUADOR_RESFRIADOR = 4   # tipo para mensagem de conexao resfriador
    COMP_ATUADOR_IRRIGACAO = 5    # tipo para mensagem de conexao irrigacao
    COMP_ATUADOR_INJETOR_CO2 = 6  # tipo para mensagem de conexao injetor
    COMP_CLIENTE = 7              # tipo para mensagem de conexao cliente
    COMP_GERENCIADOR = 8          # tipo para mensagem de conexao gerenciador
    COMP_AMBIENTE = 9             # tipo para mensagem de conexao ambiente


###### Funcoes padroes do protocolo ######
def recebe_mensagem(socket):
    """ Funcao que verifica se um socket enviou alguma mensagem e, caso positivo,
        retorna um dicionario com os dados da mensagem
    """
    try:
        # Tenta ler o cabecalho da mensagem
        cabecalho_mensagem = socket.recv(TAMANHO_CABECALHO)
        if not len(cabecalho_mensagem): # cabecalho vazio
            return False

        # Ao conseguir, o separa em seus campos (ID Emissor, ID Receptor, tipo da mensagem e tamanho da mensagem)
        cabecalho_mensagem = cabecalho_mensagem.decode("utf-8").strip() # tira espacos vazios do cabecalho
        id_emissor = cabecalho_mensagem[0:2]
        id_receptor = cabecalho_mensagem[2:4]
        tipo_mensagem = Tipo_Mensagem(int(cabecalho_mensagem[4]))
        tamanho_mensagem = int(cabecalho_mensagem[5:])

        # E, em seguida, retorna um dicionario com as informacoes do cabecalho e os dados da mensagem 
        return {"ID_E": id_emissor, "ID_R": id_receptor, "Tipo": tipo_mensagem, "Dados": socket.recv(tamanho_mensagem)}

    except:
        return False # Caso haja algum empedimento
