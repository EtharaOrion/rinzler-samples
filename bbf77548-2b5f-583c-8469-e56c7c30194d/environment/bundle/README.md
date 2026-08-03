# rinzler Harbor task bbf77548-2b5f-583c-8469-e56c7c30194d

Tier `tier_expert` · seed `8260` · config `tier_expert`.

Operate a simulated AI startup through the `rinzler` CLI over a one-year horizon;
stay solvent, complete client tasks, and flag adversarial (RAT) clients by evidence.

## Run against an LLM agent (from the harness root)
```bash
uv run rinzler run --config <bundle>/config.toml --seed 8260
```

## Run deterministically (no API key)
```bash
uv run python scripts/bot_runner.py --bot greedy --config <bundle>/config.toml --seed 8260
```

## Grade a rollout
```bash
uv run python tests/checkers.py --rollout <rollout.json> --live-state <live_state.json> --bundle-checkers tests/bundle_checkers.py
```
