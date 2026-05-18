from __future__ import annotations

import argparse
import random
from datetime import datetime, timedelta

import pandas as pd

from .config import RAW_DIR, ensure_dirs


PROVINCES = ["北京", "上海", "广东", "浙江", "江苏", "山东", "四川", "湖北", "陕西"]
DEVICES = ["ios", "android", "web"]
CATEGORIES = ["数码", "美妆", "食品", "服饰", "图书", "家居", "运动"]
EVENT_FLOW = ["impression", "click", "add_cart", "purchase"]


def generate_users(user_count: int, seed: int) -> pd.DataFrame:
    random.seed(seed)
    rows = []
    start = datetime(2022, 1, 1)
    for user_id in range(1, user_count + 1):
        rows.append(
            {
                "user_id": f"u{user_id:06d}",
                "province": random.choice(PROVINCES),
                "device": random.choices(DEVICES, weights=[0.42, 0.45, 0.13])[0],
                "register_date": (start + timedelta(days=random.randint(0, 720))).date().isoformat(),
            }
        )
    return pd.DataFrame(rows)


def generate_items(item_count: int, seed: int) -> pd.DataFrame:
    random.seed(seed + 7)
    rows = []
    for item_id in range(1, item_count + 1):
        category = random.choice(CATEGORIES)
        base_price = round(random.uniform(19, 799), 2)
        rows.append(
            {
                "item_id": f"sku{item_id:05d}",
                "item_name": f"{category}商品{item_id:05d}",
                "category": category,
                "base_price": base_price,
            }
        )
    return pd.DataFrame(rows)


def _sample_event_type() -> str:
    return random.choices(EVENT_FLOW, weights=[0.58, 0.25, 0.1, 0.07])[0]


def generate_events(
    users: pd.DataFrame,
    items: pd.DataFrame,
    event_count: int,
    seed: int,
    start_date: str,
    days: int,
) -> pd.DataFrame:
    random.seed(seed + 13)
    start = datetime.fromisoformat(start_date)
    user_ids = users["user_id"].tolist()
    item_records = items.to_dict("records")
    rows = []
    for event_id in range(1, event_count + 1):
        item = random.choice(item_records)
        event_type = _sample_event_type()
        event_time = start + timedelta(
            days=random.randint(0, days - 1),
            seconds=random.randint(0, 86399),
        )
        quantity = random.randint(1, 3) if event_type == "purchase" else 0
        price = round(item["base_price"] * random.uniform(0.82, 1.18), 2)
        rows.append(
            {
                "event_id": f"e{event_id:09d}",
                "event_time": event_time.strftime("%Y-%m-%d %H:%M:%S"),
                "event_date": event_time.date().isoformat(),
                "session_id": f"s{random.randint(1, event_count // 3):08d}",
                "user_id": random.choice(user_ids),
                "item_id": item["item_id"],
                "event_type": event_type,
                "quantity": quantity,
                "price": price,
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic raw data for the big data demo.")
    parser.add_argument("--users", type=int, default=5000)
    parser.add_argument("--items", type=int, default=600)
    parser.add_argument("--events", type=int, default=80000)
    parser.add_argument("--days", type=int, default=90)
    parser.add_argument("--start-date", default="2024-01-01")
    parser.add_argument("--seed", type=int, default=202405)
    args = parser.parse_args()

    ensure_dirs()
    users = generate_users(args.users, args.seed)
    items = generate_items(args.items, args.seed)
    events = generate_events(users, items, args.events, args.seed, args.start_date, args.days)

    users.to_csv(RAW_DIR / "users.csv", index=False, encoding="utf-8-sig")
    items.to_csv(RAW_DIR / "items.csv", index=False, encoding="utf-8-sig")
    events.to_csv(RAW_DIR / "events.csv", index=False, encoding="utf-8-sig")
    print(f"Generated users={len(users)}, items={len(items)}, events={len(events)} in {RAW_DIR}")


if __name__ == "__main__":
    main()

