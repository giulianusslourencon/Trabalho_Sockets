""" Trabalho de redes 2019 - ICMC
    Codigo que faz o servidor do 'ambiente' da estufa inteligente
    ele mantem as informacoes de temperatura, co2 e umidade do ambiente atual.

    Alexandre Norcia Medeiros - 10295583
    Gabriel Alfonso Nascimento Salgueiro - 10284368
    Giuliano Lourençon - 10295590
    Pedro Francisco Darela Neto - 10295624
"""
# Include de bibliotecas
from protocolo import *
import socket
import select
import time
import random
from _thread import start_new_thread

IP = "127.0.0.1"    # Endereco que representa o localhost
PORTA = PORTA_A     # Porta escolhida para usar no trabalho

########## ATRIBUTOS DO AMBIENTE ##########
# valores iniciais
TEMPERATURA = 25    # temperatura em grau celcius(ºC)
UMIDADE = 0.3       # umidade em porcentagem
CO2 = 0.3           # nivel de co2 em porcentagem

aquecedores_ligados = 0
resfriadores_ligados = 0
irrigadores_ligados = 0
injetoresCO2_ligados = 0

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
last_time = time.time()
while True:
    
    current_time = time.time()
    delta_time = current_time - last_time
    last_time = current_time

    TEMPERATURA += delta_time * (random.random()*2-1)  #função aleatoria para gerar a mudanca de temperatura, umidade e CO2
    UMIDADE -= delta_time * UMIDADE ** 3 * (random.random()*.25)
    CO2 -= delta_time * CO2 ** 4 * (random.random()*.1)

    TEMPERATURA += delta_time * aquecedores_ligados * 2 #função aleatoria para gerar a mudanca de temperatura, umidade e CO2
    TEMPERATURA -= delta_time * resfriadores_ligados * 2 
    UMIDADE += delta_time * irrigadores_ligados * .05
    CO2 += delta_time * injetoresCO2_ligados * .01
    
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
            # exibe conexao estabelecida e inicia uma nova thread para tratar do novo componente
            print(f"Conexao estabelecida de {endereco_cliente[0]}:{endereco_cliente[1]} tipo:{Tipo_Componente(int(componente['Dados'].decode('utf-8')))}")
        # socket modificado nao e o servidor, logo e um sensor ou atuador   
        else:
            componente_modificado = componentes[socket_modificado] # seleciona componente
            tipo = Tipo_Componente(int(componente_modificado['Dados'].decode('utf-8'))) # verifica tipo
            mensagem = recebe_mensagem(socket_modificado)
            if mensagem is False:
                break
            print(f"Mensagem recebida de {tipo} ({componente_modificado['ID_E'].strip()}): {mensagem['Dados'].decode('utf-8')}")
            
            # verifica tipo do sensor e manda informacao relacionada
            if tipo == Tipo_Componente.COMP_SENSOR_TEMPERATURA:
                tamanho = len(str(TEMPERATURA)) # tamanho do dado
                socket_modificado.send(f"99{mensagem['ID_E']}0{tamanho:<3}{str(TEMPERATURA)}".encode('utf-8')) # manda temperatura
            
            elif tipo == Tipo_Componente.COMP_SENSOR_UMIDADE_SOLO:
                tamanho = len(str(UMIDADE)) # tamanho do dado
                socket_modificado.send(f"99{mensagem['ID_E']}0{tamanho:<3}{str(UMIDADE)}".encode('utf-8')) # manda umidade
            
            elif tipo == Tipo_Componente.COMP_SENSOR_NIVEL_CO2:
                tamanho = len(str(CO2)) # tamanho do dado
                socket_modificado.send(f"99{mensagem['ID_E']}0{tamanho:<3}{str(CO2)}".encode('utf-8')) # manda co2
            
            # casos onde o cliente modificado e um atuador
            elif tipo == Tipo_Componente.COMP_ATUADOR_AQUECEDOR:
                if mensagem['Dados'].decode('utf-8') == str(True):
                    aquecedores_ligados += 1
                    print(f"Aquecedor ligado: {componente_modificado['ID_E']} - {aquecedores_ligados}")
                else:
                    aquecedores_ligados -= 1
                    print(f"Aquecedor desligado: {componente_modificado['ID_E']} - {aquecedores_ligados}")
                
            elif tipo == Tipo_Componente.COMP_ATUADOR_RESFRIADOR:
                if mensagem['Dados'].decode('utf-8') == str(True):
                    resfriadores_ligados += 1
                    print(f"Resfriador ligado: {componente_modificado['ID_E']} - {resfriadores_ligados}")
                else:
                    resfriadores_ligados -= 1
                    print(f"Resfriador desligado: {componente_modificado['ID_E']} - {resfriadores_ligados}")
                
            elif tipo == Tipo_Componente.COMP_ATUADOR_IRRIGACAO:
                if mensagem['Dados'].decode('utf-8') == str(True):
                    irrigadores_ligados += 1
                    print(f"Irrigador ligado: {componente_modificado['ID_E']} - {irrigadores_ligados}")
                else:
                    irrigadores_ligados -= 1
                    print(f"Irrigador desligado: {componente_modificado['ID_E']} - {irrigadores_ligados}")
            
            elif tipo == Tipo_Componente.COMP_ATUADOR_INJETOR_CO2:
                if mensagem['Dados'].decode('utf-8') == str(True):
                    injetoresCO2_ligados += 1
                    print(f"Injetor ligado: {componente_modificado['ID_E']} - {injetoresCO2_ligados}")
                else:
                    injetoresCO2_ligados -= 1
                    print(f"Injetor desligado: {componente_modificado['ID_E']} - {injetoresCO2_ligados}")

    # trata clientes com erro de execucao removendo sua coneccao   
    for socket_modificado in sockets_excecao:
        print(f"ERRO!!\nConexao encerrada de {Tipo_Componente(int(componentes[socket_modificado]['Dados'].decode('utf-8')))}:{componentes[socket_modificado]['ID_E'].strip()}")
        sockets_conectados.remove(socket_modificado)
        del componentes[socket_modificado]