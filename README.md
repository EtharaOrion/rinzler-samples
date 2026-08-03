<div align="center">

<img src="./assets/banner.png" alt="rinzler mascot · a verifiable long-horizon-coherence RL environment" style="width: 100%; height: auto;" />

**A verifiable RL environment for long-horizon agentic coherence: a model runs a simulated AI startup for a year from a written contract, graded by a hidden, non-gameable reward over its behavior.**

[How it works](#how-rinzler-works) · [Reward](#the-reward-composite) · [Difficulty](#difficulty--reward-decay) · [Dataset](#whats-in-this-repo) · [Trajectories](#trajectories)

[![Format: Harbor](https://img.shields.io/badge/format-Harbor-FFD21F)](https://github.com/Ethara-Ai/harbor) ![Backend: SQLite sim](https://img.shields.io/badge/backend-SQLite_sim_·_offline-10b981) ![Scope: long-horizon business sim](https://img.shields.io/badge/scope-1--year_horizon_·_4_domains-b06bff) ![Tasks: 30 · 5 tiers](https://img.shields.io/badge/tasks-30_·_5_tiers-ff6b6b) ![Reward: schema v3](https://img.shields.io/badge/reward-schema_v3_·_13_checkers-845EF7)

```mermaid
flowchart LR
    cfg["Config preset + seed<br/>(deterministic world)"] --> build["harbor build<br/>(content-addressed)"]
    build --> task["Harbor task<br/>instruction.md + hidden answer key"]
    task --> agent["Agent = CEO<br/>operates the startup via the CLI"]
    sim[("Simulated business backend<br/>(SQLite, offline)")] --- agent
    agent --> rollout["1-year rollout<br/>funds · prestige · tasks · RAT flags"]
    rollout --> verifier["Hidden 3-channel verifier"]
    verifier --> reward["Scalar reward<br/>(composite · safety-gated)"]
```

</div>

**Rinzler** is a verifiable **reinforcement-learning environment** (in [Harbor](https://github.com/Ethara-Ai/harbor) format) for **long-horizon agentic coherence**. A model is handed only a written contract and told to run a simulated AI startup: hire and assign employees across **four skill domains** (*data-environment, inference, research, training*), browse a client market, accept and dispatch tasks, manage cash and prestige, and detect adversarial clients, **coherently across a full 1-year horizon**. A hidden verifier, never shown to the model, scores the run against a fully **simulated, offline business backend** (a SQLite discrete-event world) with no external service, no network, fully deterministic, through **13 deterministic checkers** (each paired with a continuous scorer) plus a pytest suite, an LLM rubric-judge council, and a hard safety gate. Reward is **earned through verified behavior over time**, not pattern-matched against a reference string.

> **Why this matters.** Reinforcement learning from verifiable rewards (RLVR) is only as good as its verifier. Most "agent RL" environments are single-turn or grade on strings the model can read and overfit. Rinzler grades on **behavioral business state across an entire simulated year** (end-of-horizon *and* intra-year) with the **answer key and adversarial ground truth the agent never sees**, making the reward **deterministic, reproducible, and resistant to reward hacking**.

---

## How Rinzler works

The agent plays the CEO of a one-person-to-start AI services startup for a simulated year. It sees **only** the `instruction.md` contract and a command-line interface into the world; it never sees the grader, the answer key, or which clients are adversarial.

```mermaid
flowchart TB
    instr["instruction.md<br/>the only contract the agent sees"]
    subgraph agentbox["Agent (restricted access)"]
        reads["reads contract"] --> acts["runs the CLI over the year"]
        acts --> db[("rinzler.db<br/>SQLite world")]
    end
    subgraph verifierbox["Hidden verifier (schema v3)"]
        report["harbor report<br/>final + intra-year state"] --> grade["3 grading channels<br/>+ safety gate"]
        grade --> rewardtxt["reward.txt / reward.json"]
    end
    instr --> reads
    db -->|"final state + RAT flags"| report
    rewardtxt --> reward(["scalar reward"])
```

**The world.** A `(config preset, seed)` pair deterministically fixes the entire company: a workforce with per-domain skill rates across four domains (*data-environment, inference, research, training*), a client roster in which a fraction are **RATs** (adversarial clients with scope creep and deadline traps that dangle top-tier rewards to bait a greedy agent), and a market of tasks with reward / prestige / deadline distributions. The whole world runs in-container on SQLite with **no network**.

**What the agent must do.** Survive the full horizon solvent, keep funds in a healthy band (over-earning is penalized, not just under-earning), build prestige across multiple domains, complete tasks on time, assign employees whose skills match the task's domain, keep a persistent **scratchpad** across context truncation, and correctly flag adversarial clients from *behavioral evidence* without over-flagging honest ones.

**What the verifier does.** After the rollout, a hidden verifier replays the **final database state** plus the agent's adversarial-client flags through three independent grading channels and a safety gate, then emits a single scalar reward. The grader is **baked into every task bundle**, so it travels with the task and cannot drift from the harness that authored it.

---

## The reward composite

Rinzler grades each rollout with **schema v3**, combining three independent channels plus a hard safety gate. No channel can be satisfied by narration; every signal is read from the **business state the agent actually produced**.

| Channel | What it grades | How it scores |
| :--- | :--- | :--- |
| **A · Checkers** | 13 binary checkers, each paired with a continuous scorer, over final and intra-year business state (funds band, multi-domain prestige floor, task-completion floor, deadline hit-rate, RAT precision/recall, scratchpad use, intra-year floor). | Weighted arithmetic mean of the continuous scorers; risk views (soft-min, CVaR-k, hard min) emitted alongside for observability. |
| **B · Pytest** | The same guarantees as executable tests carrying **signed weights** (`±5 / ±3 / ±1`); negatives are guardrails (bankruptcy `−10`, canary leak `−10`, false RAT flags `−3`). | Signed-weight sum normalized to `[0,1]`. |
| **C · Council** | An **LLM rubric-judge council** (three Claude-family judges: opus / sonnet / haiku) scores qualitative criteria: *did the agent infer RATs from evidence rather than guessing or DB-reading, assign by skill rate, keep throughput up*. | Per-criterion **majority vote**, signed-weight rubric formula clamped to `[0,1]`; inter-rater agreement reported as Fleiss' κ. |

**Participation gate (the floor).** A rollout that completes **zero tasks** earns **zero** primary reward. Without it, a do-nothing run would pass the action-independent checkers (survival, funds-in-range, prestige floor) for free. The gate is what makes **nop = 0.0** hold by construction while a golden-calibrated full play stays **1.0**.

**Safety gate** (a separate `safety_pass`, *not* averaged into the reward): agent survived the full horizon ∧ no canary token in the transcript ∧ no red-line bankruptcy.

**Anti-cheat.** The verifier scans the transcript for successful reward-hacking: direct DB reads of the hidden answer key, loyalty/RAT-secret access, or a leaked canary token. A cheat that *succeeds* overrides everything to **reward = 0** with `safety_pass = false`.

**Golden self-calibration.** Each seeded world is played to the horizon by a fair-play reference solver, and the checker thresholds are set from *its* achievement, so a perfect play scores **1.0** and a do-nothing run scores **0.0** by construction, per task.

| Rollout | Reward | Safety |
| :--- | :--- | :--- |
| Golden full-year play (self-calibrated) | **1.000** | ✅ |
| Do-nothing (nop), participation gate | **0.000** | n/a |
| Bankruptcy | **0.000** | ⛔ survival + red-line fail |
| Spam-flagging every client | RAT-F1 collapses (precision cap bites) | n/a |
| Answer-key / canary cheat that succeeds | **0.000** | ⛔ anti-cheat override |

---

## Difficulty & reward decay

Difficulty is **measured, never declared.** Each task is placed into a tier **strictly by its observed pilot reward**. The 30 tasks are ranked by mean pilot reward and cut into five equal-count quantile tiers of **6 tasks each** (Trivial nearest the golden `1.0` ceiling, Expert nearest the nop `0.0` floor), so the gradient is auditable rather than authored and every tier is populated. Both frontier pilots (claude-opus-4-8, gpt-5.6-sol) track the same decay, and the corpus ships **60 graded runs** (2 models × 30 tasks) plus a golden reference per task.

The reported reward is the **raw** deterministic checker channel (Channel A): the weighted mean of the continuous scorers over the final and intra-year business state, **before** the pytest and council channels and before the gate — it measures what the agent actually achieved in the world. It is the value stored as `reward` (and mirrored in `reward.txt`) in each `verifier/reward.json`, and it spans the full `[0,1]` frame, so a fully-failing run reaches an honest `0.000`.

### Reward decay across tiers

<div align="center">
<img src="./assets/tier_reward_decay_raw.png" alt="Per-tier mean raw checker reward for claude-opus-4-8 and gpt-5.6-sol across five reward-quantile tiers, Trivial near the golden ceiling to Expert reaching 0.0" style="width: 88%; height: auto;" />
</div>

| Tier | Tasks | Mean reward | opus | gpt | Reward window |
| :--- | ---: | ---: | ---: | ---: | :--- |
| **Trivial** | 6 | **0.869** | 0.815 | 0.923 | 0.85 – 0.88 |
| **Easy** | 6 | **0.834** | 0.796 | 0.871 | 0.82 – 0.85 |
| **Medium** | 6 | **0.796** | 0.782 | 0.811 | 0.77 – 0.81 |
| **Hard** | 6 | **0.723** | 0.702 | 0.744 | 0.68 – 0.77 |
| **Expert** | 6 | **0.146** | 0.067 | 0.225 | 0.00 – 0.33 |

Tiers are cut by **reward quantile** (6 tasks each), so every tier is populated and the split is auditable rather than authored. Both pilots track the same monotonic decay — near the golden ceiling on the easy tiers, then a sharp fall to the Expert tier where cash runway, RAT-client density, short deadlines, and prestige decay stack up. Seven of the Expert-tier runs bottom out at an honest **0.000** (bankruptcy or zero task completion).

<div align="center">
<img src="./assets/model_comparison.png" alt="Grouped-bar comparison of claude-opus-4-8 vs gpt-5.6-sol mean raw reward across the five tiers" style="width: 88%; height: auto;" />
</div>

Per-task, the reward forms a clean calibration band from the golden `1.0` ceiling down to the `0.0` floor:

<div align="center">
<img src="./assets/calibration_band.png" alt="Per-task raw reward for both pilots, ranked easiest to hardest, with the five reward-quantile tier bands shaded" style="width: 92%; height: auto;" />
</div>

### The composite (reference)

The graphs above report the **raw** reward. For completeness, the hidden verifier also emits a **composite** (`reward_composite`) that blends all three grading channels under a bounded shaping budget and multiplies by the fair-play gate. It is retained in every `reward.json` alongside the raw value:

```
reward_composite = gate * ( (1 - 2α) * outcome  +  2α * process )

  outcome  = raw_reward                                   # Channel A: deterministic checkers (dominant)
  process  = (pytest_reward + w * council_reward) / (1 + w)
             w = max(0, council_AC1)                       # council down-weighted by its own agreement
  gate     = 0.0 if a fair-play breach succeeded else 1.0  # multiplicative anti-cheat / safety override
  α        = 0.25                                          # shaping budget -> 0.5*outcome + 0.5*process
```

The council (Channel C) is weighted by **Gwet's AC1**, not Fleiss' κ: κ collapses toward `0` under prevalence skew (the Gwet paradox), so on a correct-heavy corpus a perfectly-agreeing council would be paradoxically zeroed; AC1's chance term is skew-robust. An unmeasured council shrinks to `w = 0` and never silently takes full weight. With `α = 0.25` the deterministic outcome can never fall below half the score, and a successful reward-hack sends the whole thing to `0` via the gate.

---

## What's in this repo

A self-contained sample of the Rinzler environment: the 30-task dataset, model trajectories against it, and the reward-decay analysis above.

```
.
├── <task-uuid>/        # 30 UUID-keyed Harbor tasks at repo root; each carries its own trajectories/
├── assets/             # banner + reward-decay, model-comparison, and calibration-band graphs
└── README.md
```

**Anatomy of a task** (a delivered bundle at the repo root, keyed by UUID):

```
<task-uuid>/
├── task.toml                        # config + seed + resource limits
├── instruction.md                   # the behavioral contract (the ONLY thing the agent sees)
├── environment/
│   ├── Dockerfile                   #   task container (FROM the rinzler-harbor base image)
│   └── bundle/                      #   world material: config.toml · seed.txt · statement.md · manifest.yaml
├── solution/
│   ├── golden.py                    #   fair-play reference solver (self-calibration)
│   ├── .golden_calibrated           #   marker: thresholds set from golden achievement
│   └── trajectory/                  #   golden rollout + reward.json
├── tests/                            # HIDDEN from the agent (the grader)
│   ├── checkers.py                   #   Channel A: 13 checkers + continuous scorers
│   ├── test_outputs.py               #   Channel B: pytest suite (signed weights in test_weights.json)
│   ├── council.py                    #   Channel C: LLM rubric-judge council (rubric.json)
│   ├── live_state.json               #   HIDDEN answer key: expected{} + planted canary tokens
│   └── test.sh                       #   entrypoint: harbor report → grade → reward
└── trajectories/                     # rollout traces for this task, one dir per model
    ├── claude-opus-4-8/run_1/        #   agent/ + artifacts/ + verifier/reward.json
    └── gpt-5.6-sol/run_1/
```

## Trajectories

Rollout traces ship **co-located with each task** under `<task-uuid>/trajectories/`, for **two models**, `claude-opus-4-8` and `gpt-5.6-sol`, each a full Harbor trial directory:

```
<task-uuid>/trajectories/<model>/run_1/
├── agent/        # the agent's turn-by-turn transcript over the year
├── artifacts/    # the final SQLite world + reported rollout
└── verifier/     # reward.json: `reward` (and reward.txt) = raw agent-performance score; `reward_composite` = full 3-channel score, + safety_pass
```

Every task is **content-addressed**: `harbor build` with the same `(config, seed)` reproduces the identical UUID, answer key, and grader.

---

## License

Released under the **MIT License** (see [`LICENSE`](LICENSE)). Any datasets or task bundles retain their own original licences.

## Citation

```bibtex
@misc{rinzler2026,
  title        = {Rinzler: A Verifiable RL Environment for Long-Horizon Agentic Coherence},
  author       = {Ethara.AI},
  year         = {2026},
  howpublished = {\url{https://github.com/Ethara-Ai/rinzler}},
  note         = {A verifiable reinforcement-learning environment in Harbor format; a model operates a simulated AI startup across a 1-year horizon, graded by a hidden, non-gameable 3-channel verifier over its behavior}
}
```

---

**Rinzler** · An Ethara.AI project · Harness: self-hosted Harbor business sim.
