# Hermes Dashboard

Zero‑dependency web dashboard for monitoring an Android Hermes Agent setup from your phone.

Built with pure Python stdlib — no npm, no pip (except requests for Tuya API).

## Features

- **Status** — battery % & temp, disk usage, RAM, uptime
- **Cron** — job list with real‑time countdown, log viewer per job
- **Settings** — Tuya IoT credentials editor (Access ID, Secret, Device ID, Endpoint)
- **Tuya Smart Plug** — ON/OFF test buttons, real‑time device status
- **Files** — browse ~/.hermes directory tree, read/download files
- **Apple‑light SPA** — responsive mobile‑first UI with Lucide icons

## Quick Start

```bash
git clone <repo-url>
cd hermes-dashboard
bash setup.sh            # creates .env
python3 server.py        # starts on http://localhost:5555
```

Or the one‑liner (no clone needed):

```bash
# If Hermes Agent is installed:
hermes tools install hermes-dashboard
```

## Public Access

```bash
# Serveo (easiest, free):
ssh -R 80:localhost:5555 serveo.net

# Cloudflare Tunnel (stable, custom domain):
cloudflared tunnel --url http://localhost:5555
```

## Configuration

Edit `.env` or use the Settings → Tuya IoT page in the dashboard:

| Key | Description |
|-----|-------------|
| `TUYA_ACCESS_ID` | Tuya IoT Platform Client ID |
| `TUYA_ACCESS_SECRET` | Tuya IoT Platform Secret |
| `TUYA_DEVICE_ID` | Smart Plug Device ID |
| `TUYA_ENDPOINT` | API endpoint (e.g. `openapi-sg.iotbing.com`) |

## Architecture

```
server.py              ← entrypoint, HTTP router (Python stdlib)
config.py              ← paths, limits
handlers/
├── status.py          ← /api/status (battery, disk, uptime)
├── cron.py            ← /api/cron, /api/log/<id>
├── files.py           ← /api/tree, /api/read, /api/download
├── settings.py        ← /api/settings (GET/POST Tuya credentials)
└── tuya.py            ← /api/tuya-test (status + ON/OFF commands)
utils/
└── __init__.py        ← fmt_size()
templates/
└── index.html         ← Single‑page app (vanilla JS, Lucide icons)
```

## Requirements

- Python 3.8+
- `requests` library (for Tuya API calls — optional if you don't use Tuya)

## License

MIT
