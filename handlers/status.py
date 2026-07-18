"""
Handler: system status (battery, disk, RAM, uptime)
"""
import subprocess
import json
import shutil
import os
import time

from config import HERMES_DIR


BATTERY_CACHE = os.path.expanduser("~/.hermes/scripts/.battery-state.json")
BATTERY_LOG = os.path.expanduser("~/.hermes/cron/output/.battery-log.md")
CACHE_MAX_AGE = 300  # 5 minutes


def get_battery() -> dict:
    """Return battery info — try termux-battery-status, fallback to cached state + log."""
    # Try live API (short timeout)
    try:
        raw = subprocess.check_output(
            ['termux-battery-status'],
            timeout=2,
            stderr=subprocess.DEVNULL
        ).decode()
        return json.loads(raw)
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, json.JSONDecodeError):
        pass
    except Exception:
        pass

    # Fallback: parse last log entry
    if os.path.exists(BATTERY_LOG):
        try:
            with open(BATTERY_LOG) as f:
                lines = [l.strip() for l in f if l.strip()]
            if lines:
                last = lines[-1]
                # Format: "HH:MM | 75% DISCHARGING 30.5C 🔌"
                parts = last.split('|')
                if len(parts) >= 2:
                    data = parts[1].strip().split()
                    return {
                        'percentage': int(data[0].rstrip('%')) if data else None,
                        'status': data[1] if len(data) > 1 else 'UNKNOWN',
                        'temperature': float(data[2].rstrip('C')) if len(data) > 2 else None,
                        'plugged': 'UNPLUGGED' if '🔌' in last else 'PLUGGED'
                    }
        except Exception:
            pass

    # Fallback: cache file
    if os.path.exists(BATTERY_CACHE):
        try:
            mtime = os.path.getmtime(BATTERY_CACHE)
            if time.time() - mtime < CACHE_MAX_AGE:
                with open(BATTERY_CACHE) as f:
                    cached = json.load(f)
                return {
                    'percentage': None,
                    'status': cached.get('plugged', 'UNKNOWN'),
                    'temperature': None,
                    'plugged': cached.get('plugged', 'UNKNOWN')
                }
        except Exception:
            pass

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
    bat = get_battery()
    # Normalize battery keys for frontend
    return {
        'battery': {
            'percentage': bat.get('percentage'),
            'temperature': bat.get('temperature'),
            'status': bat.get('status', ''),
            'plugged': bat.get('plugged', '')
        },
        'disk': get_disk(),
        'ram': get_ram(),
        'uptime': get_uptime(),
    }