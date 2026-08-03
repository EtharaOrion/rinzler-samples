# rinzler Harbor task 965fda63-3c1b-5c26-b81d-b8d98d4491a4

Tier `tier_easy` · seed `8211` · config `tier_easy`.

Operate a simulated AI startup through the `rinzler` CLI over a one-year horizon;
stay solvent, complete client tasks, and flag adversarial (RAT) clients by evidence.

## Run against an LLM agent (from the harness root)
```bash
uv run rinzler run --config <bundle>/config.toml --seed 8211
```

## Run deterministically (no API key)
```bash
uv run python scripts/bot_runner.py --bot greedy --config <bundle>/config.toml --seed 8211
```

## Grade a rollout
```bash
uv run python tests/checkers.py --rollout <rollout.json> --live-state <live_state.json> --bundle-checkers tests/bundle_checkers.py
```
