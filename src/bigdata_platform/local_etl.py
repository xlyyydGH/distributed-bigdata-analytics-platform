from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

import pandas as pd

from .config import MARTS_DIR, RAW_DIR, SQLITE_DB, ensure_dirs


def _rate(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    result = numerator / denominator.replace(0, pd.NA)
    return result.fillna(0).round(4)


def load_raw(raw_dir: Path = RAW_DIR) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    users = pd.read_csv(raw_dir / "users.csv")
    items = pd.read_csv(raw_dir / "items.csv")
    events = pd.read_csv(raw_dir / "events.csv")
    events["event_time"] = pd.to_datetime(events["event_time"])
    events["event_date"] = pd.to_datetime(events["event_date"]).dt.date.astype(str)
    events["gmv"] = (events["quantity"] * events["price"]).where(events["event_type"].eq("purchase"), 0)
    return users, items, events


def build_daily_overview(events: pd.DataFrame) -> pd.DataFrame:
    base = events.groupby("event_date").agg(
        dau=("user_id", "nunique"),
        sessions=("session_id", "nunique"),
        events=("event_id", "count"),
        gmv=("gmv", "sum"),
    )
    type_counts = events.pivot_table(
        index="event_date",
        columns="event_type",
        values="event_id",
        aggfunc="count",
        fill_value=0,
    )
    overview = base.join(type_counts, how="left").fillna(0).reset_index()
    for col in ["impression", "click", "add_cart", "purchase"]:
        if col not in overview:
            overview[col] = 0
    overview["ctr"] = _rate(overview["click"], overview["impression"])
    overview["cart_rate"] = _rate(overview["add_cart"], overview["click"])
    overview["cvr"] = _rate(overview["purchase"], overview["click"])
    overview["arpu"] = _rate(overview["gmv"], overview["dau"])
    return overview.sort_values("event_date")


def build_category_sales(events: pd.DataFrame, items: pd.DataFrame) -> pd.DataFrame:
    enriched = events.merge(items[["item_id", "item_name", "category"]], on="item_id", how="left")
    purchases = enriched[enriched["event_type"].eq("purchase")].copy()
    result = purchases.groupby(["event_date", "category"]).agg(
        orders=("event_id", "count"),
        buyers=("user_id", "nunique"),
        units=("quantity", "sum"),
        gmv=("gmv", "sum"),
    ).reset_index()
    result["avg_order_value"] = _rate(result["gmv"], result["orders"])
    return result.sort_values(["event_date", "gmv"], ascending=[True, False])


def build_top_items(events: pd.DataFrame, items: pd.DataFrame, top_n: int = 50) -> pd.DataFrame:
    enriched = events.merge(items[["item_id", "item_name", "category"]], on="item_id", how="left")
    purchases = enriched[enriched["event_type"].eq("purchase")].copy()
    result = purchases.groupby(["item_id", "item_name", "category"]).agg(
        orders=("event_id", "count"),
        buyers=("user_id", "nunique"),
        units=("quantity", "sum"),
        gmv=("gmv", "sum"),
    ).reset_index()
    result["avg_order_value"] = _rate(result["gmv"], result["orders"])
    return result.sort_values("gmv", ascending=False).head(top_n)


def build_retention(events: pd.DataFrame) -> pd.DataFrame:
    activity = events[["user_id", "event_date"]].drop_duplicates()
    first_seen = activity.groupby("user_id")["event_date"].min().rename("cohort_date").reset_index()
    joined = activity.merge(first_seen, on="user_id", how="inner")
    joined["event_date_dt"] = pd.to_datetime(joined["event_date"])
    joined["cohort_date_dt"] = pd.to_datetime(joined["cohort_date"])
    joined["days_after"] = (joined["event_date_dt"] - joined["cohort_date_dt"]).dt.days
    joined = joined[joined["days_after"].isin([0, 1, 7, 14, 30])]
    cohort_size = first_seen.groupby("cohort_date").agg(cohort_users=("user_id", "nunique")).reset_index()
    retained = joined.groupby(["cohort_date", "days_after"]).agg(retained_users=("user_id", "nunique")).reset_index()
    result = retained.merge(cohort_size, on="cohort_date", how="left")
    result["retention_rate"] = _rate(result["retained_users"], result["cohort_users"])
    return result.sort_values(["cohort_date", "days_after"])


def write_outputs(marts: dict[str, pd.DataFrame]) -> None:
    ensure_dirs()
    for name, frame in marts.items():
        frame.to_csv(MARTS_DIR / f"{name}.csv", index=False, encoding="utf-8-sig")
    with sqlite3.connect(SQLITE_DB) as conn:
        for name, frame in marts.items():
            frame.to_sql(name, conn, if_exists="replace", index=False)


def run() -> dict[str, pd.DataFrame]:
    users, items, events = load_raw()
    marts = {
        "daily_overview": build_daily_overview(events),
        "category_sales": build_category_sales(events, items),
        "top_items": build_top_items(events, items),
        "retention": build_retention(events),
    }
    write_outputs(marts)
    return marts


def main() -> None:
    parser = argparse.ArgumentParser(description="Run local Pandas ETL and write mart CSV/SQLite outputs.")
    parser.parse_args()
    marts = run()
    print(f"ETL finished. Tables: {', '.join(marts)}")
    print(f"CSV output: {MARTS_DIR}")
    print(f"SQLite output: {SQLITE_DB}")


if __name__ == "__main__":
    main()

