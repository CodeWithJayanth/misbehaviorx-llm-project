from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import math
import csv

def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    items = []
    with path.open("r", encoding="utf-8") as r:
        for line in r:
            line = line.strip()
            if not line:
                continue
            items.append(json.loads(line))
    return items

def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Compute accuracy per time bin (time-sliced evaluation).")
    ap.add_argument("--predictions_jsonl", required=True)
    ap.add_argument("--time_field", default="msg_rcv_time")
    ap.add_argument("--bin_seconds", type=float, default=5.0)
    ap.add_argument("--out_csv", required=True)
    return ap.parse_args()

def extract_time(x: Any) -> Optional[float]:
    try:
        if x is None:
            return None
        return float(x)
    except Exception:
        return None

def main() -> None:
    args = parse_args()
    items = read_jsonl(Path(args.predictions_jsonl))

    # bin -> counters
    bins: Dict[int, Dict[str, float]] = {}

    for r in items:
        t = extract_time(r.get(args.time_field))
        if t is None:
            continue
        b = int(math.floor(t / args.bin_seconds))
        gold = str(r.get("label", "unknown")).lower()
        pred = str(r.get("pred", "unknown")).lower()

        if b not in bins:
            bins[b] = {"n": 0, "correct": 0, "unknown": 0}

        if gold not in ["attacker", "genuine"]:
            continue

        bins[b]["n"] += 1
        if pred not in ["attacker", "genuine"]:
            bins[b]["unknown"] += 1
        elif pred == gold:
            bins[b]["correct"] += 1

    out = Path(args.out_csv)
    out.parent.mkdir(parents=True, exist_ok=True)

    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["bin_index", "time_start", "time_end", "n", "accuracy", "unknown_rate"])
        for b in sorted(bins.keys()):
            n = bins[b]["n"]
            acc = (bins[b]["correct"] / n) if n else 0.0
            unk = (bins[b]["unknown"] / n) if n else 0.0
            w.writerow([b, b * args.bin_seconds, (b + 1) * args.bin_seconds, int(n), acc, unk])

    print(f"Wrote time-sliced metrics to {out}")

if __name__ == "__main__":
    main()
