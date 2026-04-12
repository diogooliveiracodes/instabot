import json
import os

_PROFILES_FILE = 'profiles.json'
_LOGS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'logs'
)


def _profiles_path():
    os.makedirs(_LOGS_DIR, exist_ok=True)
    return os.path.join(_LOGS_DIR, _PROFILES_FILE)


def load_profiles():
    path = _profiles_path()
    if not os.path.exists(path):
        return []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        return []


def save_profile(login, password, username):
    """Salva ou atualiza um perfil. Retorna a lista atualizada."""
    profiles = load_profiles()

    for p in profiles:
        if p['username'] == username:
            p['login'] = login
            p['password'] = password
            _write(profiles)
            return profiles

    profiles.append({
        'login': login,
        'password': password,
        'username': username,
    })
    _write(profiles)
    return profiles


def remove_profile(username):
    profiles = [p for p in load_profiles() if p['username'] != username]
    _write(profiles)
    return profiles


def get_profile_dir(username):
    """Retorna e cria a pasta de dados do perfil: logs/<username>/"""
    profile_dir = os.path.join(_LOGS_DIR, username)
    os.makedirs(profile_dir, exist_ok=True)
    return profile_dir


def _write(profiles):
    with open(_profiles_path(), 'w', encoding='utf-8') as f:
        json.dump(profiles, f, ensure_ascii=False, indent=2)
