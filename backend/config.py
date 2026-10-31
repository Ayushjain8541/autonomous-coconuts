"""Small env-file reader; credentials stay local, excluded from repr/logging."""
import os
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ORIGINS = ('http://localhost:5173', 'http://127.0.0.1:5173', 'http://localhost:3000', 'http://127.0.0.1:3000')


@dataclass(frozen=True)
class Settings:
    api_key: str = field(default='', repr=False)
    model: str = 'claude-haiku-4-5-20251001'
    timeout: float = 25.0
    cors_origins: tuple = DEFAULT_ORIGINS
    report_timeout: float = 60.0


def load_settings(root=ROOT, environ=None):
    values = {}
    allowed = {'ANTHROPIC_API_KEY', 'ANTHROPIC_MODEL', 'ANTHROPIC_TIMEOUT_SECONDS', 'ANTHROPIC_REPORT_TIMEOUT_SECONDS', 'COCONUTS_CORS_ORIGINS'}
    for name in ['.env', '.env.local']:
        path = Path(root) / name
        if not path.is_file() or path.is_symlink():
            continue
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, value = line.removeprefix('export ').split('=', 1)
            key, value = key.strip(), value.strip()
            if key not in allowed:
                continue
            if len(value) >= 2 and value[0] in '\"\'' and value[-1] == value[0]:
                value = value[1:-1]
            else:
                value = value.split(' #', 1)[0].strip()
            values[key] = value
    environment = os.environ if environ is None else environ
    values.update({key: environment[key] for key in allowed if key in environment})
    try:
        timeout = float(values.get('ANTHROPIC_TIMEOUT_SECONDS', '25'))
        if not 1 <= timeout <= 60:
            raise ValueError()
    except ValueError:
        timeout = 25.0
    try:
        report_timeout=float(values.get('ANTHROPIC_REPORT_TIMEOUT_SECONDS','60'))
        if not 1<=report_timeout<=90:raise ValueError()
    except ValueError:report_timeout=60.0
    origins = tuple(x.strip() for x in values.get('COCONUTS_CORS_ORIGINS', ','.join(DEFAULT_ORIGINS)).split(',') if x.strip())
    return Settings(api_key=values.get('ANTHROPIC_API_KEY', '').strip(),
                    model=values.get('ANTHROPIC_MODEL', '').strip() or 'claude-haiku-4-5-20251001',
                    timeout=timeout, cors_origins=origins, report_timeout=report_timeout)
