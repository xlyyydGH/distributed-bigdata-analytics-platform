$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$env:PYTHONPATH = Join-Path $root "src"

& ".\.venv\Scripts\python.exe" -m uvicorn bigdata_platform.api:app --host 127.0.0.1 --port 8000

