#!/usr/bin/env bash
cd "$(dirname "$0")"
python3 -m pip install -r requirements.txt
python3 -m uvicorn app:app --host 0.0.0.0 --port 8000 &
sleep 2
if command -v xdg-open >/dev/null; then xdg-open http://localhost:8000; elif command -v open >/dev/null; then open http://localhost:8000; fi
wait
