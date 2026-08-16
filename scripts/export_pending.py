#!/usr/bin/env python3
"""Export pending reviews from reviews_master.xlsx for the next labeling wave."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import openpyxl

KEEP = [
    "row_id",
    "review_key",
    "listing_asin",
    "ASIN",
    "品牌",
    "商品标题",
    "型号",
    "星级",
    "标题",
    "内容",
    "所属国家",
    "评论时间",
    "VP评论",
    "Vine Voice评论",
    "flag_non_us",
    "flag_accessory_model",
]


def export(master: Path, out: Path, limit: int | None, skip_accessory: bool):
    wb = openpyxl.load_workbook(master, read_only=True, data_only=True)
    ws = wb["reviews_master"]
    rows = list(ws.iter_rows(values_only=True))
    wb.close()
    header = list(rows[0])
    idx = {h: i for i, h in enumerate(header)}
    items = []
    for row in rows[1:]:
        rec = {h: row[i] if i < len(row) else None for h, i in idx.items()}
        if rec.get("annotate_status") == "done":
            continue
        if skip_accessory and rec.get("flag_accessory_model") == "Y":
            continue
        items.append({k: rec.get(k) for k in KEEP if k in rec})
        if limit and len(items) >= limit:
            break
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"pending={len(items)} out={out}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--master", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--include-accessory", action="store_true")
    args = parser.parse_args()
    export(
        Path(args.master),
        Path(args.out),
        args.limit or None,
        skip_accessory=not args.include_accessory,
    )


if __name__ == "__main__":
    main()
