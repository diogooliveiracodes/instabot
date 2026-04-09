import os
from datetime import datetime


class FileManager:
    UNFOLLOWERS_FILE = 'nao-seguidores.txt'
    REMOVED_FILE = 'removidos.txt'

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

    def save_unfollowers(self, unfollowers):
        with open(self.unfollowers_path, 'w', encoding='utf-8') as f:
            for user in unfollowers:
                f.write(user + '\n')
        print(f'\nLista salva em: {self.unfollowers_path} ({len(unfollowers)} perfis)')

    def load_unfollowers(self):
        if not os.path.exists(self.unfollowers_path):
            print(f'\nArquivo {self.unfollowers_path} não encontrado.')
            print('Execute a opção "Listar não seguidores" primeiro.')
            return []
        with open(self.unfollowers_path, 'r', encoding='utf-8') as f:
            users = [line.strip() for line in f if line.strip()]
        print(f'\nLista de não-seguidores carregada: {len(users)} perfis')
        return users

    def append_removed(self, username):
        with open(self.removed_path, 'a', encoding='utf-8') as f:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f'{username} - {timestamp}\n')

    def process_removal(self, username, unfollowers):
        """Registra a remoção e atualiza ambos os arquivos."""
        self.append_removed(username)
        if username in unfollowers:
            unfollowers.remove(username)
        self.save_unfollowers(unfollowers)
        return unfollowers
