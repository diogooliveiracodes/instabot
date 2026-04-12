from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
from bot.exceptions import BotStoppedException


FOLLOWING_LABELS = ('Following', 'Seguindo')
UNFOLLOW_LABELS = ('Unfollow', 'Deixar de seguir', 'Parar de seguir')
FOLLOW_LABELS = ('Follow', 'Seguir')

MODAL_HINTS = (
    'Unfollow', 'Deixar de seguir', 'Parar de seguir',
    'Mute', 'Silenciar', 'Restrict', 'Restringir',
    'Add to close friends', 'Adicionar à lista',
    'Add to favorites', 'Adicionar aos Favoritos',
)


class ActionHandler:
    def __init__(self, driver, stop_event=None):
        self.driver = driver
        self._stop_event = stop_event

    def _wait(self, seconds):
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

    # ── Unfollow (via página do perfil) ───────────────────────────────

    def unfollow_profile(self, username, unfollowers_list):
        if username not in unfollowers_list:
            print(f'  BLOQUEADO: {username} não está na lista. Pulando.')
            return False

        profile_url = f'https://www.instagram.com/{username}/'
        print(f'\n  Abrindo perfil: {profile_url}')

        try:
            self.driver.get(profile_url)
            sleep(4)

            following_btn = self._find_following_button_on_profile()
            if not following_btn:
                print(f'  Botão "Following"/"Seguindo" não encontrado em '
                      f'{username}. Pode já ter sido removido.')
                return False

            if not self._open_unfollow_modal(following_btn):
                print(f'  Modal não abriu para {username}.')
                return False

            if not self._click_unfollow_in_modal():
                print(f'  "Deixar de seguir" não encontrado para {username}.')
                self._dismiss_popup()
                return False

            sleep(2)

            if self._verify_unfollowed_on_profile():
                print(f'  Removido o follow do perfil: {username}')
                return True

            print(f'  Unfollow de {username} não confirmado.')
            return False

        except Exception as e:
            print(f'  Erro ao tentar unfollow de {username}: {e}')
            return False

    # ── Encontrar botão Following ─────────────────────────────────────

    def _find_following_button_on_profile(self):
        for label in FOLLOWING_LABELS:
            try:
                btn = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable(
                        (By.XPATH,
                         f'//button[contains(normalize-space(.), "{label}")]'))
                )
                txt = btn.text.strip()
                if any(l in txt for l in FOLLOWING_LABELS):
                    print(f'  Botão encontrado: "{txt}"')
                    return btn
            except Exception:
                continue

        try:
            btn = self.driver.execute_script("""
                const labels = arguments[0];
                const btns = document.querySelectorAll('button');
                for (const b of btns) {
                    const t = b.textContent.trim();
                    for (const l of labels) {
                        if (t.includes(l)) return b;
                    }
                }
                return null;
            """, list(FOLLOWING_LABELS))
            if btn:
                print(f'  Botão encontrado (JS): "{btn.text.strip()}"')
                return btn
        except Exception:
            pass

        return None

    # ── Abrir modal e verificar ───────────────────────────────────────

    def _open_unfollow_modal(self, following_btn):
        """Clica no botão Following UMA vez e espera o modal aparecer.
        Se não abrir, tenta outros métodos de click (sem re-clicar).
        """
        click_methods = [
            lambda: following_btn.click(),
            lambda: ActionChains(self.driver).move_to_element(
                following_btn).pause(0.5).click().perform(),
            lambda: self.driver.execute_script("""
                const btn = arguments[0];
                btn.dispatchEvent(new PointerEvent('pointerdown',
                    {bubbles:true, cancelable:true}));
                btn.dispatchEvent(new MouseEvent('mousedown',
                    {bubbles:true, cancelable:true}));
                btn.dispatchEvent(new PointerEvent('pointerup',
                    {bubbles:true, cancelable:true}));
                btn.dispatchEvent(new MouseEvent('mouseup',
                    {bubbles:true, cancelable:true}));
                btn.dispatchEvent(new MouseEvent('click',
                    {bubbles:true, cancelable:true}));
            """, following_btn),
        ]

        for i, click_fn in enumerate(click_methods):
            try:
                click_fn()
                print(f'  Click executado (método {i + 1}/3)')
            except Exception as e:
                print(f'  Click falhou (método {i + 1}): {e}')
                continue

            for wait in range(6):
                sleep(1)
                if self._is_modal_open():
                    print(f'  Modal detectado após {wait + 1}s')
                    return True

            print(f'  Modal não detectado. Fechando possível estado '
                  f'intermediário...')
            self._dismiss_popup()
            sleep(1)

        return False

    def _is_modal_open(self):
        """Detecta o modal buscando QUALQUER elemento com texto das opções.
        Usa JS textContent para máxima confiabilidade.
        """
        try:
            return self.driver.execute_script("""
                const hints = arguments[0];
                const all = document.querySelectorAll('*');
                for (const el of all) {
                    if (el.children.length > 0) continue;
                    const t = el.textContent.trim();
                    if (!t || t.length > 60) continue;
                    for (const hint of hints) {
                        if (t === hint) return true;
                    }
                }
                return false;
            """, list(MODAL_HINTS))
        except Exception:
            return False

    # ── Clicar em Unfollow no modal ───────────────────────────────────

    def _click_unfollow_in_modal(self):
        """Encontra e clica no botão/elemento 'Deixar de seguir'/'Unfollow'.
        Busca qualquer elemento clicável com o texto correto.
        """
        # Estratégia 1: JS - busca TODOS os elementos (não só button)
        try:
            clicked = self.driver.execute_script("""
                const labels = arguments[0];
                const all = document.querySelectorAll('*');
                for (const el of all) {
                    const t = el.textContent.trim();
                    for (const label of labels) {
                        if (t === label) {
                            const clickable = el.closest(
                                'button, [role="button"], [role="menuitem"], a'
                            ) || el;
                            clickable.click();
                            return t;
                        }
                    }
                }
                return null;
            """, list(UNFOLLOW_LABELS))
            if clicked:
                print(f'  Confirmação clicada (JS): "{clicked}"')
                return True
        except Exception:
            pass

        # Estratégia 2: XPath normalize-space para cada label
        for label in UNFOLLOW_LABELS:
            try:
                btn = self.driver.find_element(
                    By.XPATH,
                    f'//*[normalize-space(.)="{label}"]')
                print(f'  Confirmação encontrada (XPath): '
                      f'"{btn.text.strip()}"')
                self._real_click(btn)
                return True
            except Exception:
                continue

        # Estratégia 3: Selenium find_elements em buttons
        try:
            buttons = self.driver.find_elements(By.TAG_NAME, 'button')
            for btn in buttons:
                try:
                    txt = btn.text.strip()
                except Exception:
                    continue
                if txt in UNFOLLOW_LABELS:
                    print(f'  Confirmação encontrada (button): "{txt}"')
                    self._real_click(btn)
                    return True
        except Exception:
            pass

        # Estratégia 4: Selenium find_elements em divs
        try:
            divs = self.driver.find_elements(By.TAG_NAME, 'div')
            for div in divs:
                try:
                    txt = div.text.strip()
                except Exception:
                    continue
                if txt in UNFOLLOW_LABELS:
                    print(f'  Confirmação encontrada (div): "{txt}"')
                    self._real_click(div)
                    return True
        except Exception:
            pass

        # Diagnóstico
        self._debug_visible_elements()
        return False

    def _debug_visible_elements(self):
        try:
            info = self.driver.execute_script("""
                const result = [];
                const all = document.querySelectorAll(
                    'button, [role="button"], [role="menuitem"], div[tabindex]'
                );
                for (const el of all) {
                    const t = el.textContent.trim();
                    if (t && t.length > 0 && t.length < 80) {
                        result.push(el.tagName + ': "' + t.substring(0, 50) + '"');
                    }
                }
                return result.slice(-20);
            """)
            print(f'  [DEBUG] Últimos 20 elementos interativos:')
            for line in info:
                print(f'    {line}')
        except Exception:
            pass

    # ── Verificação ───────────────────────────────────────────────────

    def _verify_unfollowed_on_profile(self):
        try:
            buttons = self.driver.find_elements(By.TAG_NAME, 'button')
            for btn in buttons:
                try:
                    txt = btn.text.strip()
                except Exception:
                    continue
                if txt in FOLLOW_LABELS:
                    return True
                if any(l in txt for l in FOLLOWING_LABELS):
                    return False
        except Exception:
            pass
        return True

    # ── Utilitários ───────────────────────────────────────────────────

    def _dismiss_popup(self):
        try:
            self.driver.find_element(
                By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
        except Exception:
            pass
        sleep(1)

    def _real_click(self, element):
        try:
            element.click()
        except Exception:
            try:
                ActionChains(self.driver).move_to_element(
                    element).pause(0.3).click().perform()
            except Exception:
                self.driver.execute_script(
                    "arguments[0].click();", element)
