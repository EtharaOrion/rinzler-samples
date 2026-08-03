# rinzler Harbor task a6abeb93-fdf0-5a79-b1de-98406e104b34

Tier `tier_trivial` · seed `8203` · config `tier_trivial`.

Operate a simulated AI startup through the `rinzler` CLI over a one-year horizon;
stay solvent, complete client tasks, and flag adversarial (RAT) clients by evidence.

## Run against an LLM agent (from the harness root)
```bash
uv run rinzler run --config <bundle>/config.toml --seed 8203
```

## Run deterministically (no API key)
```bash
uv run python scripts/bot_runner.py --bot greedy --config <bundle>/config.toml --seed 8203
```

## Grade a rollout
```bash
uv run python tests/checkers.py --rollout <rollout.json> --live-state <live_state.json> --bundle-checkers tests/bundle_checkers.py
```
