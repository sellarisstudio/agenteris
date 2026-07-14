"""
Config — environment & constants

All paths default to ~/.hermes for Hermes Agent integration.
Override with env vars for standalone usage.
"""
import os

# Root path — fallback to ./hermes if no Hermes Agent installed
HERMES_DIR = os.path.expanduser(os.environ.get(
    'HERMES_DIR', '~/.hermes'
))

CRON_DIR = os.path.join(HERMES_DIR, 'cron')
CRON_JOBS_FILE = os.path.join(CRON_DIR, 'jobs.json')
OUTPUT_DIR = os.path.join(CRON_DIR, 'output')
SCRIPTS_DIR = os.path.join(HERMES_DIR, 'scripts')
ENV_FILE = os.path.join(HERMES_DIR, '.env')

PORT = int(os.environ.get('PORT', 5555))
HOST = os.environ.get('HOST', '0.0.0.0')

# File browser limits
DIR_SCAN_DEPTH = 3
DIR_MAX_ITEMS = 80
DIR_SIZE_LIMIT = 5 * 1024 * 1024  # 5MB max file size to show inline
