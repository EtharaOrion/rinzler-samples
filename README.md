<p align="center"><img src="images/hero.svg" alt="Project" width="720"></p>

# Project: samples

<p align="center"><b>The samples lane: 5 of 5 Harbor task bundles.</b></p>

<p align="center"><a href="#summary"><img src="https://img.shields.io/badge/bundles-5_of_5-845EF7" alt="bundles: 5 of 5"></a> <a href="#evidence-status"><img src="https://img.shields.io/badge/sealed-0-845EF7" alt="sealed: 0"></a> <a href="#difficulty-tiers"><img src="https://img.shields.io/badge/difficulty-measured-845EF7" alt="difficulty: measured"></a></p>

<p align="center"><sub><a href="#abstract">Abstract</a> | <a href="#summary">Summary</a> | <a href="#difficulty-tiers">Difficulty tiers</a> | <a href="#evidence-status">Evidence status</a> | <a href="#coverage">Coverage</a> | <a href="#dataset-structure">Dataset structure</a> | <a href="#verification-and-quality-assurance">Verification and quality assurance</a> | <a href="#reproduction">Reproduction</a> | <a href="#cite">Cite</a> | <a href="#license">License</a> | <a href="#contact">Contact</a></sub></p>

## Abstract

The curated lane of this corpus: at most 5 Harbor task bundles, every anchor seated first and every other bundle in seal order. Bundles past that ceiling live in `delivery/`.

Each bundle is one Harbor task in a directory named by its content-derived uuid5, so the name doubles as an integrity check. This page is rendered from the resident bundles on every reconcile; a value a bundle does not carry reads `absent`, and the page never fills one in.

## Summary

| Property | Value |
| --- | --- |
| Bundles | 5 of 5 |
| Sealed | 0 of 5 |
| Registrations | unregistered (5) |
| Audit verdicts | none (5) |
| Harbor schema | 1.1 (5) |

## Difficulty tiers

Difficulty is measured by the signed pilot alone and never declared in a bundle, so this page states no tier a bundle claims.

## Evidence status

The verdict is the audit outcome recorded at the sealed digest, and `none` means no verdict has landed for that digest yet. Only an authoring run removes a bundle from this lane, so removal waits for the next one.

| uuid | Verdict | Sealed digest | Stream |
| --- | --- | --- | --- |
| 011a30d7-6ad5-5508-9cf7-1d1395904a66 | none | absent | none |
| 402e1dfb-da73-5105-80f2-7127d48b8d7e | none | absent | none |
| 5d24e5ab-d372-5b50-abb4-4267d04e77bb | none | absent | none |
| a6abeb93-fdf0-5a79-b1de-98406e104b34 | none | absent | none |
| ebdef900-eea4-5f75-9d96-bd3f405b6f3d | none | absent | none |

## Coverage

| Keyword | Bundles |
| --- | --- |
| business-sim | 5 |
| long-horizon | 5 |
| rinzler | 5 |

## Dataset structure

| Bundle | Task | Keywords | Registration | Sealed at | Tier |
| --- | --- | --- | --- | --- | --- |
| [`011a30d7-6ad5-5508-9cf7-1d1395904a66`](011a30d7-6ad5-5508-9cf7-1d1395904a66/) | `rinzler/011a30d7-6ad5-5508-9cf7-1d1395904a66` | business-sim, long-horizon, rinzler | unregistered | unsealed | - |
| [`402e1dfb-da73-5105-80f2-7127d48b8d7e`](402e1dfb-da73-5105-80f2-7127d48b8d7e/) | `rinzler/402e1dfb-da73-5105-80f2-7127d48b8d7e` | business-sim, long-horizon, rinzler | unregistered | unsealed | - |
| [`5d24e5ab-d372-5b50-abb4-4267d04e77bb`](5d24e5ab-d372-5b50-abb4-4267d04e77bb/) | `rinzler/5d24e5ab-d372-5b50-abb4-4267d04e77bb` | business-sim, long-horizon, rinzler | unregistered | unsealed | - |
| [`a6abeb93-fdf0-5a79-b1de-98406e104b34`](a6abeb93-fdf0-5a79-b1de-98406e104b34/) | `rinzler/a6abeb93-fdf0-5a79-b1de-98406e104b34` | business-sim, long-horizon, rinzler | unregistered | unsealed | - |
| [`ebdef900-eea4-5f75-9d96-bd3f405b6f3d`](ebdef900-eea4-5f75-9d96-bd3f405b6f3d/) | `rinzler/ebdef900-eea4-5f75-9d96-bd3f405b6f3d` | business-sim, long-horizon, rinzler | unregistered | unsealed | - |

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#131a33","primaryTextColor":"#e8ecff","primaryBorderColor":"#845EF7","lineColor":"#22d3ee","fontFamily":"monospace"}}}%%
flowchart LR
    bundle["&lt;uuid&gt;/"]
    bundle --> n0["task.toml<br/>runner manifest"]
    bundle --> n1["instruction.md<br/>objective the agent reads"]
    bundle --> n2["environment/<br/>agent sandbox image"]
    bundle --> n3["tests/<br/>verifier, hidden from the agent"]
    bundle --> n4["solution/<br/>private oracle"]
    bundle --> n5["trajectories/"]
```

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#131a33","primaryTextColor":"#e8ecff","primaryBorderColor":"#845EF7","lineColor":"#22d3ee","fontFamily":"monospace"}}}%%
flowchart LR
    staging["staging/"]
    staging --> samples["samples/<br/>5 of 5"]
    samples --> delivery["delivery/<br/>25 of 30"]
    delivery --> stock["stock/<br/>0 of 10000"]
```

## Verification and quality assurance

Each bundle's signed provenance carrier holds its screening roots, screening instant, and absolute expiry. Placement moves that carrier into the private derivation set, which this page never reads, so reconcile lists no root it cannot verify here.

## Reproduction

Each bundle directory is a complete Harbor task: `task.toml` is the runner manifest, `instruction.md` the objective, `environment/` the sandbox image, and `tests/` the verifier. Point a Harbor runner at one bundle directory to reproduce it; `solution/` stays private.

## Cite

```bibtex
@misc{rinzler2026,
  title        = {Rinzler: A Verifiable RL Environment for Long-Horizon Agentic Coherence},
  author       = {Ethara.AI},
  year         = {2026},
  howpublished = {\url{https://github.com/Ethara-Ai/rinzler}},
  note         = {A model operates a simulated AI startup across a 1-year horizon,
                  graded by a hidden, non-gameable score-v3 verifier over its behavior}
}
```

## License

Released under the MIT License; see [LICENSE](LICENSE). Copyright (c) 2026 Ethara.AI. Datasets and task bundles retain their own upstream licences; YC-Bench remains under its respective licence.

## Contact

- Organization: [Ethara.AI](https://github.com/Ethara-Ai)
- Security and benchmark-integrity disclosure: see [SECURITY.md](SECURITY.md) (do not open public issues for leaks, contamination, or gameable shortcuts)
- Contribution route: [CONTRIBUTING.md](CONTRIBUTING.md)
