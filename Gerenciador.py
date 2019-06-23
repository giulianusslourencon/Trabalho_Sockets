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

########## Variaveis de controle ##########
IP = "127.0.0.1"    # Endereco que representa o localhost
PORTA = PORTA_G     # Porta escolhida para usar no trabalho

ultima_temperatura = 25
ultimo_nivelCO2 = 0.3
ultima_umidade = 0.3

min_temperatura, max_temperatura = 20, 40
min_nivelCO2, max_nivelCO2 = 0.2, 0.4
min_umidade, max_umidade = 0.25, 0.5

########## FUNCOES ##########
def thread_sensor(socket_sensor):
    """ Funcao que ficara em thread tratando as mensagens de um sensor """
    # define escopo de variaveis globais
    global ultima_temperatura
    global ultimo_nivelCO2 
    global ultima_umidade

    componente_sensor = componentes[socket_sensor]
    while True:
        mensagem = recebe_mensagem(socket_sensor)
        if mensagem is False:
            break
        
        # verifica tipo do sensor e guarda informacao relacionada
        if Tipo_Componente(int(componente_sensor['Dados'].decode('utf-8'))) == Tipo_Componente.COMP_SENSOR_TEMPERATURA:
            ultima_temperatura = float(mensagem['Dados'].decode('utf-8'))
        elif Tipo_Componente(int(componente_sensor['Dados'].decode('utf-8'))) == Tipo_Componente.COMP_SENSOR_UMIDADE_SOLO:
            ultima_umidade = float(mensagem['Dados'].decode('utf-8'))
        elif Tipo_Componente(int(componente_sensor['Dados'].decode('utf-8'))) == Tipo_Componente.COMP_SENSOR_NIVEL_CO2:
            ultimo_nivelCO2 = float(mensagem['Dados'].decode('utf-8'))
    
        print(f"Mensagem recebida de {Tipo_Componente(int(componente_sensor['Dados'].decode('utf-8')))} ({componente_sensor['ID_E'].strip()}): {mensagem['Dados'].decode('utf-8')}")
    
    # caso de fim de conexao
    print(f"Conexao encerrada de {Tipo_Componente(int(componente_sensor['Dados'].decode('utf-8')))} ({componente_sensor['ID_E'].strip()})")
    sockets_conectados.remove(socket_sensor)
    del componentes[socket_sensor]
    socket_sensor.close()


def thread_atuador(socket_atuador):
    """ Funcao que ficara em thread tratando as mensagens de um atuador """
    # define escopo de variaveis globais
    global ultima_temperatura
    global ultimo_nivelCO2 
    global ultima_umidade

    # variavel local da thread que indica se o atuador referente esta ativado
    ativado = False

    componente_atuador = componentes[socket_atuador]
    while True:
        histerese_temperatura = (max_temperatura-min_temperatura) / 2 # valor de folga entre desativacao dos atuadores de temperatura
        # verifica tipo do atuador e guarda informacao relacionada
        # Aquecedor
        if Tipo_Componente(int(componente_atuador['Dados'].decode('utf-8'))) == Tipo_Componente.COMP_ATUADOR_AQUECEDOR:
            # ativa aquecedor caso a temperatura atual esteja abaixo da ideal
            if float(ultima_temperatura) < min_temperatura and ativado == False:
                print(f"Aquecedor ({componente_atuador['ID_E']}) ativado.")
                tamanho = len(str(True))
                mensagem = f"0 {componente_atuador['ID_E']}4{tamanho:<3}{str(True)}"
                # verifica se existe o socket
                try:
                    socket_atuador.send(mensagem.encode('utf-8'))
                    ativado = True
                except:
                    break

            # desativa aquecedor caso a temperatura atinga o nivel ideal
            elif float(ultima_temperatura) > (min_temperatura + histerese_temperatura) and ativado == True:
                print(f"Aquecedor ({componente_atuador['ID_E']}) desativado.")
                tamanho = len(str(False))
                mensagem = f"0 {componente_atuador['ID_E']}4{tamanho:<3}{str(False)}"
                # verifica se existe o socket
                try:
                    socket_atuador.send(mensagem.encode('utf-8'))
                    ativado = False 
                except:
                    break
        
        # Resfriador        
        elif Tipo_Componente(int(componente_atuador['Dados'].decode('utf-8'))) == Tipo_Componente.COMP_ATUADOR_RESFRIADOR:
            # ativa resfriador caso a temperatura atual esteja acima da ideal
            if float(ultima_temperatura) > max_temperatura and ativado == False:
                print(f"Resfriador ({componente_atuador['ID_E']}) ativado.")
                tamanho = len(str(True))
                mensagem = f"0 {componente_atuador['ID_E']}4{tamanho:<3}{str(True)}"
                # verifica se existe o socket
                try:
                    socket_atuador.send(mensagem.encode('utf-8'))
                    ativado = True 
                except:
                    break

            # desativa resfriador caso a temperatura atinga o nivel ideal
            elif float(ultima_temperatura) < (max_temperatura - histerese_temperatura) and ativado == True:
                print(f"Resfriador ({componente_atuador['ID_E']}) desativado.")
                tamanho = len(str(False))
                mensagem = f"0 {componente_atuador['ID_E']}4{tamanho:<3}{str(False)}"
                # verifica se existe o socket
                try:
                    socket_atuador.send(mensagem.encode('utf-8'))
                    ativado = False 
                except:
                    break
        
        # Irrigador
        elif Tipo_Componente(int(componente_atuador['Dados'].decode('utf-8'))) == Tipo_Componente.COMP_ATUADOR_IRRIGACAO:
            # ativa irrigador caso a umidade atual esteja abaixo da ideal
            if ultima_umidade < min_umidade and ativado == False:
                print(f"Irrigador ativado: {componente_atuador['ID_E']}")
                tamanho = len(str(True))
                mensagem = f"0 {componente_atuador['ID_E']}4{tamanho:<3}{str(True)}"
                # verifica se existe o socket
                try:
                    socket_atuador.send(mensagem.encode('utf-8'))
                    ativado = True 
                except:
                    break

            # desativa irrigador caso a umidade atinga o nivel ideal
            elif ultima_umidade > max_umidade and ativado == True:
                print(f"Irrigador desativado: {componente_atuador['ID_E']}")
                tamanho = len(str(False))
                mensagem = f"0 {componente_atuador['ID_E']}4{tamanho:<3}{str(False)}"
                # verifica se existe o socket
                try:
                    socket_atuador.send(mensagem.encode('utf-8'))
                    ativado = False 
                except:
                    break 
                
        
        # Injedor de CO2
        elif Tipo_Componente(int(componente_atuador['Dados'].decode('utf-8'))) == Tipo_Componente.COMP_ATUADOR_INJETOR_CO2:
            # ativa injetor de CO2 caso a concentracao de CO2 atual esteja abaixo da ideal
            if ultimo_nivelCO2 < min_nivelCO2 and ativado == False:
                print(f"Injetor de CO2 ativado: {componente_atuador['ID_E']}")
                tamanho = len(str(True))
                mensagem = f"0 {componente_atuador['ID_E']}4{tamanho:<3}{str(True)}"
                # verifica se existe o socket
                try:
                    socket_atuador.send(mensagem.encode('utf-8'))
                    ativado = True 
                except:
                    break 

            # desativa injetor de CO2 caso a concentracao de CO2 atinga o nivel ideal
            elif ultimo_nivelCO2 > max_nivelCO2 and ativado == True:
                print(f"Injetor de CO2 desativado: {componente_atuador['ID_E']}")
                tamanho = len(str(False))
                mensagem = f"0 {componente_atuador['ID_E']}4{tamanho:<3}{str(False)}"
                # verifica se existe o socket
                try:
                    socket_atuador.send(mensagem.encode('utf-8'))
                    ativado = False 
                except:
                    break
    
    
    # caso de fim de conexao
    print(f"Conexao encerrada de {Tipo_Componente(int(componente_atuador['Dados'].decode('utf-8')))} ({componente_atuador['ID_E'].strip()})")
    sockets_conectados.remove(socket_atuador)
    del componentes[socket_atuador]
    socket_atuador.close()

def thread_cliente(socket_cliente):
    """ funcao que define thread que lida com o cliente """
    # define escopo de variaveis globais
    global min_temperatura, max_temperatura
    global min_nivelCO2, max_nivelCO2
    global min_umidade, max_umidade

    # loop principal de execucao da thread que lida com o cliente
    while True:
        # tenta receber mensagem do cliente
        mensagem = recebe_mensagem(socket_cliente)
        if mensagem is False: # caso coneccao seja encerrada
            break        
        print(f"Mensagem recebida do cliente ({componentes[socket_cliente]['ID_E'].strip()}): {mensagem['Dados'].decode('utf-8')}")
    
        # caso onde a mensagem eh do tipo de requisicao
        if mensagem['Tipo'] == Tipo_Mensagem.MEN_REQUISICAO_DADOS:
            dado = int(mensagem['Dados'].decode('utf-8'))
            valor = 0
            if dado == 0:
                valor = ultima_temperatura
            elif dado == 1:
                valor = ultima_umidade
            elif dado == 2:
                valor = ultimo_nivelCO2

            mensagem = f"0 {componentes[socket_cliente]['ID_E']}1{len(str(valor)):<3}{str(valor)}".encode('utf-8')
            socket_cliente.send(mensagem)
            print(f"Mensagem com o valor {str(valor)} enviada para o cliente")

        # caso onde a mensagem eh do tipo de definicao de configuracoes
        elif mensagem['Tipo'] == Tipo_Mensagem.MEN_DEFINICAO_CONFIG:
            dado, min_v, max_v = mensagem['Dados'].decode('utf-8').split(" ")
            print(f"Dado = {dado}  Min = {min_v}  Max = {max_v}")
            dado = int(dado)
            if dado == 0: # define nova faixa de temperatura
                min_temperatura, max_temperatura = float(min_v), float(max_v)
            elif dado == 1: # define nova faixa de umidade do solo
                min_umidade, max_umidade = float(min_v), float(max_v)
            elif dado == 2: # define nova faixa de concentracao de cO2
                min_nivelCO2, max_nivelCO2 = float(min_v), float(max_v)
            
            mensagem = "Parametros alterados com sucesso"
            mensagem = f"0 {componentes[socket_cliente]['ID_E']}1{len(mensagem):<3}{mensagem}".encode('utf-8')
            socket_cliente.send(mensagem)
            print(mensagem)

    # caso de fim de conexao
    print(f"Conexao encerrada com o cliente ({componentes[socket_cliente]['ID_E'].strip()})")
    sockets_conectados.remove(socket_cliente)
    del componentes[socket_cliente]
    socket_cliente.close()


# Mapa para os diferentes tipos de componentes ligando as funcoes de thread correspondentes
tipo_thread = { Tipo_Componente.COMP_SENSOR_TEMPERATURA:    thread_sensor,
                Tipo_Componente.COMP_SENSOR_NIVEL_CO2:      thread_sensor,
                Tipo_Componente.COMP_SENSOR_UMIDADE_SOLO:   thread_sensor,
                Tipo_Componente.COMP_ATUADOR_AQUECEDOR:   thread_atuador,
                Tipo_Componente.COMP_ATUADOR_RESFRIADOR:   thread_atuador,
                Tipo_Componente.COMP_ATUADOR_IRRIGACAO:   thread_atuador,
                Tipo_Componente.COMP_ATUADOR_INJETOR_CO2:   thread_atuador,
                Tipo_Componente.COMP_CLIENTE:   thread_cliente
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