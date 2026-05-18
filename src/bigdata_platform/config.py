from __future__ import annotations

import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
WAREHOUSE_DIR = PROJECT_ROOT / "warehouse"
MARTS_DIR = WAREHOUSE_DIR / "marts"
REPORT_DIR = WAREHOUSE_DIR / "reports"
SQLITE_DB = WAREHOUSE_DIR / "analytics.db"


MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "bigdata123")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "bigdata_analytics")


def ensure_dirs() -> None:
    for path in [RAW_DIR, MARTS_DIR, REPORT_DIR, WAREHOUSE_DIR]:
        path.mkdir(parents=True, exist_ok=True)

