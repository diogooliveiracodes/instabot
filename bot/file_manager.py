import json
import os
from datetime import datetime


class FileManager:
    UNFOLLOWERS_FILE = 'nao-seguidores.json'
    REMOVED_FILE = 'removidos.json'

    def __init__(self, profile_dir):
        self._profile_dir = profile_dir
        os.makedirs(self._profile_dir, exist_ok=True)

    @property
    def unfollowers_path(self):
        return os.path.join(self._profile_dir, self.UNFOLLOWERS_FILE)

    @property
    def removed_path(self):
        return os.path.join(self._profile_dir, self.REMOVED_FILE)

    # ── nao-seguidores.json ──────────────────────────────────────────

    def save_unfollowers(self, unfollowers):
        with open(self.unfollowers_path, 'w', encoding='utf-8') as f:
            json.dump(unfollowers, f, ensure_ascii=False, indent=2)
        print(f'\nLista salva em: {self.unfollowers_path} '
              f'({len(unfollowers)} perfis)')

    def load_unfollowers(self):
        if not os.path.exists(self.unfollowers_path):
            print(f'\nArquivo {self.unfollowers_path} não encontrado.')
            print('Execute a opção "Listar não seguidores" primeiro.')
            return []

        with open(self.unfollowers_path, 'r', encoding='utf-8') as f:
            users = json.load(f)
        print(f'\nLista de não-seguidores carregada: {len(users)} perfis')
        return users

    # ── removidos.json ───────────────────────────────────────────────

    def append_removed(self, username):
        entries = self._load_removed()
        entries.append({
            'username': username,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        with open(self.removed_path, 'w', encoding='utf-8') as f:
            json.dump(entries, f, ensure_ascii=False, indent=2)

    def _load_removed(self):
        if not os.path.exists(self.removed_path):
            return []
        try:
            with open(self.removed_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, ValueError):
            return []

    # ── Operação composta ────────────────────────────────────────────

    def process_removal(self, username, unfollowers):
        if username not in unfollowers:
            print(f'  AVISO: {username} não está na lista. Remoção ignorada.')
            return unfollowers
        self.append_removed(username)
        unfollowers.remove(username)
        self.save_unfollowers(unfollowers)
        return unfollowers
