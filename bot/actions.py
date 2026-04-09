from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
from bot.exceptions import BotStoppedException


FOLLOWING_LABELS = ('Following', 'Seguindo')
UNFOLLOW_LABELS = ('Unfollow', 'Deixar de seguir')
FOLLOW_LABELS = ('Follow', 'Seguir')


class ActionHandler:
    def __init__(self, driver, stop_event=None):
        self.driver = driver
        self._stop_event = stop_event

    def _wait(self, seconds):
        """Sleep interruptível pelo stop_event."""
        if self._stop_event:
            if self._stop_event.wait(seconds):
                raise BotStoppedException()
        else:
            sleep(seconds)

    # ── Follow ────────────────────────────────────────────────────────

    def follow_users(self, max_count):
        try:
            buttons = self.driver.find_elements(
                By.XPATH, '//div[@role="dialog"]//button'
            )
            count = 0
            for btn in buttons:
                if self._stop_event and self._stop_event.is_set():
                    raise BotStoppedException()
                if count >= max_count:
                    break
                try:
                    if btn.text.strip() in FOLLOW_LABELS:
                        self._real_click(btn)
                        count += 1
                        print(f'  Seguido {count}/{max_count}')
                        self._wait(300)
                except BotStoppedException:
                    raise
                except Exception:
                    pass
        except BotStoppedException:
            raise
        except Exception:
            print('\nErro na função follow')
        print('\nPERFIS SEGUIDOS COM SUCESSO')

    # ── Unfollow ──────────────────────────────────────────────────────

    def unfollow_from_dialog(self, unfollowers):
        """Percorre o dialog e remove o follow do primeiro perfil da lista.
        Retorna o username removido ou None.
        """
        try:
            dialog = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div[role="dialog"]'))
            )

            # 1) Encontrar o botão "Following" do unfollower e clicar
            username, btn = self._find_following_button(dialog, unfollowers)
            if not username:
                return None

            print(f'  Clicando em "Following" de {username}...')
            self._real_click(btn)
            sleep(2)

            # 2) Clicar no botão "Unfollow" da confirmação
            if not self._click_unfollow_confirm():
                print(f'  Confirmação não encontrada para: {username}')
                self._dismiss_popup()
                return None

            sleep(2)

            # 3) Verificar se o unfollow funcionou
            if self._verify_unfollowed(dialog, username):
                print(f'\nRemovido o follow do perfil: {username}')
                return username

            print(f'\nUnfollow de {username} não confirmado pela verificação.')
            return None

        except Exception as e:
            print(f'\nErro ao tentar unfollow no dialog: {e}')
        return None

    def _find_following_button(self, dialog, unfollowers):
        """Encontra o botão 'Following'/'Seguindo' de um unfollower no dialog.
        Retorna (username, button_element) ou (None, None).
        """
        buttons = dialog.find_elements(By.TAG_NAME, 'button')

        for btn in buttons:
            try:
                txt = btn.text.strip()
            except Exception:
                continue
            if txt not in FOLLOWING_LABELS:
                continue

            try:
                parent = btn.find_element(
                    By.XPATH,
                    './ancestor::div[.//a[contains(@href, "/")]]')
            except Exception:
                continue

            links = parent.find_elements(By.TAG_NAME, 'a')
            for link in links:
                try:
                    href = link.get_attribute('href')
                except Exception:
                    continue
                if not href:
                    continue
                uname = href.rstrip('/').split('/')[-1]
                if uname in unfollowers:
                    return uname, btn

        return None, None

    def _click_unfollow_confirm(self):
        """Encontra e clica no botão 'Unfollow'/'Deixar de seguir'.
        Usa 3 estratégias: Selenium XPath, Selenium find_elements, ActionChains.
        """
        # Estratégia 1: XPath com normalize-space (Selenium click)
        try:
            unfollow_btn = WebDriverWait(self.driver, 8).until(
                EC.element_to_be_clickable(
                    (By.XPATH,
                     '//button[normalize-space(.)="Unfollow" '
                     'or normalize-space(.)="Deixar de seguir"]'))
            )
            sleep(0.5)
            self._real_click(unfollow_btn)
            return True
        except Exception:
            pass

        # Estratégia 2: percorrer todos os botões pelo texto visível
        try:
            all_buttons = self.driver.find_elements(By.TAG_NAME, 'button')
            for b in all_buttons:
                try:
                    txt = b.text.strip()
                except Exception:
                    continue
                if txt in UNFOLLOW_LABELS:
                    self._real_click(b)
                    return True
        except Exception:
            pass

        # Estratégia 3: JavaScript busca por textContent e dispara click nativo
        try:
            found = self.driver.execute_script("""
                const labels = arguments[0];
                const btns = document.querySelectorAll('button');
                for (const btn of btns) {
                    const t = btn.textContent.trim();
                    if (labels.includes(t)) {
                        btn.dispatchEvent(new PointerEvent('pointerdown',
                            {bubbles: true, cancelable: true}));
                        btn.dispatchEvent(new MouseEvent('mousedown',
                            {bubbles: true, cancelable: true}));
                        btn.dispatchEvent(new PointerEvent('pointerup',
                            {bubbles: true, cancelable: true}));
                        btn.dispatchEvent(new MouseEvent('mouseup',
                            {bubbles: true, cancelable: true}));
                        btn.dispatchEvent(new MouseEvent('click',
                            {bubbles: true, cancelable: true}));
                        return true;
                    }
                }
                return false;
            """, list(UNFOLLOW_LABELS))
            if found:
                return True
        except Exception:
            pass

        return False

    def _verify_unfollowed(self, dialog, username):
        """Verifica se o botão do perfil mudou de 'Following' para 'Follow'."""
        try:
            buttons = dialog.find_elements(By.TAG_NAME, 'button')
            links_in_dialog = dialog.find_elements(By.TAG_NAME, 'a')

            for link in links_in_dialog:
                try:
                    href = link.get_attribute('href')
                except Exception:
                    continue
                if not href:
                    continue
                uname = href.rstrip('/').split('/')[-1]
                if uname != username:
                    continue

                try:
                    parent = link.find_element(
                        By.XPATH,
                        './ancestor::div[.//button]')
                except Exception:
                    continue

                row_buttons = parent.find_elements(By.TAG_NAME, 'button')
                for btn in row_buttons:
                    try:
                        txt = btn.text.strip()
                    except Exception:
                        continue
                    if txt in FOLLOW_LABELS:
                        return True
                    if txt in FOLLOWING_LABELS:
                        return False
        except Exception:
            pass
        return True

    def _dismiss_popup(self):
        """Fecha qualquer popup/sheet de confirmação aberto."""
        try:
            self.driver.find_element(
                By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
        except Exception:
            pass
        sleep(1)

    def _real_click(self, element):
        """Clica com Selenium; se falhar, usa ActionChains como fallback."""
        try:
            element.click()
        except Exception:
            try:
                ActionChains(self.driver).move_to_element(
                    element).pause(0.3).click().perform()
            except Exception:
                self.driver.execute_script(
                    "arguments[0].click();", element)
