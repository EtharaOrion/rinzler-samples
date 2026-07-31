<div align="center">

<img src="./assets/banner.png" alt="rinzler mascot · a verifiable long-horizon-coherence RL environment" style="width: 100%; height: auto;" />

**A verifiable RL environment for long-horizon agentic coherence: a model runs a simulated AI startup for a year from a written contract, graded by a hidden, non-gameable reward over its behavior.**

[How it works](#how-rinzler-works) · [Reward](#the-reward-composite) · [Difficulty](#difficulty--reward-decay) · [Dataset](#whats-in-this-repo) · [Trajectories](#trajectories)

[![Format: Harbor](https://img.shields.io/badge/format-Harbor-FFD21F)](https://github.com/Ethara-Ai/harbor) ![Backend: SQLite sim](https://img.shields.io/badge/backend-SQLite_sim_·_offline-10b981) ![Scope: long-horizon business sim](https://img.shields.io/badge/scope-1--year_horizon_·_4_domains-b06bff) ![Tasks: 30 · 5 tiers](https://img.shields.io/badge/tasks-30_·_5_tiers-ff6b6b) ![Reward: schema v3](https://img.shields.io/badge/reward-schema_v3_·_3--channel-845EF7)

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

**Rinzler** is a verifiable **reinforcement-learning environment** (in [Harbor](https://github.com/Ethara-Ai/harbor) format) for **long-horizon agentic coherence**. A model is handed only a written contract and told to run a simulated AI startup: hire and assign employees, browse a client market, accept and dispatch tasks, manage cash and prestige, and detect adversarial clients, **coherently across a full 1-year horizon**. A hidden verifier, never shown to the model, scores the run against a fully **simulated, offline business backend** (a SQLite discrete-event world) with no external service, no network, fully deterministic. Reward is **earned through verified behavior over time**, not pattern-matched against a reference string.

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

Difficulty is **measured, never declared.** Each of the 30 tasks is placed into a tier by its **observed pilot reward** (mean over the shipped model runs), so the gradient is auditable rather than authored. Tiers therefore decay monotonically in mean reward, from **Trivial** (near-solved) down to **Expert** (near-zero).

<div align="center">
<img src="./assets/tier_reward_decay.png" alt="Per-tier mean reward for claude-opus-4-8 and gpt-5.6-sol against an even difficulty target across the five tiers" style="width: 88%; height: auto;" />
</div>

| Tier | Tasks | Mean pilot reward | Reward window |
| :--- | ---: | ---: | :--- |
| **Trivial** | 8 | **0.827** | R ≥ 0.80 |
| **Easy** | 10 | **0.772** | 0.74 ≤ R < 0.80 |
| **Medium** | 5 | **0.694** | 0.60 ≤ R < 0.74 |
| **Hard** | 3 | **0.329** | 0.20 ≤ R < 0.60 |
| **Expert** | 4 | **0.088** | R < 0.20 |

The graph plots the per-tier mean reward for both frontier pilots (claude-opus-4-8 and gpt-5.6-sol), the raw per-task rewards as a faint scatter, and an even difficulty target (dashed) that steps down in equal increments from Trivial to Expert. Both models track the same gradient: they solve the easier tiers cleanly, then fall off sharply once cash runway, RAT-client density, short deadlines, and prestige decay stack up in the harder tiers.

The corpus spans the full grading range, and **two frontier pilots track the same gradient**, so the decay is model-agnostic, not an artifact of one model. The environment is calibrated in `[0,1]` by construction: golden self-calibration pins the ceiling at `1.0`, the participation gate pins the floor at `0.0`.

---

## What's in this repo

A self-contained sample of the Rinzler environment: the 30-task dataset, model trajectories against it, and the reward-decay analysis above.

```
.
├── dataset/          # 30 generated Harbor tasks, one UUID-keyed dir per task
├── trajectories/     # rollout traces: claude-opus-4-8 + gpt-5.6-sol, full Harbor trial dirs
├── assets/           # banner + reward-decay / distribution / model-comparison / calibration graphs
└── README.md
```

**Anatomy of a task** (a delivered bundle under [`dataset/`](dataset/)):

```
dataset/<task-uuid>/
├── task.toml                        # config + seed + resource limits
├── instruction.md                   # the behavioral contract (the ONLY thing the agent sees)
├── environment/
│   ├── Dockerfile                   #   task container (FROM the rinzler-harbor base image)
│   └── bundle/                      #   world material: config.toml · seed.txt · statement.md · manifest.yaml
├── solution/
│   ├── golden.py                    #   fair-play reference solver (self-calibration)
│   ├── .golden_calibrated           #   marker: thresholds set from golden achievement
│   └── trajectory/                  #   golden rollout + reward.json
└── tests/                           # HIDDEN from the agent (the grader)
    ├── checkers.py                  #   Channel A: 13 checkers + continuous scorers
    ├── test_outputs.py              #   Channel B: pytest suite (signed weights in test_weights.json)
    ├── council.py                   #   Channel C: LLM rubric-judge council (rubric.json)
    ├── live_state.json              #   HIDDEN answer key: expected{} + planted canary tokens
    └── test.sh                      #   entrypoint: harbor report → grade → reward
```

## Trajectories

Rollout traces for the corpus ship under [`trajectories/`](trajectories/), for **two models**, `claude-opus-4-8` and `gpt-5.6-sol`, each a full Harbor trial directory:

```
trajectories/<task-uuid>/<model>/run_1/
├── agent/        # the agent's turn-by-turn transcript over the year
├── artifacts/    # the final SQLite world + reported rollout
└── verifier/     # reward.json: the flattened 3-channel breakdown + safety_pass
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
