# InstaBot
Este protótipo tem a finalidade de aumentar a quantidade de seguidores de um determinado perfil do instagram de forma automatizada e deixar de seguir perfis que não te seguem.

## 🚀 Funcionalidades
* Seguir seguidores de perfis de troca de seguidores para que eles te sigam de volta.
* Listar perfis que não te seguem de volta.
* Deixar de seguir perfis que não te seguem.

## 💻 Pré-requisitos
* Python 3 — https://www.python.org/downloads/
* Google Chrome instalado
* Windows

## 🤖 Instalação
1. Clone o repositório.
2. Instale a dependência do Selenium:
   ```
   pip install selenium
   ```
3. Abra o arquivo `config.py` e configure suas credenciais:
   - `USER_LOGIN` — e-mail ou usuário do Instagram.
   - `USER_PASSWORD` — senha da conta.
4. Execute o script:
   ```
   python main.py
   ```

## 📖 Como usar

Ao executar o script, o menu principal será exibido:

```
[ 1 ] - Ganhar seguidores
[ 2 ] - Deixar de seguir quem não te segue
```

### Opção 1 — Ganhar seguidores
O bot abre o perfil configurado em `PROFILE_LIST` (`config.py`), percorre a lista de seguidores desse perfil e segue cada um deles para que sigam de volta.

### Opção 2 — Deixar de seguir quem não te segue
Ao selecionar esta opção, um sub-menu é apresentado:

```
[ 1 ] - Listar não seguidores
[ 2 ] - Deixar de seguir não seguidores
```

#### 2.1 — Listar não seguidores
Raspa as listas de seguidores e seguindo do perfil logado, compara ambas e salva os perfis que não seguem de volta em `logs/nao-seguidores.txt`. Nenhum unfollow é realizado.

#### 2.2 — Deixar de seguir não seguidores
Carrega o arquivo `logs/nao-seguidores.txt` gerado pela opção 2.1 e começa a remover o follow de cada perfil da lista. A cada remoção:
- O perfil é adicionado em `logs/removidos.txt` com data e hora.
- O perfil é removido de `logs/nao-seguidores.txt`.

Se o script for interrompido, basta executar a opção 2.2 novamente — ele continua de onde parou.

> **Dica:** execute a opção 2.1 primeiro para gerar a lista, revise o arquivo `logs/nao-seguidores.txt` se desejar, e depois execute a opção 2.2 para iniciar a remoção.

## 📂 Estrutura de arquivos
```
instabot/
├── main.py                  # Ponto de entrada (menu)
├── config.py                # Credenciais e configurações
├── bot/
│   ├── __init__.py
│   ├── instabot.py          # Classe orquestradora
│   ├── browser.py           # Setup do driver, login, popups
│   ├── navigation.py        # Navegação (perfil, seguidores, dialog)
│   ├── scraper.py           # Scroll e extração de usernames
│   ├── actions.py           # Follow / unfollow
│   └── file_manager.py      # Leitura e escrita dos arquivos .txt
├── logs/
│   ├── nao-seguidores.txt   # Lista dos perfis que não seguem de volta
│   └── removidos.txt        # Histórico de perfis removidos com timestamp
└── README.md
```

## ☠️ Aviso!
A responsabilidade pela utilização deste código é totalmente sua. O mesmo foi desenvolvido para fins acadêmicos e não comerciais. O Instagram não autoriza a utilização de bots em sua plataforma.
