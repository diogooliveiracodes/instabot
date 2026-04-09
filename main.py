from bot import InstaBot
from time import sleep


def show_menu():
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

    return choice, sub_choice


def main():
    choice, sub_choice = show_menu()

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
    except Exception:
        print('\nErro na função Iniciar')

    print('\nFim do Script')


if __name__ == '__main__':
    main()
