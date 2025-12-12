from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List, Dict, Any, Iterable, Optional

import pandas as pd
from tqdm import tqdm

from utils_data import row_to_text, label_from_attack_type, DEFAULT_COLMAP

def iter_csv_files(inp: Path) -> List[Path]:
    if inp.is_file() and inp.suffix.lower() == ".csv":
        return [inp]
    if inp.is_dir():
        return sorted([p for p in inp.rglob("*.csv")])
    raise FileNotFoundError(f"Input path not found: {inp}")

def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Convert MisbehaviorX CSV logs into JSONL prompt samples.")
    ap.add_argument("--input", required=True, help="Path to a CSV file or a folder containing CSV files.")
    ap.add_argument("--output", required=True, help="Output JSONL path (will be overwritten).")
    ap.add_argument("--attacks", nargs="*", default=None,
                    help="Optional whitelist of attack_type values to keep (e.g., Genuine RandomPosition DoS).")
    ap.add_argument("--max_rows", type=int, default=None, help="Optional max total rows to write (after filtering).")
    ap.add_argument("--shuffle", action="store_true", help="Shuffle rows before writing.")
    ap.add_argument("--seed", type=int, default=42)
    return ap.parse_args()

def main() -> None:
    args = parse_args()
    inp = Path(args.input)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    files = iter_csv_files(inp)
    if not files:
        raise RuntimeError(f"No CSV files found under: {inp}")

    dfs = []
    for f in tqdm(files, desc="Reading CSVs"):
        df = pd.read_csv(f)
        df["_source_file"] = str(f)
        dfs.append(df)

    df_all = pd.concat(dfs, ignore_index=True)

    # Filter by attack types if provided
    if args.attacks is not None and len(args.attacks) > 0:
        keep = set([str(a) for a in args.attacks])
        if "attack_type" not in df_all.columns:
            raise KeyError("Column 'attack_type' not found; cannot filter by --attacks.")
        df_all = df_all[df_all["attack_type"].astype(str).isin(keep)].copy()

    if args.shuffle:
        df_all = df_all.sample(frac=1.0, random_state=args.seed).reset_index(drop=True)

    if args.max_rows is not None:
        df_all = df_all.head(args.max_rows).copy()

    # Write JSONL
    n = 0
    with out.open("w", encoding="utf-8") as w:
        for i, row in tqdm(df_all.iterrows(), total=len(df_all), desc="Writing JSONL"):
            attack_type = row.get("attack_type", None)
            rec = {
                "id": int(i),
                "attack_type": None if attack_type is None else str(attack_type),
                "label": label_from_attack_type(attack_type),
                "text": row_to_text(row, DEFAULT_COLMAP),
                # include time if present (useful for time-slicing)
                "msg_rcv_time": row.get("msg_rcv_time", None),
                "source_file": row.get("_source_file", None),
            }
            w.write(json.dumps(rec, ensure_ascii=False) + "\n")
            n += 1

    print(f"Wrote {n} samples to {out}")

if __name__ == "__main__":
    main()
