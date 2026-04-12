import sys


class _CliLogger:
    def __init__(self, original):
        self._original = original

    def write(self, text):
        if self._original:
            self._original.write(text)
        if text and text.strip():
            from bot import logger
            logger.log(text.strip())

    def flush(self):
        if self._original:
            self._original.flush()


def cli():
    from bot import InstaBot, logger, profiles
    from time import sleep

    saved = profiles.load_profiles()
    login = password = username = None

    if saved:
        print('\nPerfis salvos:')
        for i, p in enumerate(saved):
            print(f'  [{i + 1}] @{p["username"]}')
        print(f'  [0] Novo login')
        choice = input('\nEscolha: ').strip()
        if choice.isdigit() and 0 < int(choice) <= len(saved):
            p = saved[int(choice) - 1]
            login, password, username = p['login'], p['password'], p['username']

    if not login:
        login = input('Login: ').strip()
        password = input('Senha: ').strip()

    if username:
        profile_dir = profiles.get_profile_dir(username)
    else:
        profile_dir = None

    choice = '0'
    sub_choice = '0'

    print('\n\nQual função deseja utilizar?')
    print('[ 1 ] - Ganhar seguidores')
    print('[ 2 ] - Deixar de seguir quem não te segue')

    while choice not in ('1', '2'):
        choice = input('\nDigite sua escolha [ 1 ou 2 ] :')

    if choice == '2':
        print('\n[ 1 ] - Listar não seguidores')
        print('[ 2 ] - Deixar de seguir não seguidores')
        while sub_choice not in ('1', '2'):
            sub_choice = input('\nDigite sua escolha [ 1 ou 2 ] :')

    if not profile_dir:
        import tempfile
        profile_dir = tempfile.mkdtemp(prefix='instabot_')

    logger.set_profile_dir(profile_dir)
    log_path = logger.start_session()
    sys.stdout = _CliLogger(sys.stdout)
    print(f'Arquivo de log: {log_path}')

    bot = InstaBot(
        login=login, password=password,
        profile_dir=profile_dir)
    try:
        bot.start()

        if not username:
            detected = bot.capture_username()
            if detected:
                username = detected
                new_dir = profiles.get_profile_dir(username)
                bot.files = __import__(
                    'bot.file_manager', fromlist=['FileManager']
                ).FileManager(new_dir)
                profiles.save_profile(login, password, username)

        if choice == '1':
            bot.farm_followers()
        elif choice == '2' and sub_choice == '1':
            bot.list_unfollowers()
        elif choice == '2' and sub_choice == '2':
            bot.unfollow_from_list()

        sleep(5)
    except Exception as e:
        print(f'\nErro: {e}')

    print('\nFim do Script')
    logger.stop_session()
    sys.stdout = sys.__stdout__


if __name__ == '__main__':
    if '--cli' in sys.argv:
        cli()
    else:
        from gui import run
        run()
