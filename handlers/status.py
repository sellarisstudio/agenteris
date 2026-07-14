"""
Handler: system status (battery, disk, RAM, uptime)
"""
import subprocess
import json
import shutil

from config import HERMES_DIR


def get_battery() -> dict:
    """Return parsed termux-battery-status or defaults."""
    try:
        raw = subprocess.check_output(['termux-battery-status'], timeout=5).decode()
        return json.loads(raw)
    except Exception:
        return {}


def get_disk() -> dict:
    """Return Android internal storage usage."""
    try:
        usage = shutil.disk_usage('/storage/emulated/0/Android/obb')
        return {
            'total': f'{usage.total // (1 << 30)}G',
            'used': f'{usage.used // (1 << 30)}G',
            'free': f'{usage.free // (1 << 30)}G',
            'pct': f'{(usage.used / usage.total * 100):.0f}%',
        }
    except Exception:
        return {'total': '?', 'used': '?', 'free': '?', 'pct': '?'}


def get_ram() -> dict:
    """Return parsed /proc/meminfo."""
    try:
        total_kb = 0
        avail_kb = 0
        for line in open('/proc/meminfo'):
            if line.startswith('MemTotal:'):
                total_kb = int(line.split()[1])
            elif line.startswith('MemAvailable:'):
                avail_kb = int(line.split()[1])
        return {
            'total': f'{total_kb // 1024}MB',
            'used': f'{(total_kb - avail_kb) // 1024}MB',
        }
    except Exception:
        return {'total': '?', 'used': '?'}


def get_uptime() -> str:
    """Return human‑readable uptime."""
    try:
        secs = float(open('/proc/uptime').read().split()[0])
        h = int(secs // 3600)
        m = int((secs % 3600) // 60)
        return f'{h}j {m}m' if h else f'{m}m'
    except Exception:
        return '?'


def status_handler() -> dict:
    """GET /api/status — return everything in one shot."""
    return {
        'battery': get_battery(),
        'disk': get_disk(),
        'ram': get_ram(),
        'uptime': get_uptime(),
    }
