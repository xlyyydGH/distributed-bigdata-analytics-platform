$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$env:PYTHONPATH = Join-Path $root "src"

python -m bigdata_platform.generate_events --users 5000 --items 600 --events 80000 --days 90
python -m bigdata_platform.local_etl
python -m bigdata_platform.report

Write-Host ""
Write-Host "Local demo finished."
Write-Host "Open: $root\warehouse\reports\dashboard.html"

