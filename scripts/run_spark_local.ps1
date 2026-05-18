$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot

# PySpark on Windows can fail when the project path contains Chinese
# characters. Map the project directory to an ASCII drive for the local demo.
$drive = "B:"
cmd /c "subst $drive /D" 2>$null | Out-Null
cmd /c "subst $drive `"$root`"" | Out-Null

Set-Location "$drive\"
$env:PYTHONPATH = "$drive\src"
$env:PYSPARK_PYTHON = "$drive\.venv\Scripts\python.exe"
$env:PYSPARK_DRIVER_PYTHON = "$drive\.venv\Scripts\python.exe"
$env:SPARK_HOME = "$drive\.venv\Lib\site-packages\pyspark"

& "$drive\.venv\Scripts\python.exe" -m bigdata_platform.spark_etl --raw-dir data/raw --output-dir warehouse/spark_marts

Write-Host ""
Write-Host "Spark local ETL finished."
Write-Host "Output: $root\warehouse\spark_marts"
