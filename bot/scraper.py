from time import sleep
from bot.exceptions import BotStoppedException


class Scraper:
    def __init__(self, driver, stop_event=None):
        self.driver = driver
        self._stop_event = stop_event

    def _scroll_and_count(self):
        """Scrolla o dialog e retorna a contagem de perfis únicos por links.
        Sempre conta por links (não por botões) para evitar subcontagem
        durante lazy loading.
        """
        return self.driver.execute_script("""
            const dialog = document.querySelector('div[role="dialog"]');
            if (!dialog) return 0;

            const divs = dialog.querySelectorAll('div');
            for (const div of divs) {
                const style = window.getComputedStyle(div);
                const ov = style.overflowY;
                if ((ov === 'auto' || ov === 'scroll' || ov === 'hidden')
                    && div.scrollHeight > div.clientHeight
                    && div.clientHeight > 50) {
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
                    && !href.startsWith('/explore')
                    && !href.startsWith('/accounts')
                    && !seen.has(href)) {
                    seen.add(href);
                    count++;
                }
            }
            return count;
        """)

    def sweep(self, only_following=False, max_iterations=None,
              save_callback=None):
        last_count = 0
        last_saved_at = 0
        try:
            sleep(2)
            stable_checks = 0
            iterations = 0
            while stable_checks < 3:
                if self._stop_event and self._stop_event.is_set():
                    raise BotStoppedException()
                count = self._scroll_and_count()
                sleep(2)
                if count == last_count:
                    stable_checks += 1
                else:
                    stable_checks = 0
                last_count = count
                iterations += 1
                if iterations % 10 == 0:
                    print(f'  Scroll: {count} perfis carregados...')

                if save_callback and (count - last_saved_at) >= 100:
                    usernames = self.get_usernames(only_following)
                    save_callback(usernames)
                    last_saved_at = count
                    print(f'  Progresso salvo: {len(usernames)} perfis')

                if max_iterations and iterations >= max_iterations:
                    print(f'  Limite de iterações atingido ({count} perfis)')
                    break
        except BotStoppedException:
            if save_callback and last_count > 0:
                usernames = self.get_usernames(only_following)
                save_callback(usernames)
                print(f'  Progresso salvo antes de parar: '
                      f'{len(usernames)} perfis')
            raise
        except Exception as e:
            if save_callback and last_count > 0:
                try:
                    usernames = self.get_usernames(only_following)
                    save_callback(usernames)
                    print(f'  Progresso salvo após erro: '
                          f'{len(usernames)} perfis')
                except Exception:
                    pass
            print(f'\nErro na função sweep: {e}')
        print(f'\nVARREDURA REALIZADA COM SUCESSO ({last_count} perfis)')
        return last_count

    def get_usernames(self, only_following=False):
        try:
            return self.driver.execute_script("""
                const onlyFollowing = arguments[0];
                const dialog = document.querySelector('div[role="dialog"]');
                if (!dialog) return [];

                const excluded = new Set([
                    '', '#', 'explore', 'accounts', 'p', 'reel',
                    'stories', 'reels', 'direct'
                ]);
                const seen = new Set();
                const usernames = [];

                if (onlyFollowing) {
                    const followingLabels = ['Following', 'Seguindo'];
                    const buttons = dialog.querySelectorAll('button');
                    for (const btn of buttons) {
                        const btnText = btn.textContent.trim();
                        if (!followingLabels.includes(btnText)) continue;

                        // Subir na árvore DOM para encontrar o container da row
                        let container = btn.parentElement;
                        for (let i = 0; i < 8 && container && container !== dialog; i++) {
                            const links = container.querySelectorAll('a[href]');
                            if (links.length > 0) {
                                for (const a of links) {
                                    const href = a.getAttribute('href');
                                    if (!href) continue;
                                    const parts = href.replace(/\\/+$/, '').split('/');
                                    const username = parts[parts.length - 1];
                                    if (username && !seen.has(username)
                                        && !excluded.has(username)) {
                                        seen.add(username);
                                        usernames.push(username);
                                    }
                                }
                                break;
                            }
                            container = container.parentElement;
                        }
                    }
                } else {
                    const links = dialog.querySelectorAll('a[href]');
                    for (const a of links) {
                        const href = a.getAttribute('href');
                        if (!href) continue;
                        const parts = href.replace(/\\/+$/, '').split('/');
                        const username = parts[parts.length - 1];
                        if (username && !seen.has(username)
                            && !excluded.has(username)) {
                            seen.add(username);
                            usernames.push(username);
                        }
                    }
                }
                return usernames;
            """, only_following)
        except Exception as e:
            print(f'\nErro ao extrair usernames: {e}')
            return []
