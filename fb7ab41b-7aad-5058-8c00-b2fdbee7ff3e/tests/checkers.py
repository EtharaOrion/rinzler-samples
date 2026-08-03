#!/usr/bin/env python3
"""Standalone verifier driver: load the bundle checkers module and grade a rollout (reward-v3)."""
from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib


def _load_module(path):
    spec = importlib.util.spec_from_file_location("bundle_checkers", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rollout", required=True)
    ap.add_argument("--live-state", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--bundle-checkers", default="/tests/bundle_checkers.py")
    args = ap.parse_args()

    rollout = json.loads(pathlib.Path(args.rollout).read_text())
    live_state = json.loads(pathlib.Path(args.live_state).read_text())
    mod = _load_module(args.bundle_checkers)

    # Reward-v3: the bundle checkers module owns scoring + aggregation.
    reward = mod.grade(rollout, live_state)
    pathlib.Path(args.out).write_text(json.dumps(reward, indent=2))
    print(json.dumps(reward))


if __name__ == "__main__":
    main()
