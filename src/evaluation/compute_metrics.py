from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Any, List

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
    ap = argparse.ArgumentParser(description="Compute basic metrics for attacker vs genuine predictions.")
    ap.add_argument("--predictions_jsonl", required=True)
    ap.add_argument("--out_json", required=True)
    return ap.parse_args()

def safe_div(a: float, b: float) -> float:
    return float(a) / float(b) if b else 0.0

def main() -> None:
    args = parse_args()
    preds = read_jsonl(Path(args.predictions_jsonl))

    total = 0
    correct = 0
    unknown = 0

    per = {
        "attacker": {"n": 0, "correct": 0},
        "genuine": {"n": 0, "correct": 0},
    }

    for r in preds:
        gold = str(r.get("label", "unknown")).lower()
        pred = str(r.get("pred", "unknown")).lower()

        if gold not in per:
            continue  # skip unknown labels
        total += 1
        per[gold]["n"] += 1

        if pred not in ["attacker", "genuine"]:
            unknown += 1
            continue

        if pred == gold:
            correct += 1
            per[gold]["correct"] += 1

    metrics = {
        "n": total,
        "overall_accuracy": safe_div(correct, total),
        "unknown_rate": safe_div(unknown, total),
        "attacker_accuracy": safe_div(per["attacker"]["correct"], per["attacker"]["n"]),
        "genuine_accuracy": safe_div(per["genuine"]["correct"], per["genuine"]["n"]),
    }

    out = Path(args.out_json)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print(json.dumps(metrics, indent=2))

if __name__ == "__main__":
    main()
