from __future__ import annotations

import argparse
from html import escape

import pandas as pd

from .config import MARTS_DIR, REPORT_DIR, ensure_dirs


def _table(frame: pd.DataFrame, limit: int = 12) -> str:
    return frame.head(limit).to_html(index=False, classes="data-table", border=0)


def build_report() -> str:
    ensure_dirs()
    daily = pd.read_csv(MARTS_DIR / "daily_overview.csv")
    category = pd.read_csv(MARTS_DIR / "category_sales.csv")
    top_items = pd.read_csv(MARTS_DIR / "top_items.csv")
    retention = pd.read_csv(MARTS_DIR / "retention.csv")

    latest = daily.sort_values("event_date").tail(1).iloc[0]
    total_gmv = daily["gmv"].sum()
    avg_cvr = daily["cvr"].mean()
    html = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>分布式大数据处理与分析平台 - 指标报表</title>
  <style>
    body {{ font-family: "Microsoft YaHei", Arial, sans-serif; margin: 32px; color: #222; }}
    h1 {{ margin-bottom: 6px; }}
    .sub {{ color: #666; margin-bottom: 24px; }}
    .cards {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 24px; }}
    .card {{ border: 1px solid #ddd; border-radius: 8px; padding: 14px; background: #fafafa; }}
    .label {{ color: #666; font-size: 13px; }}
    .value {{ font-size: 24px; font-weight: 700; margin-top: 6px; }}
    .section {{ margin-top: 28px; }}
    .data-table {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
    .data-table th, .data-table td {{ border-bottom: 1px solid #e6e6e6; padding: 8px; text-align: left; }}
    .data-table th {{ background: #f2f4f7; }}
  </style>
</head>
<body>
  <h1>分布式大数据处理与分析平台</h1>
  <div class="sub">本地演示报表，由 raw events 经过离线 ETL 聚合生成。</div>
  <div class="cards">
    <div class="card"><div class="label">最新日期</div><div class="value">{escape(str(latest["event_date"]))}</div></div>
    <div class="card"><div class="label">最新 DAU</div><div class="value">{int(latest["dau"]):,}</div></div>
    <div class="card"><div class="label">累计 GMV</div><div class="value">¥{total_gmv:,.0f}</div></div>
    <div class="card"><div class="label">平均 CVR</div><div class="value">{avg_cvr:.2%}</div></div>
  </div>
  <div class="section"><h2>每日核心指标</h2>{_table(daily.sort_values("event_date", ascending=False))}</div>
  <div class="section"><h2>品类销售排行</h2>{_table(category.sort_values("gmv", ascending=False))}</div>
  <div class="section"><h2>Top 商品</h2>{_table(top_items)}</div>
  <div class="section"><h2>用户留存</h2>{_table(retention.sort_values(["cohort_date", "days_after"], ascending=[False, True]))}</div>
</body>
</html>"""
    output = REPORT_DIR / "dashboard.html"
    output.write_text(html, encoding="utf-8")
    return str(output)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build an HTML report from mart tables.")
    parser.parse_args()
    print(build_report())


if __name__ == "__main__":
    main()

