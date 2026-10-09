#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -m venv .venv
.venv/bin/python -m pip install -U pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m playwright install chromium
echo "Installed. Open this folder in Cursor, or run:"
echo "  .venv/bin/python scripts/download_sn_list.py '<sales-nav-list-url>'"
