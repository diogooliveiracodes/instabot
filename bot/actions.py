from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep


class ActionHandler:
    def __init__(self, driver):
        self.driver = driver

    def follow_users(self, max_count):
        try:
            buttons = self.driver.find_elements(
                By.XPATH, '//div[@role="dialog"]//button'
            )
            count = 0
            for btn in buttons:
                if count >= max_count:
                    break
                try:
                    if btn.text.strip() in ('Follow', 'Seguir'):
                        btn.click()
                        count += 1
                        sleep(300)
                except Exception:
                    pass
        except Exception:
            print('\nErro na função follow')
        print('\nPERFIS SEGUIDOS COM SUCESSO')

    def unfollow_from_dialog(self, unfollowers):
        """Percorre o dialog e remove o follow do primeiro perfil da lista.
        Retorna o username removido ou None.
        """
        try:
            dialog = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div[role="dialog"]'))
            )
            buttons = dialog.find_elements(By.TAG_NAME, 'button')

            for btn in buttons:
                if btn.text.strip() not in ('Following', 'Seguindo'):
                    continue

                parent = btn.find_element(
                    By.XPATH, './ancestor::div[.//a[contains(@href, "/")]]')
                links = parent.find_elements(By.TAG_NAME, 'a')

                for link in links:
                    href = link.get_attribute('href')
                    if not href:
                        continue
                    username = href.rstrip('/').split('/')[-1]
                    if username not in unfollowers:
                        continue

                    btn.click()
                    sleep(1)
                    unfollow_btn = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable(
                            (By.XPATH,
                             '//button[text()="Unfollow" '
                             'or text()="Deixar de seguir"]'))
                    )
                    sleep(1)
                    unfollow_btn.click()
                    print(f'\nRemovido o follow do perfil: {username}')
                    sleep(300)
                    return username

        except Exception:
            print('\nErro ao tentar unfollow no dialog')
        return None
