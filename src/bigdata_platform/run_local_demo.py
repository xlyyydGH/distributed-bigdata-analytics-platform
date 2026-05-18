from __future__ import annotations

from .generate_events import main as generate_main
from .local_etl import main as etl_main
from .report import main as report_main


if __name__ == "__main__":
    generate_main()
    etl_main()
    report_main()

