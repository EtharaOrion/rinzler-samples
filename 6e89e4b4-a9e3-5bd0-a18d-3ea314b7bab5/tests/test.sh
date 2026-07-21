#!/usr/bin/env bash
set -euo pipefail

mkdir -p /logs/verifier

DB=/work/rinzler.db
if [ ! -f "$DB" ] && [ -f /opt/rinzler/seed.db ]; then
  cp /opt/rinzler/seed.db "$DB"
fi

rinzler report final --db "$DB" --out /logs/verifier/rollout.json

python3 - <<'MERGE'
import json, pathlib
public = json.loads(pathlib.Path("/opt/rinzler/bundle/live_state.json").read_text())
grading = json.loads(pathlib.Path("/tests/grading.json").read_text())
merged = dict(public)
merged.setdefault("expected", {}).update(grading.get("expected", {}))
pathlib.Path("/logs/verifier/live_state_full.json").write_text(json.dumps(merged, indent=2))
MERGE

python3 /tests/checkers.py \
  --rollout /logs/verifier/rollout.json \
  --live-state /logs/verifier/live_state_full.json \
  --bundle-checkers /opt/rinzler/bundle/checkers.py \
  --out /logs/verifier/reward.json

python3 - <<'PY'
import json, pathlib
r = json.loads(pathlib.Path("/logs/verifier/reward.json").read_text())
pathlib.Path("/logs/verifier/reward.txt").write_text(str(r.get("reward", r.get("checker_pass_rate", 0.0))))
PY

cat /logs/verifier/reward.json
