# How To Run TAU2 (Smoke + Prod + Adapter Analysis)

This guide documents the exact commands we use for:
- smoke tests,
- full production runs,
- adapter usefulness analysis.

All commands assume CWD:
- `/Users/rawhad/1_Projects/tau2-bench`

## 1) Prerequisites

1. Local model endpoints are up:
   - Agent wrapper (`served-adapter`): `http://localhost:8000/v1`
   - User model (`gpt-oss-120b`): `http://localhost:8101/v1`
2. TAU2 is runnable via `uv run tau2 ...`.
3. For analysis (Vertex Claude), Google auth is configured for your shell.

Optional quick health check:

```bash
uv run python - <<'PY'
import urllib.request
for url in [
    'http://localhost:8000/v1/chat/completions',
    'http://localhost:8101/v1/models',
]:
    try:
        with urllib.request.urlopen(url, timeout=3) as r:
            print(url, 'status', r.status)
    except Exception as e:
        print(url, 'error', type(e).__name__, e)
PY
```

Notes:
- `localhost:8000/v1/models` may return 404 on some wrappers; that can still be fine.
- For TAU2, what matters is that OpenAI-compatible chat completions work.

## 2) Smoke Test (5 tasks, 1 trial, high concurrency)

Use this exact command for `served-adapter` + `gpt-oss-120b`:

```bash
uv run tau2 run \
  --domain airline \
  --agent llm_agent \
  --agent-llm openai/served-adapter \
  --agent-llm-args '{"api_base":"http://localhost:8000/v1","api_key":"local","temperature":0}' \
  --user-llm openai/gpt-oss-120b \
  --user-llm-args '{"api_base":"http://localhost:8101/v1","api_key":"local","temperature":0}' \
  --num-trials 1 \
  --num-tasks 5 \
  --max-concurrency 50 \
  --task-split-name base \
  --save-to served_adapter_agent_user_120b_smoke_5task_1trial_mc50_<date>
```

Quick verify output:

```bash
uv run python - <<'PY'
import json
from pathlib import Path
p = Path('data/simulations/served_adapter_agent_user_120b_smoke_5task_1trial_mc50_<date>.json')
d = json.loads(p.read_text())
sims = d.get('simulations', [])
print('num_sims', len(sims))
print('rewards', [s.get('reward_info', {}).get('reward') for s in sims])
PY
```

## 3) Full Production Run (50 tasks, 3 trials)

```bash
uv run tau2 run \
  --domain airline \
  --agent llm_agent \
  --agent-llm openai/served-adapter \
  --agent-llm-args '{"api_base":"http://localhost:8000/v1","api_key":"local","temperature":0}' \
  --user-llm openai/gpt-oss-120b \
  --user-llm-args '{"api_base":"http://localhost:8101/v1","api_key":"local","temperature":0}' \
  --num-trials 3 \
  --num-tasks 50 \
  --max-concurrency 50 \
  --task-split-name base \
  --save-to served_adapter_agent_user_120b_airline_full_3trials_<date>_prod_mc50
```

### Rename simulation artifact with commit hash

```bash
mv "data/simulations/served_adapter_agent_user_120b_airline_full_3trials_<date>_prod_mc50.json" \
   "data/simulations/served_adapter_agent_user_120b_airline_full_3trials_<date>_prod_mc50_<commit_hash>.json"
```

Example commit hash used previously:
- `99262e9f3c35e9ba77804451bddd8746f3fd2541`

## 4) Generate Adapter Usefulness Analysis

Script:
- `scripts/analyze_adapter_usefulness.py`

What it does:
- Reads simulation traces.
- Sends trace snapshots to Claude Opus judge.
- Returns strict structured JSON (schema-enforced).
- Tracks major API failures vs adapter fix outcomes.
- Supports async concurrency via `asyncio.Semaphore`.
- Shows progress via `tqdm`.

### Smoke analysis (1 trace)

```bash
uv run --with "google-cloud-aiplatform>=1.38" python scripts/analyze_adapter_usefulness.py \
  --simulation-file data/simulations/served_adapter_agent_user_120b_airline_full_3trials_<date>_prod_mc50_<commit_hash>.json \
  --max-traces 1 \
  --max-concurrency 1 \
  --model "vertex_ai/claude-opus-4-6@default" \
  --vertex-location us-east5 \
  --thinking-budget-tokens 10000 \
  --max-tokens 16000 \
  --output notes/adapter_usefulness_smoke_<commit_hash>.json
```

### Full analysis (all traces, prod mode)

```bash
uv run --with "google-cloud-aiplatform>=1.38" python scripts/analyze_adapter_usefulness.py \
  --simulation-file data/simulations/served_adapter_agent_user_120b_airline_full_3trials_<date>_prod_mc50_<commit_hash>.json \
  --max-concurrency 10 \
  --model "vertex_ai/claude-opus-4-6@default" \
  --vertex-location us-east5 \
  --thinking-budget-tokens 10000 \
  --max-tokens 16000 \
  --output notes/adapter_usefulness_full_mc10_<commit_hash>.json
```

## 5) Important Runtime Notes

1. For Claude thinking mode, script sets the required behavior:
   - thinking budget: `10000`
   - max output tokens: `16000`
2. LiteLLM warnings like "model isn't mapped yet" are usually non-fatal (cost = 0).
3. If run fails with connection errors, usually `localhost:8101` (user model) is down.
4. If Vertex complains about region/model availability, use `--vertex-location us-east5`.

## 6) Minimal Checklist

1. Run smoke test (5x1).
2. Confirm non-empty simulation JSON.
3. Run full prod (50x3).
4. Rename artifact with commit hash.
5. Run smoke analysis (1 trace).
6. Run full analysis with `--max-concurrency 10`.
