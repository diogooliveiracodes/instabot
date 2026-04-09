# InstaBot
Este protótipo tem a finalidade de aumentar a quantidade de seguidores de um determinado perfil do instagram de forma automatizada e deixar de seguir perfis que não te seguem.

## 🚀 Funcionalidades
* Interface gráfica (GUI) para controlar o bot.
* Botão de parar que encerra a operação e fecha o navegador.
* Seguir seguidores de perfis de troca de seguidores para que eles te sigam de volta.
* Listar perfis que não te seguem de volta.
* Deixar de seguir perfis que não te seguem.

## 💻 Pré-requisitos
* Python 3 — https://www.python.org/downloads/
* Google Chrome instalado
* Windows

## 🤖 Instalação
1. Clone o repositório.
2. Instale as dependências:
   ```
   pip install selenium customtkinter
   ```
3. Abra o arquivo `config.py` e configure suas credenciais:
   - `USER_LOGIN` — e-mail ou usuário do Instagram.
   - `USER_PASSWORD` — senha da conta.
4. Execute o script:
   ```
   python main.py
   ```
   Para usar o modo CLI (sem interface gráfica):
   ```
   python main.py --cli
   ```

## 📖 Como usar

### Interface Gráfica (padrão)

Ao executar `python main.py`, a interface gráfica será aberta com os campos de login/senha e os botões de ação:

| Botão | Descrição |
|---|---|
| **Listar não seguidores** | Raspa seguidores e seguindo, salva os não-seguidores em arquivo. |
| **Deixar de seguir** | Carrega a lista de não-seguidores e remove o follow de cada um. |
| **Ganhar seguidores** | Segue perfis da lista configurada em `config.py`. |
| **⏹ Parar Bot** | Interrompe a operação em andamento e fecha o navegador. |

O painel de log na parte inferior exibe todas as mensagens do bot em tempo real.

### Opção — Listar não seguidores
Raspa as listas de seguidores e seguindo do perfil logado, compara ambas e salva os perfis que não seguem de volta em `logs/nao-seguidores.txt`. Nenhum unfollow é realizado.

### Opção — Deixar de seguir não seguidores
Carrega o arquivo `logs/nao-seguidores.txt` e começa a remover o follow de cada perfil da lista. A cada remoção:
- O perfil é adicionado em `logs/removidos.txt` com data e hora.
- O perfil é removido de `logs/nao-seguidores.txt`.

Se o script for interrompido, basta executar a opção novamente — ele continua de onde parou.

### Opção — Ganhar seguidores
O bot abre o perfil configurado em `PROFILE_LIST` (`config.py`), percorre a lista de seguidores desse perfil e segue cada um deles para que sigam de volta.

> **Dica:** execute "Listar não seguidores" primeiro para gerar a lista, revise o arquivo `logs/nao-seguidores.txt` se desejar, e depois execute "Deixar de seguir" para iniciar a remoção.

## 📂 Estrutura de arquivos
```
instabot/
├── main.py                  # Ponto de entrada (GUI ou CLI)
├── gui.py                   # Interface gráfica (CustomTkinter)
├── config.py                # Credenciais e configurações
├── bot/
│   ├── __init__.py
│   ├── instabot.py          # Classe orquestradora
│   ├── browser.py           # Setup do driver, login, popups
│   ├── navigation.py        # Navegação (perfil, seguidores, dialog)
│   ├── scraper.py           # Scroll e extração de usernames
│   ├── actions.py           # Follow / unfollow
│   ├── file_manager.py      # Leitura e escrita dos arquivos .txt
│   └── exceptions.py        # Exceções customizadas
├── logs/
│   ├── nao-seguidores.txt   # Lista dos perfis que não seguem de volta
│   └── removidos.txt        # Histórico de perfis removidos com timestamp
└── README.md
```

## ☠️ Aviso!
A responsabilidade pela utilização deste código é totalmente sua. O mesmo foi desenvolvido para fins acadêmicos e não comerciais. O Instagram não autoriza a utilização de bots em sua plataforma.
