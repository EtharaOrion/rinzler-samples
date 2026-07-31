---
name: rinzler-trelquist-sim
description: "Key mechanics of the rinzler \"Trelquist\" AI-startup CEO simulation (survive-to-horizon, funds band, multi-domain prestige)"
metadata: 
  node_type: memory
  type: reference
  originSessionId: e71e31e8-5af5-4291-b601-3bb733cde019
  modified: 2026-07-30T20:01:38.633Z
---

The `rinzler` CLI runs a 2-year AI-startup sim (Trelquist). Setup: `[ -f /work/rinzler.db ] || cp /opt/rinzler-task/seed.db /work/rinzler.db`. Orchestrated end-to-end by `/work/autopilot.py`. Non-obvious mechanics discovered the hard way:

- **Adversarial client detection is client-based, NOT task-based.** Vanguard ML balloons ALL its tasks ~4.876x real qty on accept (infeasible). Prism Analytics + Equinox Labs are honest (real qty ≤ market qty). Market `required_qty` is only a preview; real qty revealed via `task inspect` after accept. Flag with `harbor flag-adversarial --client-id N`.
- **`sim resume` REQUIRES ≥1 active dispatched task** — the sim cannot idle; time only advances while a task runs.
- **Funds only climb, cannot be reduced.** Payroll ~3.3M/mo (all 7 employees, fixed, grows slowly) << per-task reward ~0.7-1.3M, and there is NO hire/invest/spend command. So over-earning is structurally forced under a no-failure constraint. Best mitigation: 1 concurrent task, minimal crews, low-reward fillers.
- **Throughput K is domain-specific and grows over time** (research/inference ~30-48, data_env/training ~9-12). qty/day ≈ K × sum(crew skill in domain). Conservative K sizing avoids deadline failures but leaves tasks over-crewed (finish fast → over-earn). Deadline ~10-13 days; missing it = task FAILS.
- **data_env/training honest tasks gated at required_trust:3** (trust builds by completing a client's tasks; reached ~4 for both). Honest data_env supply is very scarce (basically one Equinox task that regenerates slowly), so data_env prestige stays low.

Outcome achieved: horizon reached, no bankruptcy, 0 deadline failures, 4-domain prestige — but funds over-earned to ~$104M from ~$60M start (unavoidable). See [[MEMORY]].
