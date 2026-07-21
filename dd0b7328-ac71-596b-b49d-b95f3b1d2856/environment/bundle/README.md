# Bundle dd0b7328-ac71-596b-b49d-b95f3b1d2856

Run this bundle via the vendored YC-Bench harness at the parent-project `harness/` submodule.

## Prerequisites

- Python 3.12+
- `uv` package manager
- An LLM API key (any LiteLLM-compatible provider). Set one of `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`, `OPENROUTER_API_KEY` in a `.env` at the parent project root.

## Run against an LLM agent

From the parent project root (the directory containing `harness/`):

```bash
uv run --project harness yc-bench run \
  --config dataset/dd0b7328-ac71-596b-b49d-b95f3b1d2856/config.toml \
  --seed 7100202
```

Rollout JSON emitted to `harness/results/`. SQLite state to `harness/db/`.

## Run deterministically (no API key)

```bash
uv run --project harness python harness/scripts/bot_runner.py \
  --bot greedy \
  --config dataset/dd0b7328-ac71-596b-b49d-b95f3b1d2856/config.toml \
  --seed 7100202
```

Bot strategies: `greedy`, `random`, `throughput`, `prestige`.

## Grade the rollout

```bash
uv run --project seed python dataset/dd0b7328-ac71-596b-b49d-b95f3b1d2856/checkers.py \
  <path-to-rollout.json> \
  <path-to-live_state.yaml>
```

`live_state.yaml` is assembled from `manifest.yaml` + `seed/private/dd0b7328-ac71-596b-b49d-b95f3b1d2856/reference_expectations.yaml` + `seed/private/dd0b7328-ac71-596b-b49d-b95f3b1d2856/canaries.yaml` at grading time by the outer runner (out of scope for this bundle README; the auditor uses CRUCIBLE's independent re-scan of the rollout for canary + provenance).
