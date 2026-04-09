from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from time import sleep


class BrowserManager:
    def __init__(self):
        self.driver = None

    def quit(self):
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None

    def setup(self, url):
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.get(url)
        return self.driver

    def login(self, username, password):
        try:
            login_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'input[name="email"]'))
            )
            login_input.send_keys(username)
        except Exception:
            print('\nErro ao preencher o login')

        try:
            password_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'input[name="pass"]'))
            )
            password_input.send_keys(password)
            sleep(1)
        except Exception:
            print('\nErro ao preencher a senha')

        try:
            login_button = self.driver.find_element(By.CSS_SELECTOR, 'form button')
            login_button.click()
        except Exception:
            try:
                password_input.send_keys(Keys.RETURN)
            except Exception:
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
            except Exception:
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
                except Exception:
                    pass
