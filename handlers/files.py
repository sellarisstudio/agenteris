"""
Handler: file tree explorer + read + download
"""
import os

from config import HERMES_DIR, DIR_SCAN_DEPTH, DIR_MAX_ITEMS, DIR_SIZE_LIMIT
from utils import fmt_size


def _scan(path: str, depth: int = 0) -> list:
    """Recursively scan a directory up to DIR_SCAN_DEPTH."""
    if depth > DIR_SCAN_DEPTH:
        return [{'name': '…', 'type': 'ellipsis'}]

    try:
        items = sorted(
            os.listdir(path),
            key=lambda x: (not os.path.isdir(os.path.join(path, x)), x.lower()),
        )
    except PermissionError:
        return [{'name': '…', 'type': 'ellipsis'}]

    result = []
    for name in items:
        if len(result) >= DIR_MAX_ITEMS:
            break
        if name.startswith('.'):
            continue
        full = os.path.join(path, name)
        try:
            if os.path.isdir(full):
                result.append({
                    'name': name,
                    'type': 'dir',
                    'children': _scan(full, depth + 1),
                })
            else:
                sz = os.path.getsize(full)
                if sz > DIR_SIZE_LIMIT:
                    continue
                result.append({
                    'name': name,
                    'type': 'file',
                    'size': fmt_size(sz),
                })
        except OSError:
            continue
    return result


def tree_handler(rel: str) -> dict:
    """GET /api/tree?dir=<relative> — return directory listing."""
    target = os.path.normpath(os.path.join(HERMES_DIR, rel))
    if not target.startswith(HERMES_DIR) or not os.path.isdir(target):
        return None
    return {
        'root': os.path.basename(target),
        'path': target,
        'children': _scan(target),
    }


def read_handler(rel: str):
    """GET /api/read/<relative> — return file content + mime."""
    full = os.path.normpath(os.path.join(HERMES_DIR, rel))
    if not full.startswith(HERMES_DIR) or not os.path.isfile(full):
        return None, 404

    try:
        data = open(full, 'rb').read()
    except OSError:
        return None, 500

    ct = 'text/plain;charset=utf-8'
    if data[:4] == b'\x89PNG':
        ct = 'image/png'
    elif data[:3] == b'\xff\xd8\xff':
        ct = 'image/jpeg'
    return data, ct
