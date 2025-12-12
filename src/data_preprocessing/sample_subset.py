from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List, Dict, Any

from sklearn.model_selection import train_test_split

def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    items = []
    with path.open("r", encoding="utf-8") as r:
        for line in r:
            line = line.strip()
            if not line:
                continue
            items.append(json.loads(line))
    return items

def write_jsonl(items: List[Dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as w:
        for obj in items:
            w.write(json.dumps(obj, ensure_ascii=False) + "\n")

def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Split a JSONL dataset into dev/test (stratified by label).")
    ap.add_argument("--input_jsonl", required=True)
    ap.add_argument("--out_dir", required=True)
    ap.add_argument("--test_size", type=float, default=0.2)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--max_total", type=int, default=None, help="Optional cap on total items before splitting.")
    return ap.parse_args()

def main() -> None:
    args = parse_args()
    inp = Path(args.input_jsonl)
    out_dir = Path(args.out_dir)

    items = read_jsonl(inp)
    if args.max_total is not None:
        items = items[:args.max_total]

    labels = [x.get("label", "unknown") for x in items]
    dev, test = train_test_split(
        items,
        test_size=args.test_size,
        random_state=args.seed,
        stratify=labels if len(set(labels)) > 1 else None,
    )

    write_jsonl(dev, out_dir / "dev.jsonl")
    write_jsonl(test, out_dir / "test.jsonl")

    print(f"Dev: {len(dev)}  Test: {len(test)}  -> {out_dir}")

if __name__ == "__main__":
    main()
