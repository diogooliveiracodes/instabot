import config
import threading
from time import sleep
from bot.browser import BrowserManager
from bot.navigation import Navigator
from bot.scraper import Scraper
from bot.actions import ActionHandler
from bot.file_manager import FileManager
from bot.exceptions import BotStoppedException


class InstaBot:
    def __init__(self, login, password, profile_dir,
                 stop_event=None):
        self._login = login
        self._password = password
        self._profile_dir = profile_dir
        self._stop_event = stop_event or threading.Event()

        self.browser = BrowserManager()
        self.driver = self.browser.setup(config.INSTAGRAM_URL)
        self.nav = Navigator(self.driver)
        self.scraper = Scraper(self.driver, self._stop_event)
        self.actions = ActionHandler(self.driver, self._stop_event)
        self.files = FileManager(profile_dir)
        self.followers = []
        self.following = []
        self.unfollowers = []
        self.username = None

    def _check(self):
        if self._stop_event.is_set():
            raise BotStoppedException()

    def _sleep(self, seconds):
        if self._stop_event.wait(seconds):
            raise BotStoppedException()

    def quit(self):
        self.browser.quit()

    def start(self):
        self.browser.login(self._login, self._password)
        self._sleep(5)
        self._check()
        self.browser.dismiss_popups()

    def capture_username(self):
        """Captura o username do perfil logado a partir da URL do perfil."""
        try:
            url = self.driver.execute_script("""
                const labels = ['Profile', 'Perfil'];
                for (const label of labels) {
                    const svg = document.querySelector(
                        'svg[aria-label="' + label + '"]');
                    if (svg) {
                        const link = svg.closest('a');
                        if (link) return link.href;
                    }
                }
                const allLinks = document.querySelectorAll('a[href]');
                for (const a of allLinks) {
                    const spans = a.querySelectorAll('span');
                    for (const s of spans) {
                        const t = s.textContent.trim();
                        if (t === 'Profile' || t === 'Perfil') return a.href;
                    }
                }
                return null;
            """)
            if url:
                self.username = url.rstrip('/').split('/')[-1]
                print(f'\nPerfil detectado: {self.username}')
                return self.username
        except Exception:
            pass

        try:
            self.nav.open_self_profile()
            self._sleep(2)
            current_url = self.driver.current_url
            self.username = current_url.rstrip('/').split('/')[-1]
            print(f'\nPerfil detectado (via URL): {self.username}')
            return self.username
        except Exception as e:
            print(f'\nErro ao capturar username: {e}')
        return None

    def _restart_session(self):
        print('\n' + '=' * 50)
        print('REINICIANDO SESSÃO DO NAVEGADOR')
        print('=' * 50)
        self.browser.quit()
        self._sleep(5)
        self._check()

        self.driver = self.browser.setup(config.INSTAGRAM_URL)
        self.nav = Navigator(self.driver)
        self.scraper = Scraper(self.driver, self._stop_event)
        self.actions = ActionHandler(self.driver, self._stop_event)

        self.browser.login(self._login, self._password)
        self._sleep(5)
        self._check()
        self.browser.dismiss_popups()
        print('Nova sessão iniciada com sucesso!\n')

    # ── Coleta de dados ──────────────────────────────────────────────

    def get_followers(self):
        self._check()
        self.nav.open_followers()
        self._sleep(2)
        self.scraper.sweep()
        self.followers = self.scraper.get_usernames()
        self.nav.close_dialog()
        print('\nFunção get_followers executada com sucesso!')

    def get_following(self):
        self._check()
        self.nav.open_following()
        self._sleep(2)
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
                self._check()
                self.nav.search_profile(profile_name)
                self._sleep(5)
                self.nav.open_followers()
                self._sleep(10)
                self.scraper.sweep(max_iterations=500)
                self._sleep(5)
                self.actions.follow_users(config.NUMBER_TO_FOLLOW // 2)
                self._sleep(2)
                self.nav.close_dialog()
                self._sleep(2)
        except BotStoppedException:
            raise
        except Exception as e:
            print(f'\nErro na função farm_followers: {e}')

    # ── Fluxo 2.1: Listar não seguidores ─────────────────────────────

    def list_unfollowers(self):
        try:
            self.nav.open_self_profile()
            self._sleep(2)

            self.get_followers()
            print(f'\n\nNúmero de Seguidores: {len(self.followers)}')

            self.get_following()
            print(f'\n\nNúmero de Seguindo: {len(self.following)}')

            self.get_unfollowers()
            print(f'\nNúmero de perfis que não seguem de volta: '
                  f'{len(self.unfollowers)}')

            self.files.save_unfollowers(self.unfollowers)
            self.files.save_followers(self.followers)
            print('\nListagem concluída com sucesso!')
        except BotStoppedException:
            raise
        except Exception as e:
            print(f'\nErro na função list_unfollowers: {e}')

    # ── Fluxo 3: Verificar quem deixou de seguir ─────────────────────

    def check_lost_followers(self):
        try:
            self.nav.open_self_profile()
            self._sleep(2)

            self.get_followers()
            print(f'\n\nNúmero de Seguidores atual: {len(self.followers)}')

            lost = self.files.detect_lost_followers(self.followers)
            print(f'\nTotal de perdidos registrados: {len(lost)}')
            print('\nVerificação concluída com sucesso!')
            return lost
        except BotStoppedException:
            raise
        except Exception as e:
            print(f'\nErro na função check_lost_followers: {e}')
            return []

    # ── Fluxo 2.2: Deixar de seguir não seguidores ───────────────────

    def unfollow_from_list(self):
        try:
            self.unfollowers = self.files.load_unfollowers()
            if not self.unfollowers:
                print('\nNenhum não-seguidor na lista. Execute a opção 1 '
                      'primeiro.')
                return

            total = len(self.unfollowers)
            batch_size = config.UNFOLLOW_BATCH_SIZE
            interval = config.UNFOLLOW_INTERVAL

            print(f'\nIniciando remoção de {total} não-seguidores...')
            print(f'Configuração: {batch_size} por lote, '
                  f'{interval // 60} min entre cada unfollow')

            batch_count = 0
            consecutive_failures = 0

            while self.unfollowers:
                self._check()
                username = self.unfollowers[0]

                success = self.actions.unfollow_profile(
                    username, self.unfollowers)

                if success:
                    consecutive_failures = 0
                    batch_count += 1
                    self.unfollowers = self.files.process_removal(
                        username, self.unfollowers)
                    print(f'Unfollowers restantes: {len(self.unfollowers)} '
                          f'(lote {batch_count}/{batch_size})')

                    if not self.unfollowers:
                        break

                    if batch_count >= batch_size:
                        print(f'\nLote de {batch_count} unfollows concluído.')
                        print(f'Aguardando {interval // 60} minutos '
                              'antes de reiniciar a sessão...')
                        self._sleep(interval)
                        self._restart_session()
                        batch_count = 0
                    else:
                        print(f'Aguardando {interval // 60} minutos '
                              'antes da próxima remoção...')
                        self._sleep(interval)
                else:
                    consecutive_failures += 1
                    if consecutive_failures >= 5:
                        print('\n5 falhas consecutivas. Encerrando o loop.')
                        break
                    print(f'  Falha ({consecutive_failures}/5). '
                          'Pulando para o próximo...')
                    self.unfollowers.append(self.unfollowers.pop(0))
                    self.files.save_unfollowers(self.unfollowers)
                    self._sleep(10)

            removed_count = total - len(self.unfollowers)
            print(f'\nProcesso concluído! {removed_count} perfis removidos.')
        except BotStoppedException:
            raise
        except Exception as e:
            print(f'\nErro na função unfollow_from_list: {e}')
