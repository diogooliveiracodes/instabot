import os
from datetime import datetime

_log_file = None
_logs_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'logs'
)


def start_session():
    """Cria um novo arquivo de log com timestamp no nome.
    Retorna o caminho do arquivo criado.
    """
    global _log_file
    stop_session()
    os.makedirs(_logs_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    path = os.path.join(_logs_dir, f'{timestamp}.log')
    _log_file = open(path, 'w', encoding='utf-8')
    log('=' * 50)
    log('SESSÃO INICIADA')
    log('=' * 50)
    return path


def stop_session():
    """Fecha o arquivo de log da sessão atual."""
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
    """Escreve uma linha no arquivo de log com timestamp."""
    if _log_file and text:
        try:
            ts = datetime.now().strftime('%H:%M:%S')
            _log_file.write(f'[{ts}] {text}\n')
            _log_file.flush()
        except Exception:
            pass
