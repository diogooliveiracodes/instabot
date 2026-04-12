import customtkinter as ctk
import ctypes
import json
import os
import threading
import queue
import sys
import webbrowser
from bot import InstaBot, BotStoppedException
from bot import logger
from bot import profiles

ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class LogRedirector:
    def __init__(self, log_queue, original):
        self._queue = log_queue
        self._original = original

    def write(self, text):
        if text and text.strip():
            self._queue.put(text.rstrip("\n"))
            logger.log(text.strip())
        if self._original:
            self._original.write(text)

    def flush(self):
        if self._original:
            self._original.flush()


# ══════════════════════════════════════════════════════════════════════
#  Tela de Seleção de Perfil
# ══════════════════════════════════════════════════════════════════════

class LoginScreen(ctk.CTkFrame):
    """Tela inicial para selecionar perfil salvo ou entrar com novas
    credenciais."""

    def __init__(self, master, on_profile_selected):
        super().__init__(master)
        self._on_profile_selected = on_profile_selected
        self._build_ui()

    def _build_ui(self):
        ctk.CTkLabel(
            self, text="InstaBot",
            font=ctk.CTkFont(size=28, weight="bold"),
        ).pack(pady=(30, 2))

        ctk.CTkLabel(
            self, text="Selecione um perfil ou faça login",
            font=ctk.CTkFont(size=13), text_color="gray",
        ).pack(pady=(0, 20))

        # ── Perfis salvos ──
        saved = profiles.load_profiles()
        if saved:
            ctk.CTkLabel(
                self, text="Perfis salvos",
                font=ctk.CTkFont(size=14, weight="bold"),
                anchor="w",
            ).pack(anchor="w", padx=40, pady=(0, 5))

            profiles_frame = ctk.CTkFrame(self)
            profiles_frame.pack(fill="x", padx=30, pady=(0, 15))

            for p in saved:
                row = ctk.CTkFrame(profiles_frame, fg_color="transparent")
                row.pack(fill="x", padx=10, pady=4)

                ctk.CTkButton(
                    row,
                    text=f"@{p['username']}",
                    height=40,
                    anchor="w",
                    font=ctk.CTkFont(size=14),
                    command=lambda pr=p: self._select_saved(pr),
                ).pack(side="left", fill="x", expand=True, padx=(0, 5))

                ctk.CTkButton(
                    row, text="✕", width=40, height=40,
                    fg_color="#c0392b", hover_color="#e74c3c",
                    command=lambda pr=p: self._delete_profile(pr),
                ).pack(side="right")

            separator = ctk.CTkFrame(self, height=2, fg_color="gray30")
            separator.pack(fill="x", padx=40, pady=(0, 15))

        # ── Novo login ──
        ctk.CTkLabel(
            self, text="Novo login",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        ).pack(anchor="w", padx=40, pady=(0, 5))

        login_frame = ctk.CTkFrame(self)
        login_frame.pack(fill="x", padx=30, pady=(0, 10))
        login_frame.columnconfigure(1, weight=1)

        ctk.CTkLabel(login_frame, text="Login", anchor="w").grid(
            row=0, column=0, padx=(15, 10), pady=(15, 5), sticky="w")
        self._login_entry = ctk.CTkEntry(
            login_frame, placeholder_text="E-mail ou usuário")
        self._login_entry.grid(
            row=0, column=1, padx=(0, 15), pady=(15, 5), sticky="ew")

        ctk.CTkLabel(login_frame, text="Senha", anchor="w").grid(
            row=1, column=0, padx=(15, 10), pady=(5, 15), sticky="w")
        self._password_entry = ctk.CTkEntry(
            login_frame, placeholder_text="Senha", show="•")
        self._password_entry.grid(
            row=1, column=1, padx=(0, 15), pady=(5, 15), sticky="ew")

        self._btn_login = ctk.CTkButton(
            self, text="Entrar",
            height=45, font=ctk.CTkFont(size=15, weight="bold"),
            command=self._new_login,
        )
        self._btn_login.pack(padx=30, pady=(5, 30), fill="x")

        self._status = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=12), text_color="#e74c3c")
        self._status.pack(pady=(0, 10))

    def _select_saved(self, profile):
        self._on_profile_selected(
            profile['login'], profile['password'], profile['username'])

    def _delete_profile(self, profile):
        profiles.remove_profile(profile['username'])
        self._refresh()

    def _new_login(self):
        login = self._login_entry.get().strip()
        password = self._password_entry.get().strip()
        if not login or not password:
            self._status.configure(
                text="Preencha login e senha.", text_color="#e74c3c")
            return

        self._status.configure(
            text="Fazendo login e detectando perfil...",
            text_color="#2ecc71")
        self._btn_login.configure(state="disabled")

        self._on_profile_selected(login, password, None)

    def _refresh(self):
        for w in self.winfo_children():
            w.destroy()
        self._build_ui()


# ══════════════════════════════════════════════════════════════════════
#  Tela Principal
# ══════════════════════════════════════════════════════════════════════

class MainScreen(ctk.CTkFrame):
    """Tela principal com ações do bot, log e status."""

    def __init__(self, master, login, password, username, profile_dir,
                 on_logout):
        super().__init__(master)
        self._login = login
        self._password = password
        self._username = username
        self._profile_dir = profile_dir
        self._on_logout = on_logout

        self._bot = None
        self._stop_event = threading.Event()
        self._log_queue = queue.Queue()
        self._bot_thread = None

        self._build_ui()
        self._poll_log()
        self._set_idle_state()

    def _build_ui(self):
        # ── Cabeçalho ──
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(15, 5))

        ctk.CTkLabel(
            header, text=f"@{self._username}",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).pack(side="left")

        ctk.CTkButton(
            header, text="Trocar perfil", width=110, height=32,
            fg_color="gray30", hover_color="gray40",
            font=ctk.CTkFont(size=12),
            command=self._on_logout,
        ).pack(side="right")

        # ── Ações ──
        actions_frame = ctk.CTkFrame(self)
        actions_frame.pack(fill="x", padx=30, pady=(10, 5))
        actions_frame.columnconfigure((0, 1), weight=1)

        self._btn_list = ctk.CTkButton(
            actions_frame, text="Listar não seguidores",
            height=45, command=lambda: self._start_task("list"),
        )
        self._btn_list.grid(
            row=0, column=0, padx=10, pady=(10, 5), sticky="ew")

        self._btn_unfollow = ctk.CTkButton(
            actions_frame, text="Deixar de seguir",
            height=45, command=lambda: self._start_task("unfollow"),
        )
        self._btn_unfollow.grid(
            row=0, column=1, padx=10, pady=(10, 5), sticky="ew")

        self._btn_farm = ctk.CTkButton(
            actions_frame, text="Ganhar seguidores",
            height=45, command=lambda: self._start_task("farm"),
        )
        self._btn_farm.grid(
            row=1, column=0, padx=10, pady=(5, 5), sticky="ew")

        self._btn_stop = ctk.CTkButton(
            actions_frame, text="⏹  Parar Bot",
            height=45, fg_color="#c0392b", hover_color="#e74c3c",
            command=self._stop_bot,
        )
        self._btn_stop.grid(
            row=1, column=1, padx=10, pady=(5, 5), sticky="ew")

        self._btn_view_list = ctk.CTkButton(
            actions_frame, text="📋  Ver não seguidores",
            height=40, fg_color="#7f8c8d", hover_color="#95a5a6",
            command=self._open_unfollowers_view,
        )
        self._btn_view_list.grid(
            row=2, column=0, padx=10, pady=(5, 5), sticky="ew")

        self._btn_lost = ctk.CTkButton(
            actions_frame, text="👤  Quem parou de seguir",
            height=40, fg_color="#8e44ad", hover_color="#9b59b6",
            command=self._open_lost_followers_view,
        )
        self._btn_lost.grid(
            row=2, column=1, padx=10, pady=(5, 5), sticky="ew")

        # ── Status ──
        self._status_label = ctk.CTkLabel(
            self, text="● Aguardando",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="gray",
        )
        self._status_label.pack(pady=(5, 5))

        # ── Log ──
        ctk.CTkLabel(
            self, text="Log", anchor="w", font=ctk.CTkFont(size=13),
        ).pack(anchor="w", padx=30, pady=(5, 3))

        self._log_textbox = ctk.CTkTextbox(
            self, height=280, state="disabled",
            font=ctk.CTkFont(family="Consolas", size=12),
        )
        self._log_textbox.pack(
            fill="both", expand=True, padx=30, pady=(0, 15))

    def _poll_log(self):
        try:
            while True:
                msg = self._log_queue.get_nowait()
                self._log_textbox.configure(state="normal")
                self._log_textbox.insert("end", msg + "\n")
                self._log_textbox.see("end")
                self._log_textbox.configure(state="disabled")
        except queue.Empty:
            pass
        self.after(100, self._poll_log)

    # ── Estados ───────────────────────────────────────────────────────

    def _set_idle_state(self):
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
        self._btn_list.configure(state="normal")
        self._btn_unfollow.configure(state="normal")
        self._btn_farm.configure(state="normal")
        self._btn_stop.configure(state="disabled")
        has_followers = os.path.exists(
            os.path.join(self._profile_dir, 'seguidores.json'))
        self._btn_lost.configure(
            state="normal" if has_followers else "disabled")
        self._status_label.configure(
            text="● Aguardando", text_color="gray")

    def _set_running_state(self, label):
        ctypes.windll.kernel32.SetThreadExecutionState(
            ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED)
        self._btn_list.configure(state="disabled")
        self._btn_unfollow.configure(state="disabled")
        self._btn_farm.configure(state="disabled")
        self._btn_stop.configure(state="normal")
        self._status_label.configure(
            text=f"● {label}", text_color="#2ecc71")

    # ── Controle do bot ───────────────────────────────────────────────

    def _start_task(self, task):
        labels = {
            "list": "Listando não seguidores...",
            "unfollow": "Removendo não seguidores...",
            "farm": "Ganhando seguidores...",
            "lost": "Verificando quem parou de seguir...",
        }
        self._stop_event.clear()
        self._set_running_state(labels.get(task, "Executando..."))

        max_retries = 3

        def worker():
            import traceback
            logger.set_profile_dir(self._profile_dir)

            for attempt in range(1, max_retries + 1):
                if self._stop_event.is_set():
                    break

                log_path = logger.start_session()
                print(f"Arquivo de log: {log_path}")
                if attempt > 1:
                    print(f"--- Tentativa {attempt}/{max_retries} ---")

                bot = None
                try:
                    bot = InstaBot(
                        login=self._login,
                        password=self._password,
                        profile_dir=self._profile_dir,
                        stop_event=self._stop_event,
                    )
                    self._bot = bot
                    bot.start()

                    if task == "list":
                        bot.list_unfollowers()
                    elif task == "unfollow":
                        bot.unfollow_from_list()
                    elif task == "farm":
                        bot.farm_followers()
                    elif task == "lost":
                        bot.check_lost_followers()

                    print("\nOperação concluída com sucesso!")
                    logger.stop_session()
                    break

                except BotStoppedException:
                    print("\nBot parado pelo usuário.")
                    logger.stop_session()
                    break

                except Exception as e:
                    tb = traceback.format_exc()
                    if self._stop_event.is_set():
                        print("\nBot parado pelo usuário.")
                        logger.stop_session()
                        break

                    print(f"\nErro (tentativa {attempt}/{max_retries}): "
                          f"{e}\n{tb}")
                    logger.stop_session()

                    if bot:
                        try:
                            bot.quit()
                        except Exception:
                            pass
                        bot = None
                        self._bot = None

                    if attempt < max_retries:
                        print(f"\nReiniciando em 5 segundos...")
                        import time
                        time.sleep(5)
                    else:
                        print(f"\n{max_retries} tentativas falharam. "
                              "Encerrando.")

            if bot:
                try:
                    bot.quit()
                except Exception:
                    pass
            self._bot = None
            self.after(0, self._set_idle_state)

        self._bot_thread = threading.Thread(target=worker, daemon=True)
        self._bot_thread.start()

    def _stop_bot(self):
        self._log_queue.put("Parando o bot...")
        self._stop_event.set()
        self._status_label.configure(
            text="● Parando...", text_color="#e74c3c")
        self._btn_stop.configure(state="disabled")

        def force_quit():
            import time
            time.sleep(1)
            self._cleanup_bot()
            self.after(0, self._set_idle_state)

        threading.Thread(target=force_quit, daemon=True).start()

    def _cleanup_bot(self):
        bot = self._bot
        self._bot = None
        if bot:
            try:
                bot.quit()
            except Exception:
                pass

    # ── Ver listas ────────────────────────────────────────────────────

    def _open_unfollowers_view(self):
        UnfollowersListWindow(self.winfo_toplevel(), self._profile_dir)

    def _open_lost_followers_view(self):
        LostFollowersWindow(
            self.winfo_toplevel(), self._profile_dir,
            self._login, self._password, self._stop_event,
            self._log_queue)


# ══════════════════════════════════════════════════════════════════════
#  Janela de Lista de Não Seguidores
# ══════════════════════════════════════════════════════════════════════

class UnfollowersListWindow(ctk.CTkToplevel):
    def __init__(self, parent, profile_dir):
        super().__init__(parent)
        self.title("Não Seguidores")
        self.geometry("500x600")
        self.resizable(False, True)
        self.transient(parent)
        self.after(100, self.lift)

        self._profile_dir = profile_dir
        self._users = self._load_list()
        self._build_ui()

    def _load_list(self):
        path = os.path.join(self._profile_dir, 'nao-seguidores.json')
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def _build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 5))

        ctk.CTkLabel(
            header, text="Não Seguidores",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(side="left")

        ctk.CTkLabel(
            header, text=f"{len(self._users)} perfis",
            font=ctk.CTkFont(size=14), text_color="gray",
        ).pack(side="right")

        if not self._users:
            ctk.CTkLabel(
                self,
                text="Nenhum não-seguidor encontrado.\n"
                     "Execute 'Listar não seguidores' primeiro.",
                font=ctk.CTkFont(size=13), text_color="gray",
            ).pack(expand=True)
            return

        scroll = ctk.CTkScrollableFrame(self)
        scroll.pack(fill="both", expand=True, padx=20, pady=(5, 15))
        scroll.columnconfigure(1, weight=1)

        for i, username in enumerate(self._users):
            ctk.CTkLabel(
                scroll, text=f"{i + 1}.",
                font=ctk.CTkFont(size=12), text_color="gray",
                width=40, anchor="e",
            ).grid(row=i, column=0, padx=(5, 2), pady=2, sticky="e")

            ctk.CTkLabel(
                scroll, text=username,
                font=ctk.CTkFont(size=13), anchor="w",
            ).grid(row=i, column=1, padx=(5, 5), pady=2, sticky="w")

            ctk.CTkButton(
                scroll, text="🔗", width=36, height=28,
                font=ctk.CTkFont(size=14),
                fg_color="transparent", hover_color="gray30",
                command=lambda u=username: webbrowser.open(
                    f"https://www.instagram.com/{u}/"),
            ).grid(row=i, column=2, padx=(0, 5), pady=2)


# ══════════════════════════════════════════════════════════════════════
#  Janela de Quem Parou de Seguir
# ══════════════════════════════════════════════════════════════════════

class LostFollowersWindow(ctk.CTkToplevel):
    def __init__(self, parent, profile_dir, login, password,
                 stop_event, log_queue):
        super().__init__(parent)
        self.title("Quem parou de seguir")
        self.geometry("550x650")
        self.resizable(False, True)
        self.transient(parent)
        self.after(100, self.lift)

        self._profile_dir = profile_dir
        self._login = login
        self._password = password
        self._stop_event = stop_event
        self._log_queue = log_queue
        self._entries = self._load_lost()
        self._build_ui()

    def _load_lost(self):
        path = os.path.join(self._profile_dir, 'perdidos.json')
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, ValueError):
                return []
        return []

    def _build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 5))

        ctk.CTkLabel(
            header, text="Quem parou de seguir",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(side="left")

        ctk.CTkLabel(
            header, text=f"{len(self._entries)} perfis",
            font=ctk.CTkFont(size=14), text_color="gray",
        ).pack(side="right")

        self._btn_check = ctk.CTkButton(
            self, text="🔄  Verificar agora",
            height=40, fg_color="#8e44ad", hover_color="#9b59b6",
            command=self._run_check,
        )
        self._btn_check.pack(fill="x", padx=20, pady=(10, 5))

        self._status = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=12), text_color="gray")
        self._status.pack(pady=(0, 5))

        self._scroll_frame = ctk.CTkFrame(self)
        self._scroll_frame.pack(fill="both", expand=True, padx=20,
                                pady=(0, 15))
        self._render_list()

    def _render_list(self):
        for w in self._scroll_frame.winfo_children():
            w.destroy()

        if not self._entries:
            ctk.CTkLabel(
                self._scroll_frame,
                text="Nenhum seguidor perdido registrado.\n"
                     "Clique em 'Verificar agora' para escanear.",
                font=ctk.CTkFont(size=13), text_color="gray",
            ).pack(expand=True, pady=30)
            return

        scroll = ctk.CTkScrollableFrame(self._scroll_frame)
        scroll.pack(fill="both", expand=True)
        scroll.columnconfigure(1, weight=1)

        sorted_entries = sorted(
            self._entries, key=lambda e: e.get('lost_at', ''),
            reverse=True)

        for i, entry in enumerate(sorted_entries):
            uname = entry.get('username', '?')
            date = entry.get('lost_at', '')

            ctk.CTkLabel(
                scroll, text=f"{i + 1}.",
                font=ctk.CTkFont(size=12), text_color="gray",
                width=35, anchor="e",
            ).grid(row=i, column=0, padx=(5, 2), pady=2, sticky="e")

            ctk.CTkLabel(
                scroll, text=uname,
                font=ctk.CTkFont(size=13), anchor="w",
            ).grid(row=i, column=1, padx=(5, 0), pady=2, sticky="w")

            ctk.CTkLabel(
                scroll, text=date,
                font=ctk.CTkFont(size=11), text_color="gray",
                anchor="e",
            ).grid(row=i, column=2, padx=(5, 2), pady=2, sticky="e")

            ctk.CTkButton(
                scroll, text="🔗", width=36, height=28,
                font=ctk.CTkFont(size=14),
                fg_color="transparent", hover_color="gray30",
                command=lambda u=uname: webbrowser.open(
                    f"https://www.instagram.com/{u}/"),
            ).grid(row=i, column=3, padx=(0, 5), pady=2)

    def _run_check(self):
        self._btn_check.configure(state="disabled")
        self._status.configure(
            text="Abrindo navegador e verificando...", text_color="#2ecc71")

        def worker():
            try:
                self._stop_event.clear()
                logger.set_profile_dir(self._profile_dir)
                log_path = logger.start_session()
                print(f"Arquivo de log: {log_path}")

                bot = InstaBot(
                    login=self._login,
                    password=self._password,
                    profile_dir=self._profile_dir,
                    stop_event=self._stop_event,
                )
                bot.start()
                lost = bot.check_lost_followers()
                bot.quit()

                logger.stop_session()
                self._entries = lost
                self.after(0, self._on_check_done)
            except BotStoppedException:
                print("\nBot parado pelo usuário.")
                self.after(0, self._on_check_done)
            except Exception as e:
                print(f"\nErro: {e}")
                self.after(0, self._on_check_done)

        threading.Thread(target=worker, daemon=True).start()

    def _on_check_done(self):
        self._btn_check.configure(state="normal")
        self._status.configure(
            text=f"Concluído — {len(self._entries)} perdidos registrados",
            text_color="gray")
        self._render_list()


# ══════════════════════════════════════════════════════════════════════
#  App Principal (gerencia telas)
# ══════════════════════════════════════════════════════════════════════

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("InstaBot")
        self.geometry("640x740")
        self.resizable(False, False)
        self.iconbitmap(default="")

        self._log_queue = queue.Queue()
        self._original_stdout = sys.stdout
        sys.stdout = LogRedirector(self._log_queue, sys.__stdout__)

        self._current_screen = None
        self._show_login()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _show_login(self):
        if self._current_screen:
            self._current_screen.destroy()
        self._current_screen = LoginScreen(
            self, on_profile_selected=self._on_profile_selected)
        self._current_screen.pack(fill="both", expand=True)

    def _on_profile_selected(self, login, password, username):
        if username:
            profile_dir = profiles.get_profile_dir(username)
            self._show_main(login, password, username, profile_dir)
        else:
            self._detect_and_show(login, password)

    def _detect_and_show(self, login, password):
        """Faz login no Instagram para capturar o username e depois mostra
        a tela principal."""
        def worker():
            try:
                from bot.browser import BrowserManager
                from bot.navigation import Navigator
                import config

                print("Fazendo login para detectar o perfil...")
                bm = BrowserManager()
                driver = bm.setup(config.INSTAGRAM_URL)
                bm.login(login, password)
                import time
                time.sleep(5)
                bm.dismiss_popups()
                time.sleep(2)

                nav = Navigator(driver)
                url = driver.execute_script("""
                    const labels = ['Profile', 'Perfil'];
                    for (const l of labels) {
                        const svg = document.querySelector(
                            'svg[aria-label="' + l + '"]');
                        if (svg) {
                            const a = svg.closest('a');
                            if (a) return a.href;
                        }
                    }
                    const all = document.querySelectorAll('a[href]');
                    for (const a of all) {
                        const spans = a.querySelectorAll('span');
                        for (const s of spans) {
                            const t = s.textContent.trim();
                            if (t === 'Profile' || t === 'Perfil')
                                return a.href;
                        }
                    }
                    return null;
                """)

                detected = None
                if url:
                    detected = url.rstrip('/').split('/')[-1]

                if not detected:
                    nav.open_self_profile()
                    time.sleep(2)
                    detected = driver.current_url.rstrip('/').split('/')[-1]

                bm.quit()

                if detected:
                    print(f"Perfil detectado: @{detected}")
                    profiles.save_profile(login, password, detected)
                    profile_dir = profiles.get_profile_dir(detected)
                    self.after(0, lambda: self._show_main(
                        login, password, detected, profile_dir))
                else:
                    print("Não foi possível detectar o perfil.")
                    self.after(0, self._show_login)

            except Exception as e:
                print(f"Erro na detecção: {e}")
                self.after(0, self._show_login)

        threading.Thread(target=worker, daemon=True).start()

    def _show_main(self, login, password, username, profile_dir):
        if self._current_screen:
            self._current_screen.destroy()
        self._current_screen = MainScreen(
            self, login, password, username, profile_dir,
            on_logout=self._show_login)
        self._current_screen.pack(fill="both", expand=True)

    def _on_close(self):
        if isinstance(self._current_screen, MainScreen):
            self._current_screen._cleanup_bot()
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
        sys.stdout = self._original_stdout
        self.destroy()


def run():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    run()
