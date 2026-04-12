import sys


class _CliLogger:
    """Tee para stdout que também escreve no arquivo de log."""

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
    from bot import InstaBot
    from bot import logger
    from time import sleep

    choice = '0'
    sub_choice = '0'

    print('\n\nQual função deseja utilizar?')
    print('[ 1 ] - Ganhar seguidores')
    print('[ 2 ] - Deixar de seguir quem não te segue')

    while choice not in ('1', '2'):
        choice = input('\nDigite sua escolha [ 1 ou 2 ] :')
        if choice not in ('1', '2'):
            print('\nOpção inválida, escolha entre [ 1 ou 2 ]')

    if choice == '2':
        print('\n[ 1 ] - Listar não seguidores')
        print('[ 2 ] - Deixar de seguir não seguidores')
        while sub_choice not in ('1', '2'):
            sub_choice = input('\nDigite sua escolha [ 1 ou 2 ] :')
            if sub_choice not in ('1', '2'):
                print('\nOpção inválida, escolha entre [ 1 ou 2 ]')

    log_path = logger.start_session()
    sys.stdout = _CliLogger(sys.stdout)
    print(f'Arquivo de log: {log_path}')

    bot = InstaBot()
    try:
        bot.start()

        if choice == '1':
            bot.farm_followers()
        elif choice == '2' and sub_choice == '1':
            bot.list_unfollowers()
        elif choice == '2' and sub_choice == '2':
            bot.unfollow_from_list()

        sleep(50)
    except Exception as e:
        print(f'\nErro na função Iniciar: {e}')

    print('\nFim do Script')
    logger.stop_session()
    sys.stdout = sys.__stdout__


if __name__ == '__main__':
    if '--cli' in sys.argv:
        cli()
    else:
        from gui import run
        run()
