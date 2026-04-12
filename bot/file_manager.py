import json
import os
from datetime import datetime


class FileManager:
    UNFOLLOWERS_FILE = 'nao-seguidores.json'
    REMOVED_FILE = 'removidos.json'
    FOLLOWERS_FILE = 'seguidores.json'
    LOST_FOLLOWERS_FILE = 'perdidos.json'

    def __init__(self, profile_dir):
        self._profile_dir = profile_dir
        os.makedirs(self._profile_dir, exist_ok=True)

    @property
    def unfollowers_path(self):
        return os.path.join(self._profile_dir, self.UNFOLLOWERS_FILE)

    @property
    def removed_path(self):
        return os.path.join(self._profile_dir, self.REMOVED_FILE)

    @property
    def followers_path(self):
        return os.path.join(self._profile_dir, self.FOLLOWERS_FILE)

    @property
    def lost_followers_path(self):
        return os.path.join(self._profile_dir, self.LOST_FOLLOWERS_FILE)

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

    # ── seguidores.json ──────────────────────────────────────────────

    def save_followers(self, followers):
        with open(self.followers_path, 'w', encoding='utf-8') as f:
            json.dump(followers, f, ensure_ascii=False, indent=2)
        print(f'\nLista de seguidores salva: {len(followers)} perfis')

    def load_followers(self):
        if not os.path.exists(self.followers_path):
            return []
        with open(self.followers_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def has_followers_snapshot(self):
        return os.path.exists(self.followers_path)

    # ── perdidos.json ────────────────────────────────────────────────

    def load_lost_followers(self):
        if not os.path.exists(self.lost_followers_path):
            return []
        try:
            with open(self.lost_followers_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, ValueError):
            return []

    def save_lost_followers(self, entries):
        with open(self.lost_followers_path, 'w', encoding='utf-8') as f:
            json.dump(entries, f, ensure_ascii=False, indent=2)

    def detect_lost_followers(self, new_followers):
        """Compara a lista anterior de seguidores com a nova.
        Retorna a lista atualizada de perdidos.
        """
        old_followers = self.load_followers()
        if not old_followers:
            print('\nNenhuma lista anterior de seguidores encontrada. '
                  'Salvando lista atual como referência.')
            self.save_followers(new_followers)
            return self.load_lost_followers()

        old_set = set(old_followers)
        new_set = set(new_followers)

        lost_now = old_set - new_set
        gained_now = new_set - old_set

        print(f'\nSeguidores anteriores: {len(old_followers)}')
        print(f'Seguidores atuais: {len(new_followers)}')
        print(f'Novos seguidores: {len(gained_now)}')
        print(f'Deixaram de seguir: {len(lost_now)}')

        existing = self.load_lost_followers()
        already_logged = {e['username'] for e in existing}
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        for username in sorted(lost_now):
            if username not in already_logged:
                existing.append({
                    'username': username,
                    'lost_at': timestamp,
                })

        self.save_lost_followers(existing)
        self.save_followers(new_followers)

        return existing

    # ── Operação composta ────────────────────────────────────────────

    def process_removal(self, username, unfollowers):
        if username not in unfollowers:
            print(f'  AVISO: {username} não está na lista. Remoção ignorada.')
            return unfollowers
        self.append_removed(username)
        unfollowers.remove(username)
        self.save_unfollowers(unfollowers)
        return unfollowers
