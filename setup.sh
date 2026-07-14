#!/usr/bin/env bash
# Hermes Dashboard — zero-dependency setup
# Usage: bash setup.sh
set -e

echo "📦 Hermes Dashboard Setup"
echo "========================="

# Create .env from example if not exists
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅  .env created from .env.example"
    echo "📝  Edit .env with your Tuya credentials"
else
    echo "ℹ️   .env already exists, keeping it"
fi

echo ""
echo "🚀  Run:  python3 server.py"
echo "🌐  Open: http://localhost:5555"
echo ""
echo "📌  For public access, run:"
echo "    ssh -R 80:localhost:5555 serveo.net"
echo "    or set up Cloudflare Tunnel pointing to localhost:5555"
