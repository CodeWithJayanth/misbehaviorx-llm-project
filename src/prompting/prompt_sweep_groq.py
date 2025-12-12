from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple

import pandas as pd
from sklearn.model_selection import train_test_split
from tqdm import tqdm

from model_clients import build_client, extract_label
from prompt_templates import PROMPTS

def row_to_text(row: pd.Series) -> str:
    # Keep consistent with the report style; adjust column names if your CSV differs.
    return (
        f"Receiver vehicle {row['rv_id']} received a message from vehicle {row['hv_id']} "
        f"at time {row['msg_rcv_time']:.3f} s.\n"
        f"Sender (hv) position: ({row['hv_pos_x']:.1f}, {row['hv_pos_y']:.1f}), "
        f"speed: {row['hv_speed']:.1f} m/s, heading: {row['hv_heading']:.1f} deg.\n"
        f"Receiver (rv) position: ({row['rv_pos_x']:.1f}, {row['rv_pos_y']:.1f}), "
        f"speed: {row['rv_speed']:.1f} m/s, heading: {row['rv_heading']:.1f} deg.\n"
        f"Target id: {row['target_id']}, EEBL warning: {row['eebl_warn']}, IMA warning: {row['ima_warn']}."
    )

def load_dev_test(csv_path: Path, attack_pos: str, attack_neg: str = "Genuine", seed: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.read_csv(csv_path)

    if "attack_type" not in df.columns:
        raise KeyError("CSV must contain an 'attack_type' column.")

    # Keep only the two classes for binary testing
    df = df[df["attack_type"].isin([attack_neg, attack_pos])].copy()

    # Map to binary label
    df["label"] = df["attack_type"].map({
        attack_neg: "genuine",
        attack_pos: "attacker"
    })

    df["text"] = df.apply(row_to_text, axis=1)
    df = df[["text", "label", "attack_type"]]

    dev_df, test_df = train_test_split(df, test_size=0.2, random_state=seed, stratify=df["label"])
    return dev_df.reset_index(drop=True), test_df.reset_index(drop=True)

def eval_template(client, template: str, df: pd.DataFrame, max_rows: int) -> Dict[str, float]:
    n = min(len(df), max_rows)
    sub = df.iloc[:n]

    total = 0
    correct = 0
    unknown = 0
    n_att = 0
    n_gen = 0
    c_att = 0
    c_gen = 0

    for _, row in tqdm(sub.iterrows(), total=len(sub), leave=False):
        prompt = template.format(LOG_TEXT=row["text"], FEW_SHOT_EXAMPLES="")
        resp = client.generate(prompt)
        pred = extract_label(resp.text)

        gold = row["label"]
        total += 1

        if pred not in ["attacker", "genuine"]:
            unknown += 1
            continue

        if pred == gold:
            correct += 1
            if gold == "attacker":
                c_att += 1
            else:
                c_gen += 1

        if gold == "attacker":
            n_att += 1
        else:
            n_gen += 1

    def safe_div(a, b): return a / b if b else 0.0

    return {
        "overall_accuracy": safe_div(correct, total),
        "unknown_rate": safe_div(unknown, total),
        "attacker_accuracy": safe_div(c_att, n_att),
        "genuine_accuracy": safe_div(c_gen, n_gen),
        "n": total
    }

def parse_args():
    ap = argparse.ArgumentParser(description="Prompt sweep (dev select best prompt, then test) using Groq models.")
    ap.add_argument("--csv_path", required=True)
    ap.add_argument("--attack", required=True, help="Attack key (must exist in PROMPTS), e.g., RandomPosition")
    ap.add_argument("--provider", default="groq", choices=["groq"])
    ap.add_argument("--model", required=True)
    ap.add_argument("--mode", default="zero_shot", choices=["zero_shot", "few_shot"])
    ap.add_argument("--dev_max", type=int, default=200)
    ap.add_argument("--test_max", type=int, default=500)
    ap.add_argument("--seed", type=int, default=42)
    return ap.parse_args()

def main():
    args = parse_args()
    csv_path = Path(args.csv_path)

    if args.attack not in PROMPTS:
        raise KeyError(f"Attack '{args.attack}' not found in PROMPTS. Available: {list(PROMPTS.keys())}")

    dev_df, test_df = load_dev_test(csv_path, attack_pos=args.attack, seed=args.seed)
    print(f"Dev size: {len(dev_df)}  Test size: {len(test_df)}")

    client = build_client(args.provider, args.model, temperature=0.0, max_tokens=16)

    # For compatibility with your old script, we evaluate a small set of prompt variants.
    # Here: we just evaluate the project templates (mode-specific) for the chosen attack.
    templates = [PROMPTS[args.attack][args.mode]]

    dev_results = []
    for i, tmpl in enumerate(templates):
        m = eval_template(client, tmpl, dev_df, max_rows=args.dev_max)
        print(f"\n--- Template {i} on DEV ({args.mode}) ---")
        print(json.dumps(m, indent=2))
        dev_results.append((i, m["overall_accuracy"], m))

    best_i, best_acc, _best_m = max(dev_results, key=lambda x: x[1])
    best_tmpl = templates[best_i]
    print(f"\nBest template on dev: #{best_i} (acc={best_acc:.3f})")

    test_n = min(len(test_df), args.test_max)
    test_sample = test_df.sample(n=test_n, random_state=args.seed) if test_n < len(test_df) else test_df

    mtest = eval_template(client, best_tmpl, test_sample, max_rows=test_n)
    print("\n--- Best template on TEST ---")
    print(json.dumps(mtest, indent=2))
    print(f"(Evaluated on {test_n} test rows)")

if __name__ == "__main__":
    main()
