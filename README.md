# InstaBot
Este protótipo tem a finalidade de aumentar a quantidade de seguidores de um determinado perfil do instagram de forma automatizada e deixar de seguir perfis que não te seguem.

## Utilização
Antes de iniciar o script é necessário preencher as variáveis: <br>
self.user_login - login do usuario que quer ganhar seguidores. <br>
self.user_password - senha do usuario que quer ganhar seguidores.

## Funcionalidades
1. Seguir seguidores de perfis de troca de seguidores para que eles te sigam de volta.
2. Deixar de seguir perfis que não te seguem.

## Requerimentos
Python3 - Download: https://www.python.org/downloads/

Chrome Webdriver - Download: https://chromedriver.chromium.org/downloads

## Como instalar:
1. Faça o download do Chrome Webdriver.
2. Salve o executável do Chrome Webdriver no endereço: C:\Program Files (x86)\chromedriver.exe Caso fizer a instalação em endereço diferente, certifique-se de alterar na linha 36 a variável PATH com o novo endereço do arquivo.
3. Faça o download e instale o python3.*
4. Utilize o comando "pip install selenium" no terminal para instalar os pacotes.
5. Faça o download do arquivo main.py (neste repositório).
6. Abra sua IDE de preferência e configure as variáveis self.user_login e self.user_password.
7. Execute o código e veja a mágica acontecer.

## Testado em:
Windows 10 & Python 3.9

## Aviso!
A responsabilidade pela utilização deste código é totalmente sua. A política do Instagram pode mudar e este script pode passar a ser detectado, ocasionando o banimento da sua conta.
