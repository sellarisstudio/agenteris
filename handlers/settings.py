"""
Handler: settings — Tuya credentials management
"""
import os
import json
from pathlib import Path

from config import HERMES_DIR, ENV_FILE

# Map form keys → env keys
KEY_MAP = {
    'access_id': 'TUYA_ACCESS_ID',
    'access_secret': 'TUYA_ACCESS_SECRET',
    'device_id': 'TUYA_DEVICE_ID',
    'endpoint': 'TUYA_ENDPOINT',
}


def load_tuya() -> dict:
    """Return current Tuya credentials from .env."""
    creds = {
        'access_id': '',
        'access_secret': '',
        'device_id': '',
        'endpoint': 'openapi-sg.iotbing.com',
    }
    if not os.path.isfile(ENV_FILE):
        return creds
    try:
        for line in open(ENV_FILE):
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            k = k.strip()
            v = v.strip().strip('"\'')
            if k == 'TUYA_ACCESS_ID': creds['access_id'] = v
            elif k == 'TUYA_ACCESS_SECRET': creds['access_secret'] = v
            elif k == 'TUYA_DEVICE_ID': creds['device_id'] = v
            elif k == 'TUYA_ENDPOINT': creds['endpoint'] = v
    except OSError:
        pass
    return creds


def save_tuya(data: dict) -> None:
    """Update only Tuya lines in .env, preserving everything else."""
    form_keys = data.keys()
    env_prefix = 'TUYA_'

    # Read original .env lines
    original_lines = []
    if os.path.isfile(ENV_FILE):
        with open(ENV_FILE) as f:
            original_lines = f.readlines()

    # Build replacement map from form data
    replacements = {}
    for form_key, env_key in KEY_MAP.items():
        if form_key in data:
            replacements[env_key] = data[form_key]

    # Track which env keys we've already written
    written = set()
    new_lines = []

    for line in original_lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('#') and '=' in stripped:
            k = stripped.split('=', 1)[0].strip()
            if k in replacements:
                # Replace with new value
                new_lines.append(f'{k}={replacements[k]}\n')
                written.add(k)
                continue
        # Keep original line
        new_lines.append(line)

    # Append any new keys not yet written
    for k, v in replacements.items():
        if k not in written:
            new_lines.append(f'{k}={v}\n')

    with open(ENV_FILE, 'w') as f:
        f.writelines(new_lines)


def settings_handler(request_body: bytes = None):
    """GET or POST /api/settings

    GET  → return current Tuya credentials.
    POST → save posted credentials (JSON body).
    """
    if request_body is None:
        return load_tuya()
    data = json.loads(request_body)
    save_tuya(data)
    return {'ok': True}
