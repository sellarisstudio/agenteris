# Hermes Dashboard

Zero‑dependency web dashboard for monitoring an Android Hermes Agent setup from your phone.

Built with pure **Python stdlib** — no npm, no Webpack, no database. Only `requests` if you use Tuya IoT.

![Hermes Dashboard](https://img.shields.io/badge/Python-3.8%2B-blue) ![License](https://img.shields.io/badge/License-MIT-green)

---

## Clone & Run

```bash
# 1. Clone
git clone https://github.com/sellarisstudio/agenteris.git
cd agenteris

# 2. (Opsional) Install Tuya dependency — cuma kalo pake colokan smart plug
pip install requests

# 3. Jalankan
python3 server.py

# 4. Buka browser → http://localhost:5555
```

Atau langsung tanpa clone:

```bash
curl -L https://github.com/sellarisstudio/agenteris/archive/refs/heads/master.tar.gz | tar xz
cd agenteris-master && python3 server.py
```

---

## Features

| Tab | Fungsi |
|-----|--------|
| **Status** | Battery % & suhu, storage, RAM, uptime |
| **Cron** | Lihat semua cron job + countdown realtime + baca log tiap job |
| **Settings** | Edit Tuya IoT credentials (Access ID, Secret, Device ID, Endpoint) + **Test ON/OFF** colokan langsung dari HP |
| **Files** | Browser folder `~/.hermes` — lihat, baca, download file |

---

## Public Access (dari luar rumah)

**Serveo** (gratis, gak perlu setup):
```bash
ssh -R 80:localhost:5555 serveo.net
```
→ Dapet URL `https://xxx.serveo.net`

**Cloudflare Tunnel** (custom domain, stabil):
```bash
cloudflared tunnel --url http://localhost:5555
```

---

## Dependency

| Package | Untuk | Wajib? |
|---------|-------|--------|
| Python 3.8+ | — | ✅ Wajib |
| `requests` | Tuya IoT API (ON/OFF smart plug) | ❌ Opsional |

Cek installed:
```bash
python3 -c "import requests; print('requests OK')" || pip install requests
```

---

## Konfigurasi

Edit `~/.hermes/.env` atau dari dashboard **Settings → Tuya IoT**:

| Key | Contoh |
|-----|--------|
| `TUYA_ACCESS_ID` | `p9xrryqc9akg4n3uu3tp` |
| `TUYA_ACCESS_SECRET` | `7d653b361e11405b8c654545584ea26a` |
| `TUYA_DEVICE_ID` | `a3671b8bebfb4d0814raom` |
| `TUYA_ENDPOINT` | `openapi-sg.iotbing.com` |

---

## Project Structure

```
├── server.py              ← Entrypoint + HTTP router
├── config.py              ← Paths, port, limits
├── setup.sh               ← Init .env dari example
├── handlers/
│   ├── status.py          → /api/status
│   ├── cron.py            → /api/cron, /api/log/<id>
│   ├── files.py           → /api/tree, /api/read
│   ├── settings.py        → /api/settings (GET/POST)
│   └── tuya.py            → /api/tuya-test (ON/OFF)
├── templates/
│   └── index.html         ← SPA mobile-first (vanilla JS)
└── utils/__init__.py      ← fmt_size()
```

---

## License

MIT — bebas dipake, diubah, dijual, apapun.
