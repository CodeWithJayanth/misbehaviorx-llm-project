# MisbehaviorX LLM-based Misbehavior Detection (Term Project)

This repository contains code artifacts and the report for a term project that explores **LLM-based misbehavior detection** on the **MisbehaviorX** V2X dataset. The project converts V2X log rows (CSV) into prompt-ready text/JSONL, runs **zero-shot / few-shot** prompting on LLMs, and evaluates predictions as **attacker vs genuine**.

**Report:** `report/misbehaviorx_report.pdf`

## What’s included
- CSV → JSONL preprocessing (`src/data_preprocessing/`)
- Prompt templates + prompting runner (`src/prompting/`)
- Metrics (`src/evaluation/`)
- Example JSONL files (`examples/`)
- Config examples (`configs/`)
- Project report (`report/`)

## What’s NOT included
- The full MisbehaviorX dataset CSV logs (not uploaded to GitHub due to size/terms).

---

## Setup

### 1) Create a virtual environment (Windows)

**PowerShell**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**CMD**
```bat
python -m venv .venv
.\.venv\Scripts\activate
```

### 2) Install dependencies
```bash
pip install -r requirements.txt
```

### 3) Set API keys (DO NOT hardcode keys in code)
Create environment variables (example for Groq):

**PowerShell**
```powershell
$env:GROQ_API_KEY="YOUR_KEY_HERE"
```

**CMD**
```bat
set GROQ_API_KEY=YOUR_KEY_HERE
```

Or create a local `.env` file (never commit it) and use your shell to load it.

---

## Quickstart workflow

### A) Convert CSV → JSONL
If you have one CSV:
```bash
python src/data_preprocessing/csv_to_jsonl.py --input path/to/file.csv --output data/prompts.jsonl
```

If you have a folder of CSVs:
```bash
python src/data_preprocessing/csv_to_jsonl.py --input path/to/csv_folder --output data/prompts.jsonl
```

### B) Split into dev/test subsets
```bash
python src/data_preprocessing/sample_subset.py --input_jsonl data/prompts.jsonl --out_dir data/splits --test_size 0.2 --seed 42
```

This creates:
- `data/splits/dev.jsonl`
- `data/splits/test.jsonl`

### C) Run prompting (zero-shot or few-shot)
Zero-shot:
```bash
python src/prompting/run_prompting.py --mode zero_shot --provider groq --model llama-3.1-8b-instant --input_jsonl data/splits/test.jsonl --output_jsonl results/preds_zero.jsonl
```

Few-shot:
```bash
python src/prompting/run_prompting.py --mode few_shot --provider groq --model llama-3.1-8b-instant --few_shot_examples examples/few_shot_examples.txt --input_jsonl data/splits/test.jsonl --output_jsonl results/preds_few.jsonl
```

### D) Compute metrics
```bash
python src/evaluation/compute_metrics.py --predictions_jsonl results/preds_zero.jsonl --out_json results/metrics_zero.json
```



---

## Repo layout

```text
misbehaviorx-llm-project/
├─ README.md
├─ requirements.txt
├─ .gitignore
├─ .env.example
├─ src/
│  ├─ data_preprocessing/
│  │  ├─ csv_to_jsonl.py
│  │  ├─ sample_subset.py
│  │  └─ utils_data.py
│  ├─ prompting/
│  │  ├─ prompt_templates.py
│  │  ├─ model_clients.py
│  │  └─ run_prompting.py
│  └─ evaluation/
│     ├─ compute_metrics.py
│     └─ time_slice_metrics.py
├─ configs/
│  └─ config_groq_llama31_8b.json
├─ examples/
│  ├─ example_input.jsonl
│  ├─ example_output.jsonl
│  └─ few_shot_examples.txt
└─ report/
   └─ misbehaviorx_report.pdf
```

## Notes
- Keep naming consistent (attack type strings) between preprocessing, prompts, and evaluation.
