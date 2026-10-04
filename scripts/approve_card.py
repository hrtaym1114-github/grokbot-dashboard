#!/usr/bin/env python3
"""Set one dashboard card to 承認. Refuses unknown ids and 投稿済み."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

JST = ZoneInfo("Asia/Tokyo")
ROOT = Path(__file__).resolve().parents[1]


def next_x_slot(now: datetime) -> datetime:
    d = now.astimezone(JST).replace(second=0, microsecond=0)
    for _ in range(24 * 60):
        d += timedelta(minutes=1)
        if d.minute == 7 and d.hour >= 4:
            return d
    return d


def main() -> int:
    card_id = os.environ.get("CARD_ID", "").strip()
    if not card_id or "/" in card_id or ".." in card_id:
        print("CARD_ID が空か不正", file=sys.stderr)
        return 1
    path = Path(os.environ.get("JSON_PATH", ROOT / "docs/data/latest.json"))
    data = json.loads(path.read_text())
    card = next((c for c in data.get("cards") or [] if c.get("id") == card_id), None)
    if card is None:
        print(f"カードがない: {card_id}", file=sys.stderr)
        return 1
    status = card.get("status")
    if status == "投稿済み":
        print("投稿済みなので変えない")
        return 0
    if status == "承認":
        print("すでに承認")
        return 0
    if status not in ("未投稿", "保留"):
        print(f"承認できない状態: {status}", file=sys.stderr)
        return 1
    card["status"] = "承認"
    if card.get("channel") == "X":
        card["scheduledAt"] = next_x_slot(datetime.now(JST)).isoformat(timespec="minutes")
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    print(f"承認: {card_id} {card.get('scheduledAt') or ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
