from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from time import sleep

__author__ = "Diogo Oliveira"
__date__ = "06/01/2020"
__version__ = "2.0.0"


class InstaBot():
    def __init__(self):

        self.choose = '0'
        print('\n\nQual função deseja utilizar?\n[ 1 ] - Ganhar seguidores\n[ 2 ] - Deixar de seguir quem não te segue')
        while self.choose != '1' and self.choose != '2':
            self.choose = input('\nDigite sua escolha [ 1 ou 2 ] :')
            if self.choose != '1' and self.choose != '2':
                print('\nOpção inválida, escolha entre [ 1 ou 2 ]')

        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.get("https://instagram.com")
        self.profile_list = ['capivara.dev']
        self.user_login = ""
        self.user_password = ""
        self.number_to_follow = 2500
        self.followers = []
        self.following = []
        self.unfollowers = ['lista', 'de', 'não', 'seguidores']

        try:
            self.do_login()
            sleep(5)
            self.dismiss_popups()
            if self.choose == '1':
                self.farm_followers()
            elif self.choose == '2':
                self.unfollow_unfollowers()
            sleep(50)
        except:
            print('\nErro na função Iniciar')
        print('\nFim do Script')

    def do_login(self):
        try:
            login_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'input[name="email"]'))
            )
            login_input.send_keys(self.user_login)
        except:
            print('\nErro ao preencher o login')
        try:
            password_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'input[name="pass"]'))
            )
            password_input.send_keys(self.user_password)
            sleep(1)
        except:
            print('\nErro ao preencher a senha')
        try:
            login_button = self.driver.find_element(By.CSS_SELECTOR, 'form button')
            login_button.click()
        except:
            try:
                password_input.send_keys(Keys.RETURN)
            except:
                print('\nErro ao clicar no botão Entrar')
        print('\nLOGIN REALIZADO COM SUCESSO')

    def dismiss_popups(self):
        for _ in range(2):
            try:
                not_now = WebDriverWait(self.driver, 8).until(
                    EC.element_to_be_clickable(
                        (By.XPATH,
                         '//button[text()="Not Now" or text()="Not now" '
                         'or text()="Agora não" or text()="Ahora no"]'))
                )
                not_now.click()
                sleep(3)
            except:
                try:
                    self.driver.execute_script("""
                        const btns = document.querySelectorAll('button');
                        for (const b of btns) {
                            const t = b.textContent.trim().toLowerCase();
                            if (t === 'not now' || t === 'agora não') {
                                b.click(); return;
                            }
                        }
                    """)
                    sleep(3)
                except:
                    pass

    def search_profile(self):
        try:
            search = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH,
                     '//a[.//span[text()="Search"] or .//span[text()="Pesquisar"]]'))
            )
            search.click()
            sleep(1)
        except:
            print('\nErro ao clicar na barra de pesquisa')
        try:
            profile_name = self.profile_list[0]
            search_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     'input[placeholder="Search"], input[placeholder="Pesquisar"]'))
            )
            search_input.clear()
            search_input.send_keys(profile_name)
            sleep(3)
            searched_profile = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, f'//a[contains(@href, "/{profile_name}/")]'))
            )
            searched_profile.click()
        except:
            print('\nErro ao digitar perfil a ser pesquisado')
        self.profile_list.remove(self.profile_list[0])
        print('\nPESQUISA DE PERFIL REALIZADA COM SUCESSO')

    def open_followers(self):
        try:
            followers = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//a[contains(@href, "/followers/")]'))
            )
            followers.click()
            sleep(2)
        except:
            print('\nErro ao abrir seguidores')
        print('\nABERTURA DOS SEGUIDORES REALIZADA COM SUCESSO')

    def open_following(self):
        try:
            following = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//a[contains(@href, "/following/")]'))
            )
            following.click()
            sleep(2)
        except:
            print('\nErro ao abrir lista de perfis seguidos')
        print('\nABERTURA DE LISTA DE PERFIS SEGUIDOS REALIZADA COM SUCESSO')

    def _scroll_dialog_and_count(self):
        """Rola o container do dialog até o final e retorna a qtd de links de perfil carregados."""
        return self.driver.execute_script("""
            const dialog = document.querySelector('div[role="dialog"]');
            if (!dialog) return 0;
            const divs = dialog.querySelectorAll('div');
            for (const div of divs) {
                const style = window.getComputedStyle(div);
                const ov = style.overflowY;
                if ((ov === 'auto' || ov === 'scroll' || ov === 'hidden')
                    && div.scrollHeight > div.clientHeight && div.clientHeight > 50) {
                    div.scrollTo(0, div.scrollHeight);
                    break;
                }
            }
            const links = dialog.querySelectorAll('a[href]');
            let count = 0;
            const seen = new Set();
            for (const a of links) {
                const href = a.getAttribute('href');
                if (href && href.startsWith('/') && href !== '/'
                    && !href.startsWith('/explore') && !href.startsWith('/accounts')
                    && !seen.has(href)) {
                    seen.add(href);
                    count++;
                }
            }
            return count;
        """)

    def sweep_followers(self):
        try:
            sleep(2)
            stable_checks = 0
            last_count = 0
            iterations = 0
            while stable_checks < 3:
                count = self._scroll_dialog_and_count()
                sleep(2)
                if count == last_count:
                    stable_checks += 1
                else:
                    stable_checks = 0
                last_count = count
                iterations += 1
                if iterations % 10 == 0:
                    print(f'  Scroll: {count} perfis carregados...')
                if iterations >= 500:
                    print(f'  Limite de iterações atingido ({count} perfis)')
                    break
        except:
            print('\nErro na função sweep_followers')
        print(f'\nVARREDURA DE SEGUIDORES REALIZADA COM SUCESSO ({last_count} perfis)')

    def sweep_all_followers(self):
        try:
            sleep(2)
            stable_checks = 0
            last_count = 0
            iterations = 0
            while stable_checks < 3:
                count = self._scroll_dialog_and_count()
                sleep(2)
                if count == last_count:
                    stable_checks += 1
                else:
                    stable_checks = 0
                last_count = count
                iterations += 1
                if iterations % 10 == 0:
                    print(f'  Scroll: {count} perfis carregados...')
        except:
            print('\nErro na função sweep_all_followers')
        print(f'\nVARREDURA DE SEGUIDORES REALIZADA COM SUCESSO ({last_count} perfis)')

    def follow(self):
        try:
            follow_buttons = self.driver.find_elements(
                By.XPATH, '//div[@role="dialog"]//button'
            )
            count = 0
            for btn in follow_buttons:
                if count >= self.number_to_follow // 2:
                    break
                try:
                    btn_text = btn.text.strip()
                    if btn_text in ['Follow', 'Seguir']:
                        btn.click()
                        count += 1
                        sleep(300)
                except:
                    pass
        except:
            print('\nErro na função follow')
        print('\nPERFIS SEGUIDOS COM SUCESSO')

    def close_followers_box(self):
        closed = False
        try:
            closed = self.driver.execute_script("""
                const dialog = document.querySelector('div[role="dialog"]');
                if (!dialog) return false;
                const svg = dialog.querySelector('svg[aria-label="Close"]');
                if (svg) {
                    const btn = svg.closest('button') || svg.parentElement;
                    if (btn) { btn.click(); return true; }
                }
                return false;
            """)
        except:
            pass
        if not closed:
            try:
                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
            except:
                pass
        sleep(2)
        try:
            WebDriverWait(self.driver, 5).until(
                lambda d: '/followers' not in d.current_url and '/following' not in d.current_url
            )
        except:
            try:
                current = self.driver.current_url
                if '/followers' in current or '/following' in current:
                    base = current.split('/followers')[0].split('/following')[0] + '/'
                    self.driver.get(base)
                    sleep(2)
            except:
                pass
        print('\nLISTA FECHADA COM SUCESSO')

    def open_self_profile(self):
        try:
            profile_url = self.driver.execute_script("""
                const svg = document.querySelector('svg[aria-label="Profile"]');
                if (svg) {
                    const link = svg.closest('a');
                    if (link) return link.href;
                }
                const links = document.querySelectorAll('nav a[href]');
                for (const a of links) {
                    const spans = a.querySelectorAll('span');
                    for (const s of spans) {
                        if (s.textContent === 'Profile' || s.textContent === 'Perfil') {
                            return a.href;
                        }
                    }
                }
                return null;
            """)
            if profile_url:
                self.driver.get(profile_url)
            else:
                profile_link = self.driver.find_element(
                    By.XPATH, '//a[.//span[text()="Profile"] or .//span[text()="Perfil"]]'
                )
                profile_link.click()
        except:
            print('\nNão foi possível abrir o próprio perfil')
        sleep(2)
        print('\nPERFIL ABERTO COM SUCESSO')

    def _get_usernames_from_dialog(self):
        """Extrai usernames das URLs dos links dentro do dialog de seguidores/seguindo."""
        usernames = []
        try:
            dialog = self.driver.find_element(By.CSS_SELECTOR, 'div[role="dialog"]')
            links = dialog.find_elements(By.TAG_NAME, 'a')
            seen = set()
            excluded = {'', '#', 'explore', 'accounts', 'p', 'reel', 'stories', 'reels'}
            for link in links:
                href = link.get_attribute('href')
                if href:
                    username = href.rstrip('/').split('/')[-1]
                    if username and username not in seen and username not in excluded:
                        seen.add(username)
                        usernames.append(username)
        except:
            pass
        return usernames

    def get_followers(self):
        self.open_followers()
        sleep(2)
        self.sweep_all_followers()
        self.followers = self._get_usernames_from_dialog()
        self.close_followers_box()
        print('\nFunção get_followers executada com sucesso!')

    def get_following(self):
        self.open_following()
        sleep(2)
        self.sweep_all_followers()
        self.following = self._get_usernames_from_dialog()
        self.close_followers_box()
        print('\nFunção get_following executada com sucesso!')

    def get_unfollowers(self):
        self.unfollowers = [user for user in self.following if user not in self.followers]

    def farm_followers(self):
        print('\nComeçando a função farm_followers')
        try:
            for profile in self.profile_list[:]:
                self.search_profile()
                sleep(5)
                self.open_followers()
                sleep(10)
                self.sweep_followers()
                sleep(5)
                self.follow()
                sleep(2)
                self.close_followers_box()
                sleep(2)
        except:
            print('\nErro na função farm_followers')

    def unfollow(self):
        self.open_following()
        sleep(2)
        self.sweep_all_followers()
        sleep(2)
        try:
            dialog = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div[role="dialog"]'))
            )
            buttons = dialog.find_elements(By.TAG_NAME, 'button')
            count = 0

            for btn in buttons:
                if btn.text.strip() in ['Following', 'Seguindo']:
                    parent = btn.find_element(By.XPATH, './ancestor::div[.//a[contains(@href, "/")]]')
                    links = parent.find_elements(By.TAG_NAME, 'a')
                    for link in links:
                        href = link.get_attribute('href')
                        if href:
                            username = href.rstrip('/').split('/')[-1]
                            if username in self.unfollowers:
                                btn.click()
                                sleep(1)
                                unfollow_button = WebDriverWait(self.driver, 10).until(
                                    EC.element_to_be_clickable(
                                        (By.XPATH,
                                         '//button[text()="Unfollow" or text()="Deixar de seguir"]'))
                                )
                                sleep(1)
                                unfollow_button.click()
                                count += 1
                                self._append_removed(username)
                                print(f'\nRemovido o follow do perfil: {username}')
                                print(f'Número de follows removidos: {count}')
                                self.unfollowers.remove(username)
                                print(f'Unfollowers restantes: {len(self.unfollowers)}')
                                sleep(300)
                                break

            self.close_followers_box()
        except:
            print('\nErro na função unfollow')
            self.close_followers_box()

    def _save_unfollowers_list(self):
        filename = datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.txt'
        with open(filename, 'w', encoding='utf-8') as f:
            for user in self.unfollowers:
                f.write(user + '\n')
        print(f'\nLista de não-seguidores salva em: {filename}')
        return filename

    def _append_removed(self, username):
        with open('removidos.txt', 'a', encoding='utf-8') as f:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f'{username} - {timestamp}\n')

    def unfollow_unfollowers(self):
        try:
            self.open_self_profile()
            sleep(2)

            self.get_followers()
            print(f'\n\nNúmero de Seguidores: {len(self.followers)}')

            self.get_following()
            print(f'\n\nNúmero de Seguindo: {len(self.following)}')

            self.get_unfollowers()
            print(f'\nNúmero de perfis que não seguem de volta: {len(self.unfollowers)}')

            self._save_unfollowers_list()

            while len(self.unfollowers) > 0:
                self.unfollow()
                sleep(2)
                self.open_self_profile()
                sleep(2)
                self.get_followers()
                self.get_following()
                self.get_unfollowers()
                print(f'\nUnfollowers restantes: {len(self.unfollowers)}')

        except:
            print('\nErro na função unfollow_unfollowers')

    def close_popup(self):
        try:
            not_now = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH,
                     '//button[text()="Not Now" or text()="Not now" '
                     'or text()="Agora não" or text()="Ahora no"]'))
            )
            not_now.click()
        except:
            try:
                self.driver.execute_script("""
                    const btns = document.querySelectorAll('button');
                    for (const b of btns) {
                        const t = b.textContent.trim().toLowerCase();
                        if (t === 'not now' || t === 'agora não') {
                            b.click(); return;
                        }
                    }
                """)
            except:
                pass
        print('\nPOPUP FECHADO COM SUCESSO')

InstaBot()
