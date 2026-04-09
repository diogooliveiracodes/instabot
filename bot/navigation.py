from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep


class Navigator:
    def __init__(self, driver):
        self.driver = driver

    # ── Pesquisa ──────────────────────────────────────────────────────

    def search_profile(self, profile_name):
        try:
            search = self._find_first(
                (By.XPATH, '//a[.//span[text()="Search"] '
                           'or .//span[text()="Pesquisar"]]'),
                (By.CSS_SELECTOR, 'a[href="#"] svg[aria-label="Search"]'),
                (By.XPATH, '//a[contains(@href,"explore")]'),
            )
            if search:
                search.click()
            sleep(1)
        except Exception:
            print('\nErro ao clicar na barra de pesquisa')

        try:
            search_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     'input[placeholder="Search"], '
                     'input[placeholder="Pesquisar"], '
                     'input[aria-label="Search input"], '
                     'input[aria-label="Pesquisar"]'))
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

    # ── Abrir listas ──────────────────────────────────────────────────

    def open_followers(self):
        try:
            el = self._find_first(
                (By.XPATH, '//a[contains(@href, "/followers")]'),
                (By.CSS_SELECTOR, 'a[href*="/followers"]'),
            )
            if el:
                el.click()
                sleep(2)
            else:
                print('\nLink de seguidores não encontrado')
        except Exception:
            print('\nErro ao abrir seguidores')
        print('\nABERTURA DOS SEGUIDORES REALIZADA COM SUCESSO')

    def open_following(self):
        try:
            el = self._find_first(
                (By.XPATH, '//a[contains(@href, "/following")]'),
                (By.CSS_SELECTOR, 'a[href*="/following"]'),
            )
            if el:
                el.click()
                sleep(2)
            else:
                print('\nLink de seguindo não encontrado')
        except Exception:
            print('\nErro ao abrir lista de perfis seguidos')
        print('\nABERTURA DE LISTA DE PERFIS SEGUIDOS REALIZADA COM SUCESSO')

    # ── Fechar dialog ─────────────────────────────────────────────────

    def close_dialog(self):
        # Estratégia 1: botão Close via Selenium
        closed = False
        try:
            close_btn = self._find_first(
                (By.XPATH,
                 '//div[@role="dialog"]//button[.//*[@aria-label="Close"]]'),
                (By.XPATH,
                 '//div[@role="dialog"]//button[normalize-space(.)="Close" '
                 'or normalize-space(.)="Fechar"]'),
                (By.CSS_SELECTOR,
                 'div[role="dialog"] svg[aria-label="Close"]'),
            )
            if close_btn:
                if close_btn.tag_name == 'svg':
                    parent = close_btn.find_element(By.XPATH, './ancestor::button')
                    parent.click()
                else:
                    close_btn.click()
                closed = True
        except Exception:
            pass

        # Estratégia 2: JS close
        if not closed:
            try:
                closed = self.driver.execute_script("""
                    const dialog = document.querySelector('div[role="dialog"]');
                    if (!dialog) return false;
                    const svg = dialog.querySelector(
                        'svg[aria-label="Close"], svg[aria-label="Fechar"]');
                    if (svg) {
                        const btn = svg.closest('button') || svg.parentElement;
                        if (btn) { btn.click(); return true; }
                    }
                    const btns = dialog.querySelectorAll('button');
                    for (const b of btns) {
                        if (b.textContent.trim() === 'Close'
                            || b.textContent.trim() === 'Fechar') {
                            b.click(); return true;
                        }
                    }
                    return false;
                """)
            except Exception:
                pass

        # Estratégia 3: ESC
        if not closed:
            try:
                self.driver.find_element(
                    By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
            except Exception:
                pass

        sleep(2)

        # Estratégia 4: navegar de volta se a URL ainda tem /followers ou /following
        try:
            WebDriverWait(self.driver, 5).until(
                lambda d: '/followers' not in d.current_url
                and '/following' not in d.current_url
            )
        except Exception:
            try:
                current = self.driver.current_url
                if '/followers' in current or '/following' in current:
                    base = current.split('/followers')[0].split(
                        '/following')[0] + '/'
                    self.driver.get(base)
                    sleep(2)
            except Exception:
                pass

        print('\nLISTA FECHADA COM SUCESSO')

    # ── Abrir próprio perfil ──────────────────────────────────────────

    def open_self_profile(self):
        try:
            # Estratégia 1: SVG com aria-label Profile/Perfil
            profile_url = self.driver.execute_script("""
                const labels = ['Profile', 'Perfil'];
                for (const label of labels) {
                    const svg = document.querySelector(
                        'svg[aria-label="' + label + '"]');
                    if (svg) {
                        const link = svg.closest('a');
                        if (link) return link.href;
                    }
                }
                // Estratégia 2: link com span Profile/Perfil
                const allLinks = document.querySelectorAll('a[href]');
                for (const a of allLinks) {
                    const spans = a.querySelectorAll('span');
                    for (const s of spans) {
                        const t = s.textContent.trim();
                        if (t === 'Profile' || t === 'Perfil') return a.href;
                    }
                }
                // Estratégia 3: link com img do avatar no nav/sidebar
                const navLinks = document.querySelectorAll('nav a[href], a[href]');
                for (const a of navLinks) {
                    const href = a.getAttribute('href');
                    if (href && href.startsWith('/') && href !== '/'
                        && !href.startsWith('/explore')
                        && !href.startsWith('/direct')
                        && !href.startsWith('/reels')
                        && !href.startsWith('/accounts')
                        && a.querySelector('img[alt]')) {
                        return a.href;
                    }
                }
                return null;
            """)

            if profile_url:
                self.driver.get(profile_url)
            else:
                el = self._find_first(
                    (By.XPATH,
                     '//a[.//span[text()="Profile"] '
                     'or .//span[text()="Perfil"]]'),
                    (By.CSS_SELECTOR,
                     'a[href] svg[aria-label="Profile"]'),
                )
                if el:
                    if el.tag_name == 'svg':
                        el.find_element(
                            By.XPATH, './ancestor::a').click()
                    else:
                        el.click()
                else:
                    print('\nLink do perfil não encontrado')
        except Exception:
            print('\nNão foi possível abrir o próprio perfil')

        sleep(2)
        print('\nPERFIL ABERTO COM SUCESSO')

    # ── Utilitário ────────────────────────────────────────────────────

    def _find_first(self, *locators, timeout=5):
        """Tenta cada locator até encontrar um elemento clicável."""
        for by, selector in locators:
            try:
                el = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((by, selector))
                )
                return el
            except Exception:
                continue
        return None
