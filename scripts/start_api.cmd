@echo off
cd /d "%~dp0.."
set "PYTHONPATH=%CD%\src"
"%CD%\.venv\Scripts\python.exe" -m uvicorn bigdata_platform.api:app --host 127.0.0.1 --port 8000

