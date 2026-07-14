"""
Handler: cron jobs listing + log reader
"""
import os
import json
import time
from datetime import datetime

from config import CRON_DIR, OUTPUT_DIR


def _load_jobs() -> list:
    """Read cron/jobs.json and return the raw job list."""
    path = os.path.join(CRON_DIR, 'jobs.json')
    try:
        return json.load(open(path)).get('jobs', [])
    except Exception:
        return []


def _countdown(next_run_at: str) -> str:
    """Return human‑readable countdown string."""
    if not next_run_at:
        return ''
    try:
        if next_run_at.endswith('Z'):
            next_run_at = next_run_at[:-1] + '+00:00'
        diff = datetime.fromisoformat(next_run_at).timestamp() - time.time()
        if diff <= 0:
            return ''
        if diff < 60:
            return f'{int(diff)}d'
        if diff < 3600:
            return f'{int(diff // 60)}m'
        if diff < 86400:
            h = int(diff // 3600)
            m = int((diff % 3600) // 60)
            return f'{h}j{m}m' if m else f'{h}j'
        return f'{int(diff // 86400)}h'
    except Exception:
        return ''


def cron_list_handler() -> list:
    """GET /api/cron — return enriched job list."""
    jobs = []
    for j in _load_jobs():
        jid = j.get('id', '')
        log_dir = os.path.join(OUTPUT_DIR, jid)
        log_exists = (
            os.path.isdir(log_dir)
            and any(f.endswith('.md') for f in os.listdir(log_dir))
        )
        jobs.append({
            'id': jid,
            'name': j.get('name', '?'),
            'schedule': str(j.get('schedule', {})),
            'schedule_display': j.get('schedule', {}).get('display', str(j.get('schedule', {}))),
            'enabled': j.get('enabled', True),
            'last_status': j.get('last_status', '?'),
            'script': j.get('script', ''),
            'countdown': _countdown(j.get('next_run_at', '')),
            'next_run_at': j.get('next_run_at', ''),
            'log_exists': log_exists,
            'last_run': j.get('last_run_at', ''),
        })
    return jobs


def log_handler(job_id: str):
    """GET /api/log/<job_id> — return latest log file content."""
    log_dir = os.path.join(OUTPUT_DIR, job_id)
    if not os.path.isdir(log_dir):
        return None
    try:
        files = sorted(
            [f for f in os.listdir(log_dir) if f.endswith('.md')],
            reverse=True,
        )
        if not files:
            return None
        return open(os.path.join(log_dir, files[0])).read()
    except Exception:
        return None
