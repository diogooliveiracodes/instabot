import config
from time import sleep
from bot.browser import BrowserManager
from bot.navigation import Navigator
from bot.scraper import Scraper
from bot.actions import ActionHandler
from bot.file_manager import FileManager


class InstaBot:
    def __init__(self):
        self.browser = BrowserManager()
        self.driver = self.browser.setup(config.INSTAGRAM_URL)
        self.nav = Navigator(self.driver)
        self.scraper = Scraper(self.driver)
        self.actions = ActionHandler(self.driver)
        self.files = FileManager()
        self.followers = []
        self.following = []
        self.unfollowers = []

    def start(self):
        self.browser.login(config.USER_LOGIN, config.USER_PASSWORD)
        sleep(5)
        self.browser.dismiss_popups()

    # ── Coleta de dados ──────────────────────────────────────────────

    def get_followers(self):
        self.nav.open_followers()
        sleep(2)
        self.scraper.sweep()
        self.followers = self.scraper.get_usernames()
        self.nav.close_dialog()
        print('\nFunção get_followers executada com sucesso!')

    def get_following(self):
        self.nav.open_following()
        sleep(2)
        self.scraper.sweep(only_following=True)
        self.following = self.scraper.get_usernames(only_following=True)
        self.nav.close_dialog()
        print('\nFunção get_following executada com sucesso!')

    def get_unfollowers(self):
        self.unfollowers = [u for u in self.following if u not in self.followers]

    # ── Fluxo 1: Ganhar seguidores ───────────────────────────────────

    def farm_followers(self):
        print('\nComeçando a função farm_followers')
        try:
            for profile_name in config.PROFILE_LIST[:]:
                self.nav.search_profile(profile_name)
                sleep(5)
                self.nav.open_followers()
                sleep(10)
                self.scraper.sweep(max_iterations=500)
                sleep(5)
                self.actions.follow_users(config.NUMBER_TO_FOLLOW // 2)
                sleep(2)
                self.nav.close_dialog()
                sleep(2)
        except Exception:
            print('\nErro na função farm_followers')

    # ── Fluxo 2.1: Listar não seguidores ─────────────────────────────

    def list_unfollowers(self):
        try:
            self.nav.open_self_profile()
            sleep(2)

            self.get_followers()
            print(f'\n\nNúmero de Seguidores: {len(self.followers)}')

            self.get_following()
            print(f'\n\nNúmero de Seguindo: {len(self.following)}')

            self.get_unfollowers()
            print(f'\nNúmero de perfis que não seguem de volta: {len(self.unfollowers)}')

            self.files.save_unfollowers(self.unfollowers)
            print('\nListagem concluída com sucesso!')
        except Exception:
            print('\nErro na função list_unfollowers')

    # ── Fluxo 2.2: Deixar de seguir não seguidores ───────────────────

    def unfollow_from_list(self):
        try:
            self.unfollowers = self.files.load_unfollowers()
            if not self.unfollowers:
                print('\nNenhum não-seguidor na lista. Execute a opção 1 primeiro.')
                return

            print(f'\nIniciando remoção de {len(self.unfollowers)} não-seguidores...')

            self.nav.open_self_profile()
            sleep(2)
            self.nav.open_following()
            sleep(2)
            self.scraper.sweep(only_following=True)
            sleep(2)

            while self.unfollowers:
                removed = self.actions.unfollow_from_dialog(self.unfollowers)
                if removed:
                    self.unfollowers = self.files.process_removal(
                        removed, self.unfollowers)
                    print(f'Unfollowers restantes: {len(self.unfollowers)}')
                else:
                    print('\nNenhum unfollower encontrado no dialog atual.')
                    break

            self.nav.close_dialog()
            print('\nTodos os não-seguidores foram removidos!')
        except Exception:
            print('\nErro na função unfollow_from_list')
