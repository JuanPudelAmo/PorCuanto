#!/data/data/com.termux/files/usr/bin/bash
cd "$(dirname "$0")"
pkg install -y python >/dev/null 2>&1 || true
python -m pip install -r requirements.txt
python -m uvicorn app:app --host 0.0.0.0 --port 8000
