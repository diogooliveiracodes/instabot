import json
import os
from datetime import datetime


class FileManager:
    UNFOLLOWERS_FILE = 'nao-seguidores.json'
    REMOVED_FILE = 'removidos.json'

    def __init__(self):
        self._logs_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'logs'
        )
        os.makedirs(self._logs_dir, exist_ok=True)

    @property
    def unfollowers_path(self):
        return os.path.join(self._logs_dir, self.UNFOLLOWERS_FILE)

    @property
    def removed_path(self):
        return os.path.join(self._logs_dir, self.REMOVED_FILE)

    # ── nao-seguidores.json ──────────────────────────────────────────

    def save_unfollowers(self, unfollowers):
        with open(self.unfollowers_path, 'w', encoding='utf-8') as f:
            json.dump(unfollowers, f, ensure_ascii=False, indent=2)
        print(f'\nLista salva em: {self.unfollowers_path} '
              f'({len(unfollowers)} perfis)')

    def load_unfollowers(self):
        if not os.path.exists(self.unfollowers_path):
            old_txt = os.path.join(self._logs_dir, 'nao-seguidores.txt')
            if os.path.exists(old_txt):
                return self._migrate_unfollowers_txt(old_txt)
            print(f'\nArquivo {self.unfollowers_path} não encontrado.')
            print('Execute a opção "Listar não seguidores" primeiro.')
            return []

        with open(self.unfollowers_path, 'r', encoding='utf-8') as f:
            users = json.load(f)
        print(f'\nLista de não-seguidores carregada: {len(users)} perfis')
        return users

    def _migrate_unfollowers_txt(self, txt_path):
        """Migra nao-seguidores.txt para .json automaticamente."""
        print(f'\nMigrando {txt_path} para JSON...')
        with open(txt_path, 'r', encoding='utf-8') as f:
            users = [line.strip() for line in f if line.strip()]
        self.save_unfollowers(users)
        print(f'Migração concluída: {len(users)} perfis')
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
            old_txt = os.path.join(self._logs_dir, 'removidos.txt')
            if os.path.exists(old_txt):
                return self._migrate_removed_txt(old_txt)
            return []
        try:
            with open(self.removed_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, ValueError):
            return []

    def _migrate_removed_txt(self, txt_path):
        """Migra removidos.txt para .json automaticamente."""
        print(f'\nMigrando {txt_path} para JSON...')
        entries = []
        with open(txt_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if ' - ' in line:
                    parts = line.rsplit(' - ', 1)
                    entries.append({
                        'username': parts[0].strip(),
                        'timestamp': parts[1].strip() if len(parts) > 1 else ''
                    })
        with open(self.removed_path, 'w', encoding='utf-8') as f:
            json.dump(entries, f, ensure_ascii=False, indent=2)
        print(f'Migração concluída: {len(entries)} registros')
        return entries

    # ── Operação composta ────────────────────────────────────────────

    def is_in_unfollowers_list(self, username):
        """Verifica se o username está na lista de não-seguidores."""
        unfollowers = self.load_unfollowers() if not hasattr(self, '_cached') \
            else self._cached
        return username in unfollowers

    def process_removal(self, username, unfollowers):
        """Registra a remoção e atualiza ambos os arquivos."""
        if username not in unfollowers:
            print(f'  AVISO: {username} não está na lista. Remoção ignorada.')
            return unfollowers
        self.append_removed(username)
        unfollowers.remove(username)
        self.save_unfollowers(unfollowers)
        return unfollowers
