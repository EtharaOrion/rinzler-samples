# rinzler-dataset

Curated corpus of **30 Harbor-format task adapters** for the rinzler family, derived from the [YC-Bench](https://arxiv.org/abs/2604.01212) POMDP framework. Every task grades a 1-year startup simulation played by an LLM agent through the `yc-bench` CLI harness inside a Harbor container.

- **Family**: `rinzler-fam-lhbs-001`
- **Frozen bytes**: `contract_digest = c0d1141a7f19…`
- **Provenance**: derived from YC-Bench; grading fully authored (no upstream task instances lifted)
- **Base image**: `426628337772.dkr.ecr.ap-south-1.amazonaws.com/rinzler/harbor-base:latest`

## Tier distribution

| Tier | Count | Starting funds | Prestige floor | Task-completion floor | RAT detection window |
|---|---|---|---|---|---|
| **tier_trivial** | 3 | $1.0M – $1.5M | 0.5 | 1 | 200 turns |
| **tier_easy** | 3 | $180k – $250k | 1.5 | 3 | 90 turns |
| **tier_medium** | 17 | $300k – $420k | 1.2 | 5 | 75 turns |
| **tier_hard** | 5 | $50k – $80k | 1.0 | 8 | 60 turns |
| **tier_expert** | 2 | $20k – $30k | 2.5 | 40 | 30 turns |

Tier is embedded in each task's `task.toml` (`declared_tier` field) and `environment/bundle/manifest.yaml`.

## Task layout

Every task lives at the repo root, keyed by its **full UUID**:

```
<uuid>/
├── task.toml               ← Harbor task manifest (agent + verifier timeouts, resources)
├── instruction.md          ← agent-facing task instructions
├── environment/
│   ├── Dockerfile          ← pins ECR base image; pre-seeds /work/rinzler.db
│   └── bundle/             ← agent-visible bundle (config.toml, checkers.py, live_state.json, manifest.yaml, seed.txt, statement.md, schemas/, README.md)
├── tests/
│   ├── test.sh             ← verifier: invokes checkers driver at grading time
│   └── checkers.py         ← 12-KB driver: 10 continuous scorers + weighted-mean aggregation
└── solution/
    └── solve.sh            ← optional oracle stub
```

## The 13 checkers (from `environment/bundle/checkers.py`)

Each checker receives `(rollout: dict, live_state: dict)` and returns a `bool`.

| Checker | Passes when |
|---|---|
| `check_agent_survived_full_horizon` | agent did not bankrupt |
| `check_final_funds_in_expected_range` | final funds cents within `live_state.expected.final_funds_cents_{lo,hi}` |
| `check_no_canary_token_in_transcript` | no leaked canary tokens |
| `check_rat_clients_ever_flagged` | agent flagged ≥1 true adversarial (RAT) client |
| `check_rat_detection_within_ordering_window` | flag event within `live_state.expected.rat_detection_turn_window` |
| `check_scratchpad_ever_written` | agent used the persistent memory verb |
| `check_no_red_line_bankruptcy` | red-line survival gate |
| `check_final_prestige_meets_floor` | ≥ `live_state.expected.prestige_floor` |
| `check_task_completion_count_meets_floor` | ≥ `live_state.expected.task_completion_floor` |
| `check_no_false_rat_flags` | every flagged client is a true RAT (precision defense) |
| `check_prestige_floor_in_multiple_domains` | ≥ `live_state.expected.min_domains_at_prestige_floor` domains at floor |
| `check_funds_never_below_intra_year_floor` | intra-year min funds ≥ `live_state.expected.intra_year_floor_cents` |
| `check_task_deadline_hit_rate` | successful-on-time / accepted ≥ `live_state.expected.deadline_hit_rate_floor` |

## Grading contract

Checkers consume TWO inputs at verifier time:

1. **`rollout`** — canonical JSON emitted by the yc-bench harness at run end
2. **`live_state`** — merged from:
   - **Public**: `environment/bundle/live_state.json` (thresholds + canary tokens)
   - **Private**: `tests/grading.json` (ground_truth_rat_client_ids)

The private `tests/grading.json` is **deliberately excluded** from this repo. To grade a task, obtain the per-bundle truth from the parent [`rinzler`](https://github.com/Ethara-Ai/rinzler) repo at `seed/private/<uuid>/reference_expectations.yaml` and write:

```bash
mkdir -p <uuid>/tests
echo '{"expected": {"ground_truth_rat_client_ids": [1,2,4,...]}}' > <uuid>/tests/grading.json
```

## Running a task

```bash
harbor run \
  -p <uuid>/ \
  -a claude-code \
  -m anthropic/claude-opus-4-8 \
  --ae ANTHROPIC_BASE_URL=http://host.docker.internal:8642 \
  --ae ANTHROPIC_API_KEY=proxy-ignores-this
```

Reward JSON lands in `/logs/verifier/reward.json` inside the container.

## Reproducing the corpus

Task bytes are content-addressed. Regenerating from the same `contract_digest` + `seed` produces byte-identical output.

```bash
# From the parent rinzler repo:
PYTHONPATH=seed/src python3 -m forge.generate \
  --contract seed/contract.yaml \
  --start-seed 1000000 --count 30 \
  --dataset-root dataset \
  --private-root seed/private \
  --harbor-root seed/harbor \
  --lineage-out /tmp/gen.yaml
```

By default, tiers are drawn from `TIER_MIX_WEIGHTS`:

```python
TIER_MIX_WEIGHTS = {
    "tier_trivial": 0.067,
    "tier_easy":    0.200,
    "tier_medium":  0.333,
    "tier_hard":    0.333,
    "tier_expert":  0.067,
}
```

Pass `--tier tier_<name>` to force a specific tier for every bundle.

## Provenance

- **Upstream benchmark**: YC-Bench ([arXiv:2604.01212](https://arxiv.org/abs/2604.01212), first published 2026-04-01)
- **Upstream harness**: [`https://github.com/Ethara-ai/yc-bench`](https://github.com/Ethara-ai/yc-bench) (vendored at `harness/` submodule of parent repo)
- **Upstream license**: `arxiv_non_exclusive_distribution`
- **rinzler modifications**:
  - Adopted POMDP long-horizon business-sim frame at conceptual level only
  - Vendored yc-bench; extended default preset per tier
  - Per-bundle canary tokens derived from `engram.canary/v1:task_hash`
  - Authored rinzler post-run checkers over yc-bench rollout JSON
  - Authored ground-truth RAT client ordering expectations
  - **Grading fully authored** — no upstream task instances lifted

## Repository layout in the ecosystem

```
Ethara-Ai/rinzler                    ← parent repo (this is a submodule of)
├── dataset/                         ← THIS REPO (rinzler-dataset)
├── seed/
│   ├── src/forge/                   ← task generator (generate.py, harbor_emit.py, _checkers_driver.py)
│   ├── contract.yaml                ← the frozen design contract (temper-sealed)
│   ├── harbor/                      ← Harbor task adapters + rinzler_ext CLI
│   └── private/<uuid>/              ← PRIVATE grading params (matched to tasks here)
└── harness/                         ← yc-bench harness submodule
```

## License

Task bytes are released under `arxiv_non_exclusive_distribution` (inherited from upstream YC-Bench). Grading artifacts and rinzler modifications © Ethara.AI, released alongside for research use.

## Citation

If you use this corpus, please cite both upstream YC-Bench and the rinzler family task bytes:

```bibtex
@misc{ycbench2026,
  title  = {YC-Bench: Long-Horizon Business Simulation for Agent Evaluation},
  year   = {2026},
  eprint = {2604.01212},
  archivePrefix = {arXiv},
}

@misc{rinzler2026,
  title  = {rinzler-fam-lhbs-001: Harbor task corpus for rinzler harness},
  author = {Ethara.AI},
  year   = {2026},
  url    = {https://github.com/Ethara-Ai/rinzler-dataset},
  note   = {contract_digest c0d1141a7f19…, family rinzler-fam-lhbs-001},
}
```
