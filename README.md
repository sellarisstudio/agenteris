# Hermes Dashboard

Zero-dependency web dashboard for monitoring an Android Hermes Agent setup — straight from your phone.

Built entirely with **Python stdlib**. No npm, no Node, no database. `requests` is optional and only needed if you use a Tuya smart plug.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue) ![License](https://img.shields.io/badge/License-MIT-green)

---

## Clone & Run

```bash
# 1. Clone
git clone https://github.com/sellarisstudio/agenteris.git
cd agenteris

# 2. (Optional) Install Tuya dependency — only if you use a smart plug
pip install requests

# 3. Start
python3 server.py

# 4. Open → http://localhost:5555
```

One-liner (no clone):

```bash
curl -L https://github.com/sellarisstudio/agenteris/archive/refs/heads/master.tar.gz | tar xz
cd agenteris-master && python3 server.py
```

---

## Features

| Tab | What it does |
|-----|-------------|
| **Status** | Battery %, temperature, storage, RAM, uptime |
| **Cron** | View all cron jobs with real-time countdown, read logs per job |
| **Settings** | Edit Tuya IoT credentials (Access ID, Secret, Device ID, Endpoint) + **ON/OFF** your plug from your phone |
| **Files** | Browse `~/.hermes` — view, read, download files |

---

## Public Access

**Serveo** (free, no setup):
```bash
ssh -R 80:localhost:5555 serveo.net
```
→ Get a URL like `https://xxx.serveo.net`

**Cloudflare Tunnel** (custom domain, stable):
```bash
cloudflared tunnel --url http://localhost:5555
```

---

## Dependencies

| Package | Purpose | Required? |
|---------|---------|-----------|
| Python 3.8+ | — | ✅ Yes |
| `requests` | Tuya IoT API (smart plug ON/OFF) | ❌ Optional |

Check if installed:
```bash
python3 -c "import requests; print('OK')" || pip install requests
```

---

## Configuration

Edit `~/.hermes/.env` or use the **Settings → Tuya IoT** page in the dashboard:

| Key | Example |
|-----|---------|
| `TUYA_ACCESS_ID` | `p9xrryqc9akg4n3uu3tp` |
| `TUYA_ACCESS_SECRET` | `7d653b361e11405b8c654545584ea26a` |
| `TUYA_DEVICE_ID` | `a3671b8bebfb4d0814raom` |
| `TUYA_ENDPOINT` | `openapi-sg.iotbing.com` |

Override the Hermes path (useful for standalone setups):
```bash
HERMES_DIR=/path/to/data python3 server.py
```

---

## Project Structure

```
├── server.py              ← Entrypoint + HTTP router
├── config.py              ← Paths, port, limits
├── setup.sh               ← Init .env from example
├── handlers/
│   ├── status.py          → /api/status
│   ├── cron.py            → /api/cron, /api/log/<id>
│   ├── files.py           → /api/tree, /api/read
│   ├── settings.py        → /api/settings (GET/POST)
│   └── tuya.py            → /api/tuya-test (status + ON/OFF)
├── templates/
│   └── index.html         ← Mobile-first SPA (vanilla JS, Lucide icons)
└── utils/__init__.py      ← fmt_size()
```

---

## License

MIT — free to use, modify, sell, whatever.
