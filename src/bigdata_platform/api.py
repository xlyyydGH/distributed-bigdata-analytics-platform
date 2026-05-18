from __future__ import annotations

import sqlite3
from typing import Any

from fastapi import FastAPI, Query

from .config import SQLITE_DB


app = FastAPI(title="Distributed Big Data Analytics API", version="1.0.0")


def query_table(sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    with sqlite3.connect(SQLITE_DB) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(sql, params).fetchall()
    return [dict(row) for row in rows]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/metrics/daily")
def daily_metrics(limit: int = Query(30, ge=1, le=180)) -> list[dict[str, Any]]:
    return query_table(
        "select * from daily_overview order by event_date desc limit ?",
        (limit,),
    )


@app.get("/metrics/categories")
def category_metrics(limit: int = Query(20, ge=1, le=100)) -> list[dict[str, Any]]:
    return query_table(
        "select category, sum(orders) orders, sum(gmv) gmv, sum(units) units "
        "from category_sales group by category order by gmv desc limit ?",
        (limit,),
    )


@app.get("/metrics/top-items")
def top_items(limit: int = Query(20, ge=1, le=100)) -> list[dict[str, Any]]:
    return query_table(
        "select * from top_items order by gmv desc limit ?",
        (limit,),
    )


@app.get("/metrics/retention")
def retention(limit: int = Query(100, ge=1, le=500)) -> list[dict[str, Any]]:
    return query_table(
        "select * from retention order by cohort_date desc, days_after asc limit ?",
        (limit,),
    )

