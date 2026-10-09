$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -U pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m playwright install chromium
Write-Host "Installed. Open this folder in Cursor, or run:"
Write-Host "  .\.venv\Scripts\python.exe scripts\download_sn_list.py '<sales-nav-list-url>'"
