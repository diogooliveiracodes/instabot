import customtkinter as ctk
import ctypes
import json
import os
import threading
import queue
import sys
import webbrowser
import config
from bot import InstaBot, BotStoppedException
from bot import logger

ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class LogRedirector:
    """Redireciona stdout para uma fila thread-safe."""

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


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("InstaBot")
        self.geometry("640x740")
        self.resizable(False, False)
        self.iconbitmap(default="")

        self._bot = None
        self._stop_event = threading.Event()
        self._log_queue = queue.Queue()
        self._bot_thread = None

        self._build_ui()
        self._redirect_stdout()
        self._poll_log()
        self._set_idle_state()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── UI ────────────────────────────────────────────────────────────

    def _build_ui(self):
        title = ctk.CTkLabel(
            self, text="InstaBot",
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        title.pack(pady=(20, 2))

        subtitle = ctk.CTkLabel(
            self, text="Automação para Instagram",
            font=ctk.CTkFont(size=13), text_color="gray",
        )
        subtitle.pack(pady=(0, 15))

        # ── Credenciais ──
        cred_frame = ctk.CTkFrame(self)
        cred_frame.pack(fill="x", padx=30, pady=(0, 10))
        cred_frame.columnconfigure(1, weight=1)

        ctk.CTkLabel(cred_frame, text="Login", anchor="w").grid(
            row=0, column=0, padx=(15, 10), pady=(15, 5), sticky="w")
        self._login_entry = ctk.CTkEntry(
            cred_frame, placeholder_text="E-mail ou usuário")
        self._login_entry.grid(
            row=0, column=1, padx=(0, 15), pady=(15, 5), sticky="ew")
        if config.USER_LOGIN:
            self._login_entry.insert(0, config.USER_LOGIN)

        ctk.CTkLabel(cred_frame, text="Senha", anchor="w").grid(
            row=1, column=0, padx=(15, 10), pady=(5, 15), sticky="w")
        self._password_entry = ctk.CTkEntry(
            cred_frame, placeholder_text="Senha", show="•")
        self._password_entry.grid(
            row=1, column=1, padx=(0, 15), pady=(5, 15), sticky="ew")
        if config.USER_PASSWORD:
            self._password_entry.insert(0, config.USER_PASSWORD)

        # ── Ações ──
        actions_frame = ctk.CTkFrame(self)
        actions_frame.pack(fill="x", padx=30, pady=(0, 10))
        actions_frame.columnconfigure((0, 1), weight=1)

        self._btn_list = ctk.CTkButton(
            actions_frame, text="Listar não seguidores",
            height=45, command=lambda: self._start_task("list"),
        )
        self._btn_list.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")

        self._btn_unfollow = ctk.CTkButton(
            actions_frame, text="Deixar de seguir",
            height=45, command=lambda: self._start_task("unfollow"),
        )
        self._btn_unfollow.grid(row=0, column=1, padx=10, pady=(10, 5), sticky="ew")

        self._btn_farm = ctk.CTkButton(
            actions_frame, text="Ganhar seguidores",
            height=45, command=lambda: self._start_task("farm"),
        )
        self._btn_farm.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="ew")

        self._btn_stop = ctk.CTkButton(
            actions_frame, text="⏹  Parar Bot",
            height=45, fg_color="#c0392b", hover_color="#e74c3c",
            command=self._stop_bot,
        )
        self._btn_stop.grid(row=1, column=1, padx=10, pady=(5, 5), sticky="ew")

        self._btn_view_list = ctk.CTkButton(
            actions_frame, text="📋  Ver lista de não seguidores",
            height=40, fg_color="#7f8c8d", hover_color="#95a5a6",
            command=self._open_unfollowers_view,
        )
        self._btn_view_list.grid(
            row=2, column=0, columnspan=2, padx=10, pady=(5, 10), sticky="ew")

        # ── Status ──
        self._status_label = ctk.CTkLabel(
            self, text="● Aguardando",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="gray",
        )
        self._status_label.pack(pady=(5, 5))

        # ── Log ──
        log_header = ctk.CTkLabel(
            self, text="Log", anchor="w", font=ctk.CTkFont(size=13))
        log_header.pack(anchor="w", padx=30, pady=(5, 3))

        self._log_textbox = ctk.CTkTextbox(
            self, height=300, state="disabled",
            font=ctk.CTkFont(family="Consolas", size=12),
        )
        self._log_textbox.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    # ── Stdout → GUI ─────────────────────────────────────────────────

    def _redirect_stdout(self):
        self._original_stdout = sys.stdout
        sys.stdout = LogRedirector(self._log_queue, sys.__stdout__)

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

    # ── Controle de suspensão do sistema ─────────────────────────────

    @staticmethod
    def _prevent_sleep():
        ctypes.windll.kernel32.SetThreadExecutionState(
            ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
        )

    @staticmethod
    def _allow_sleep():
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)

    # ── Estados da interface ─────────────────────────────────────────

    def _set_idle_state(self):
        self._allow_sleep()
        self._btn_list.configure(state="normal")
        self._btn_unfollow.configure(state="normal")
        self._btn_farm.configure(state="normal")
        self._btn_stop.configure(state="disabled")
        self._login_entry.configure(state="normal")
        self._password_entry.configure(state="normal")
        self._status_label.configure(text="● Aguardando", text_color="gray")

    def _set_running_state(self, label):
        self._prevent_sleep()
        self._btn_list.configure(state="disabled")
        self._btn_unfollow.configure(state="disabled")
        self._btn_farm.configure(state="disabled")
        self._btn_stop.configure(state="normal")
        self._login_entry.configure(state="disabled")
        self._password_entry.configure(state="disabled")
        self._status_label.configure(text=f"● {label}", text_color="#2ecc71")

    # ── Controle do bot ──────────────────────────────────────────────

    def _start_task(self, task):
        login = self._login_entry.get().strip()
        password = self._password_entry.get().strip()

        if not login or not password:
            self._log_queue.put("⚠ Preencha login e senha antes de iniciar.")
            return

        labels = {
            "list": "Listando não seguidores...",
            "unfollow": "Removendo não seguidores...",
            "farm": "Ganhando seguidores...",
        }
        self._stop_event.clear()
        self._set_running_state(labels.get(task, "Executando..."))

        config.USER_LOGIN = login
        config.USER_PASSWORD = password

        def worker():
            log_path = logger.start_session()
            print(f"Arquivo de log: {log_path}")
            try:
                self._bot = InstaBot(stop_event=self._stop_event)
                self._bot.start()

                if task == "list":
                    self._bot.list_unfollowers()
                elif task == "unfollow":
                    self._bot.unfollow_from_list()
                elif task == "farm":
                    self._bot.farm_followers()

                print("\nOperação concluída com sucesso!")
            except BotStoppedException:
                print("\nBot parado pelo usuário.")
            except Exception as e:
                if self._stop_event.is_set():
                    print("\nBot parado pelo usuário.")
                else:
                    print(f"\nErro: {e}")
            finally:
                logger.stop_session()
                self._cleanup_bot()
                self.after(0, self._set_idle_state)

        self._bot_thread = threading.Thread(target=worker, daemon=True)
        self._bot_thread.start()

    def _stop_bot(self):
        print("\nParando o bot...")
        self._stop_event.set()
        self._status_label.configure(text="● Parando...", text_color="#e74c3c")
        self._btn_stop.configure(state="disabled")

        def force_quit():
            import time
            time.sleep(1)
            self._cleanup_bot()
            self.after(0, self._set_idle_state)

        threading.Thread(target=force_quit, daemon=True).start()

    def _cleanup_bot(self):
        if self._bot:
            try:
                self._bot.quit()
            except Exception:
                pass
            self._bot = None

    # ── Ver lista de não seguidores ──────────────────────────────────

    def _open_unfollowers_view(self):
        UnfollowersListWindow(self)

    # ── Fechar janela ────────────────────────────────────────────────

    def _on_close(self):
        self._stop_event.set()
        self._cleanup_bot()
        self._allow_sleep()
        sys.stdout = self._original_stdout
        self.destroy()


class UnfollowersListWindow(ctk.CTkToplevel):
    """Janela que exibe a lista de não-seguidores com links para o perfil."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Não Seguidores")
        self.geometry("500x600")
        self.resizable(False, True)
        self.transient(parent)
        self.after(100, self.lift)

        self._users = self._load_list()
        self._build_ui()

    def _load_list(self):
        logs_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'logs')
        json_path = os.path.join(logs_dir, 'nao-seguidores.json')
        txt_path = os.path.join(logs_dir, 'nao-seguidores.txt')

        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        if os.path.exists(txt_path):
            with open(txt_path, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        return []

    def _build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 5))

        ctk.CTkLabel(
            header, text="Não Seguidores",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(side="left")

        ctk.CTkLabel(
            header,
            text=f"{len(self._users)} perfis",
            font=ctk.CTkFont(size=14),
            text_color="gray",
        ).pack(side="right")

        if not self._users:
            ctk.CTkLabel(
                self,
                text="Nenhum não-seguidor encontrado.\n"
                     "Execute 'Listar não seguidores' primeiro.",
                font=ctk.CTkFont(size=13),
                text_color="gray",
            ).pack(expand=True)
            return

        scroll = ctk.CTkScrollableFrame(self)
        scroll.pack(fill="both", expand=True, padx=20, pady=(5, 15))
        scroll.columnconfigure(0, weight=0)
        scroll.columnconfigure(1, weight=1)
        scroll.columnconfigure(2, weight=0)

        for i, username in enumerate(self._users):
            bg = ("gray20", "gray17")[i % 2]

            num_label = ctk.CTkLabel(
                scroll, text=f"{i + 1}.",
                font=ctk.CTkFont(size=12),
                text_color="gray",
                width=40, anchor="e",
            )
            num_label.grid(row=i, column=0, padx=(5, 2), pady=2, sticky="e")

            name_label = ctk.CTkLabel(
                scroll, text=username,
                font=ctk.CTkFont(size=13),
                anchor="w",
            )
            name_label.grid(row=i, column=1, padx=(5, 5), pady=2, sticky="w")

            link_btn = ctk.CTkButton(
                scroll, text="🔗",
                width=36, height=28,
                font=ctk.CTkFont(size=14),
                fg_color="transparent",
                hover_color="gray30",
                command=lambda u=username: webbrowser.open(
                    f"https://www.instagram.com/{u}/"),
            )
            link_btn.grid(row=i, column=2, padx=(0, 5), pady=2)


def run():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    run()
