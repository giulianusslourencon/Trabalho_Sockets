""" Trabalho de redes 2019 - ICMC
    Codigo que faz o servidor do 'gerenciador' da estufa inteligente

    Alexandre Norcia Medeiros - 10295583
    Gabriel Alfonso Nascimento Salgueiro - 10284368
    Giuliano Lourençon - 10295590
    Pedro Francisco Darela Neto - 10295624
"""
# Include de bibliotecas
from protocolo import *
import socket
import select
from _thread import start_new_thread

IP = "127.0.0.1"    # Endereco que representa o localhost
PORTA = PORTA_G     # Porta escolhida para usar no trabalho

########## FUNCOES ##########

def thread_sensor(socket_sensor):
    """ Funcao que ficara em thread tratando as mensagens de um sensor """    
    while True:
        mensagem = recebe_mensagem(socket_sensor)
        if mensagem is False:
            break
        componente_sensor = componentes[socket_sensor]
        print(f"Mensagem recebida de {Tipo_Componente(int(componente_sensor['Dados'].decode('utf-8')))} ({componente_sensor['ID_E'].strip()}): {mensagem['Dados'].decode('utf-8')}")
    
    print(f"Conexao encerrada de {Tipo_Componente(int(componente_sensor['Dados'].decode('utf-8')))} ({componente_sensor['ID_E'].strip()})")
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
socket_servidor.listen(10) # conecta com ate 10 processos

# Lista com todos os sockets conectados ao servidor
sockets_conectados = [socket_servidor]

# Dicionario com os componentes conectados ao servidor
componentes = {}
ultimo_ID = 0

while True:
    # seleciona sockets modificados, sockets para escrita (nao usaremos), sockets com execoes
    try:
        sockets_modificados, _, sockets_excecao = select.select(sockets_conectados, [], sockets_conectados)
    except OSError as e:
        print("Erro: ", str(e))
        continue

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

            ultimo_ID += 1 # calcula novo id para o componente
            socket_cliente.send(f"0 {ultimo_ID:<2}00  ".encode('utf-8')) # mensagem de confirmacao
            componentes[socket_cliente]['ID_E'] = f"{ultimo_ID:<2}"
            
            # cria uma nova thread para tratar a comunicacao com o componente de acordo com o tipo dele
            start_new_thread(tipo_thread[Tipo_Componente(int(componente['Dados'].decode('utf-8')))], (socket_cliente,))
        
    # trata clientes com erro de execucao removendo sua coneccao   
    for socket_modificado in sockets_excecao:
        print(f"ERRO!!\nConexao encerrada de {Tipo_Componente(int(componentes[socket_modificado]['Dados'].decode('utf-8')))}:{componentes[socket_modificado]['ID_E'].strip()}")
        sockets_conectados.remove(socket_modificado)
        del componentes[socket_modificado]