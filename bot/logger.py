import os
from datetime import datetime

_log_file = None
_logs_dir = None


def set_profile_dir(profile_dir):
    """Define a pasta onde os logs serão salvos."""
    global _logs_dir
    _logs_dir = profile_dir
    if _logs_dir:
        os.makedirs(_logs_dir, exist_ok=True)


def start_session():
    global _log_file
    stop_session()

    target = _logs_dir or os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
    os.makedirs(target, exist_ok=True)

    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    path = os.path.join(target, f'{timestamp}.log')
    _log_file = open(path, 'w', encoding='utf-8')
    log('=' * 50)
    log('SESSÃO INICIADA')
    log('=' * 50)
    return path


def stop_session():
    global _log_file
    if _log_file:
        log('=' * 50)
        log('SESSÃO ENCERRADA')
        log('=' * 50)
        try:
            _log_file.close()
        except Exception:
            pass
        _log_file = None


def log(text):
    if _log_file and text:
        try:
            ts = datetime.now().strftime('%H:%M:%S')
            _log_file.write(f'[{ts}] {text}\n')
            _log_file.flush()
        except Exception:
            pass
