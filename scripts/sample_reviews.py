#!/usr/bin/env python3
"""Stratified sample of pending reviews for a labeling wave."""

from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from pathlib import Path

import openpyxl


def sample(master: Path, n: int, seed: int, only_pending: bool) -> list[dict]:
    wb = openpyxl.load_workbook(master, read_only=True, data_only=True)
    ws = wb["reviews_master"]
    rows = list(ws.iter_rows(values_only=True))
    wb.close()
    header = list(rows[0])
    idx = {h: i for i, h in enumerate(header)}
    records = []
    for row in rows[1:]:
        rec = {h: row[i] if i < len(row) else None for h, i in idx.items()}
        if only_pending and rec.get("annotate_status") == "done":
            continue
        records.append(rec)

    buckets = defaultdict(list)
    for rec in records:
        asin = rec.get("ASIN") or "NA"
        try:
            star = int(rec.get("星级") or 0)
        except (TypeError, ValueError):
            star = 0
        buckets[(asin, star)].append(rec)

    rng = random.Random(seed)
    asins = sorted({k[0] for k in buckets})
    # guarantee coverage: at least 1 per asin-star if possible, then fill
    picked = []
    used = set()

    def take(rec):
        key = rec.get("row_id")
        if key in used:
            return
        used.add(key)
        picked.append(rec)

    # first pass: one from each asin x star
    for asin in asins:
        for star in (1, 2, 3, 4, 5):
            pool = buckets.get((asin, star), [])
            if pool:
                take(rng.choice(pool))

    # second pass: proportional fill, oversample 1-3 star
    remaining = [r for r in records if r.get("row_id") not in used]
    weights = []
    for r in remaining:
        try:
            star = int(r.get("星级") or 0)
        except (TypeError, ValueError):
            star = 0
        w = {1: 3.0, 2: 3.0, 3: 2.5, 4: 1.0, 5: 0.8}.get(star, 1.0)
        weights.append(w)

    while len(picked) < min(n, len(records)) and remaining:
        total = sum(weights)
        draw = rng.random() * total
        acc = 0
        choice = 0
        for i, w in enumerate(weights):
            acc += w
            if acc >= draw:
                choice = i
                break
        take(remaining.pop(choice))
        weights.pop(choice)

    picked = picked[:n]
    picked.sort(key=lambda r: (r.get("品牌") or "", r.get("ASIN") or "", r.get("row_id") or 0))
    out = []
    for rec in picked:
        out.append(
            {
                "row_id": rec.get("row_id"),
                "review_key": rec.get("review_key"),
                "listing_asin": rec.get("listing_asin"),
                "ASIN": rec.get("ASIN"),
                "品牌": rec.get("品牌"),
                "商品标题": rec.get("商品标题"),
                "型号": rec.get("型号"),
                "星级": rec.get("星级"),
                "标题": rec.get("标题"),
                "内容": rec.get("内容"),
                "所属国家": rec.get("所属国家"),
                "评论时间": rec.get("评论时间"),
                "VP评论": rec.get("VP评论"),
                "Vine Voice评论": rec.get("Vine Voice评论"),
                "flag_non_us": rec.get("flag_non_us"),
                "flag_accessory_model": rec.get("flag_accessory_model"),
            }
        )
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--master", required=True)
    parser.add_argument("--n", type=int, default=80)
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--out", required=True)
    parser.add_argument("--include-done", action="store_true")
    args = parser.parse_args()
    items = sample(Path(args.master), args.n, args.seed, only_pending=not args.include_done)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"sampled={len(items)} out={out}")


if __name__ == "__main__":
    main()
