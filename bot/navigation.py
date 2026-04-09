from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep


class Navigator:
    def __init__(self, driver):
        self.driver = driver

    def search_profile(self, profile_name):
        try:
            search = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH,
                     '//a[.//span[text()="Search"] or .//span[text()="Pesquisar"]]'))
            )
            search.click()
            sleep(1)
        except Exception:
            print('\nErro ao clicar na barra de pesquisa')

        try:
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
        except Exception:
            print('\nErro ao digitar perfil a ser pesquisado')

        print('\nPESQUISA DE PERFIL REALIZADA COM SUCESSO')

    def open_followers(self):
        try:
            followers = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//a[contains(@href, "/followers/")]'))
            )
            followers.click()
            sleep(2)
        except Exception:
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
        except Exception:
            print('\nErro ao abrir lista de perfis seguidos')
        print('\nABERTURA DE LISTA DE PERFIS SEGUIDOS REALIZADA COM SUCESSO')

    def close_dialog(self):
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
        except Exception:
            pass

        if not closed:
            try:
                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
            except Exception:
                pass

        sleep(2)

        try:
            WebDriverWait(self.driver, 5).until(
                lambda d: '/followers' not in d.current_url
                and '/following' not in d.current_url
            )
        except Exception:
            try:
                current = self.driver.current_url
                if '/followers' in current or '/following' in current:
                    base = current.split('/followers')[0].split('/following')[0] + '/'
                    self.driver.get(base)
                    sleep(2)
            except Exception:
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
                    By.XPATH,
                    '//a[.//span[text()="Profile"] or .//span[text()="Perfil"]]'
                )
                profile_link.click()
        except Exception:
            print('\nNão foi possível abrir o próprio perfil')

        sleep(2)
        print('\nPERFIL ABERTO COM SUCESSO')
