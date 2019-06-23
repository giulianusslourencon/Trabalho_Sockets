Trabalho de Redes (SSC0142) 2019 - ICMC - USP São Carlos

Alexandre Norcia Medeiros - 10295583
Gabriel Alfonso Nascimento Salgueiro - 10284368
Giuliano Lourençon - 10295590
Pedro Francisco Darela Neto - 10295624

Trabalho referente a uma estufa inteligente, feito na linguagem **python 3.6.8** utilizando o Sistema Operacional **Linux Mint**.

Nesta aplicação, as condições da estufa são configuradas, monitoradas e controladas por um gerenciador, que se comunica com os sensores/atuadores dentro da estufa e pode receber configurações ou responder consultas de um cliente externo.

Os componentes dessa aplicação se comunicam utilizando sockets com o seguinte protocolo de cabeçalho:

- **ID Emissor** -> 2 bytes (0 até 99)
- **ID Receptor** -> 2 bytes (0 até 99)
- **Tipo mensagem** -> 1 byte (0 até 9), com tipos pré definidos
- **Tamanho da mensagem** -> 3 bytes (0 até 999), representa a quantidade de caractes existentes na mensagem
- **Dados** -> 'Tamanho da mensagem' bytes

Componentes presentes no sistema e suas funções:

- **Ambiente:** responsavel por simular e lidar com os parametros do ambiente de uma estufa (nivel de cO2, temperatura e umidade).
- **Sensores:** leem os parâmetros do ambiente e informam ao gerenciador periodicamente, a cada um segundo.
- **Atuadores:** recebem comandos do gerenciador para ligamento ou desligamento; também são responsáveis por alterar os parâmetros do ambiente.
- **Cliente:** se comunica com o gerenciador para solicitar dados coletados dos sensores e estabelecer as faixas de parâmetros desejados no ambiente.
- **Gerenciador:** se comunica com os sensores, atuadores e cliente de forma a controlar o ambiente como requisitado pelo cliente.

Interação entre componentes do sistema:

- **Ambiente** interage com **sensores** e **atuadores**
- **Sensores** e **atuadores** interagem com o **ambiente** e com o **gerenciador**
- **Gerenciador** interage com **sensores**, **atuadores** e com o **cliente**
- **Cliente** interage com o **gerenciador**

Ordem para execução dos arquivos:

    gerenciador.py - ambiente.py - sensor_temperatura.py - sensor_co2.py - sensor_umidade.py - atuador_aquecedor.py - atuador_injetor.py - atuador_irrigacao.py - atuador_resfriador.py - cliente.py .

Existem dois servidores que devem ser executados antes dos clientes, eles são o 'ambiente.py' e o 'gerenciador.py' .
Apos a execucao dos servidores, deve-se executar os sensores: 'sensor_co2.py', 'sensor_temperatura.py' e 'sensor_umiade.py'.
Apos isso, deve-se executar os atuadores: 'atuador_aquecedor.py', 'atuador_injetorCO2.py', 'atuador_irrigacao.py' e 'atuador_resfriador.py'
Por fim, deve-se executar o cliente, onde o usuario pode interagir com o gerenciador da estufa atraves de inputs pelo terminal.
