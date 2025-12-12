from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

from tqdm import tqdm

from prompt_templates import PROMPTS
from model_clients import build_client, extract_label

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
    ap = argparse.ArgumentParser(description="Run zero-shot or few-shot prompting on a JSONL dataset.")
    ap.add_argument("--mode", choices=["zero_shot", "few_shot"], required=True)
    ap.add_argument("--provider", choices=["groq"], default="groq")
    ap.add_argument("--model", required=True, help="Model name for the provider (e.g., llama-3.1-8b-instant).")
    ap.add_argument("--input_jsonl", required=True)
    ap.add_argument("--output_jsonl", required=True)

    ap.add_argument("--attack", default=None, help="Optional fixed attack key in PROMPTS (else use item['attack_type']).")
    ap.add_argument("--few_shot_examples", default=None, help="Path to text file of few-shot examples (inserted into template).")

    ap.add_argument("--max_rows", type=int, default=None)
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--max_tokens", type=int, default=16)
    return ap.parse_args()

def main() -> None:
    args = parse_args()
    inp = Path(args.input_jsonl)
    out = Path(args.output_jsonl)

    items = read_jsonl(inp)
    if args.max_rows is not None:
        items = items[:args.max_rows]

    client = build_client(args.provider, args.model, temperature=args.temperature, max_tokens=args.max_tokens)

    few_block = ""
    if args.mode == "few_shot":
        if args.few_shot_examples:
            few_block = Path(args.few_shot_examples).read_text(encoding="utf-8")
        else:
            # safe default: empty block
            few_block = ""

    out_items = []
    for item in tqdm(items, desc=f"Prompting ({args.mode})"):
        attack_key = args.attack or item.get("attack_type")
        if not attack_key:
            raise KeyError("No attack type found. Provide --attack or ensure JSONL has 'attack_type'.")
        if attack_key not in PROMPTS:
            raise KeyError(f"Attack key '{attack_key}' not found in PROMPTS. Available: {list(PROMPTS.keys())}")

        tmpl = PROMPTS[attack_key][args.mode]
        prompt = tmpl.format(FEW_SHOT_EXAMPLES=few_block, LOG_TEXT=item.get("text", ""))

        resp = client.generate(prompt)
        pred = extract_label(resp.text)

        out_items.append({
            "id": item.get("id"),
            "attack_type": item.get("attack_type"),
            "label": item.get("label"),
            "pred": pred,
            "mode": args.mode,
            "provider": args.provider,
            "model": args.model,
            "raw_text": resp.text,
            # keep optional fields if present
            "msg_rcv_time": item.get("msg_rcv_time", None),
            "source_file": item.get("source_file", None),
        })

    write_jsonl(out_items, out)
    print(f"Wrote predictions: {out}  (n={len(out_items)})")

if __name__ == "__main__":
    main()
