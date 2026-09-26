@echo off
cd /d "%~dp0"
where py >nul 2>nul && set PY=py || set PY=python
%PY% -m pip install -r requirements.txt
start "PorCuanto" cmd /c "%PY% -m uvicorn app:app --host 0.0.0.0 --port 8000"
timeout /t 2 >nul
start "" http://localhost:8000
