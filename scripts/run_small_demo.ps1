$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$env:PYTHONPATH = Join-Path $root "src"

python -m bigdata_platform.generate_events --users 500 --items 80 --events 5000 --days 30
python -m bigdata_platform.local_etl
python -m bigdata_platform.report

Write-Host ""
Write-Host "Small demo finished."
Write-Host "Open: $root\warehouse\reports\dashboard.html"

