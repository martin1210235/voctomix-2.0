# Voctomix 2.0 — Documentation

Modular open-source system for real-time remote live video production.
Built on GStreamer, containerized with Docker, validated across four deployment
scenarios from a single workstation to a Kubernetes cluster.

This `docs/` tree is the in-depth documentation complementing the top-level
[`README.md`](../README.md) quick start.

## Index

| Document | Contents |
|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | System architecture, GStreamer pipeline, modules, data flow |
| [CONTROL_PROTOCOL.md](CONTROL_PROTOCOL.md) | The line-based TCP control protocol (port 9999) — full command reference |
| [TELEMETRY.md](TELEMETRY.md) | Telemetry chain, RabbitMQ AMQP, CHANGE/STATE events, JSON schema |
| [DEPLOYMENT.md](DEPLOYMENT.md) | The four deployment scenarios, step by step |
| [CONFIGURATION.md](CONFIGURATION.md) | `default-config.ini` reference (core and GUI) |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Known issues and fixes |

## Organization (Diátaxis)

The docs follow the [Diátaxis](https://diataxis.fr/) model, separating content by
user need so readers find what they want without wading through the rest:

| Type | Need | Here |
|---|---|---|
| **Tutorial** (learning) | "guide me the first time" | README Quick Start, [DEPLOYMENT.md](DEPLOYMENT.md) |
| **How-to** (task) | "how do I do X" | [TROUBLESHOOTING.md](TROUBLESHOOTING.md), deployment steps |
| **Reference** (facts) | "what is the exact command/port" | [CONTROL_PROTOCOL.md](CONTROL_PROTOCOL.md), [CONFIGURATION.md](CONFIGURATION.md) |
| **Explanation** (why) | "why is it designed this way" | [ARCHITECTURE.md](ARCHITECTURE.md), [TELEMETRY.md](TELEMETRY.md) |

See [DOC_PATTERNS.md](DOC_PATTERNS.md) for the documentation patterns we follow
from top open-source projects.

## Documentation plan (status)

- [x] `docs/` index (this file) + Diátaxis organization
- [x] ARCHITECTURE.md, CONTROL_PROTOCOL.md, TELEMETRY.md
- [x] DEPLOYMENT.md — per-scenario walkthrough (4 scenarios)
- [x] CONFIGURATION.md — `default-config.ini` reference
- [x] TROUBLESHOOTING.md — common issues per scenario
- [x] Root `CONTRIBUTING.md`, `CHANGELOG.md`, `.env.example`
- [x] README: badges, Quick Links, four scenarios, Documentation/Contributing sections
- [x] `.github/workflows/ci.yml` — lint CI (pycodestyle). Test job omitted: the
      unit suite currently fails in a clean environment (no Makefile either).
- [x] Clean public export via `tools/export_public.sh` (allowlist; excludes
      thesis, paper, internal notes, sessions).
- [ ] Add screenshots/GIF (show, don't tell) — needs media assets
- [ ] Set the real public repository URL (also used in the paper's data-availability)
- [ ] Fix/triage the failing voctocore unit tests, then add a test job to CI
- [ ] (Future) Zenodo DOI badge so the repo is citable from the paper

## README audit (2026-06-27, resolved)

Gaps detected and fixed between the top-level `README.md` and the repository:

- ✅ `docs/`, `.env.example` now exist; `CONTRIBUTING.md`/`CHANGELOG.md` added.
- ✅ "three deployment scenarios" corrected to **four** (Single-PC, Two-PC,
  Docker, Kubernetes).
- ⚠️ Still pending: `.github/workflows/` referenced in the project structure;
  add CI or drop the reference. Quick Start clone URL still a placeholder —
  set the real public repository URL.

## Comparison with prior documentation

- The original **C3VOC Voctomix** README is correct but minimal (subproject
  split, dependency install, Docker readme).
- The **GATV `voctomix1`** README is an unfinished placeholder (GitLab default
  template + unresolved git merge-conflict markers). Not a model to imitate.
- This documentation aims to exceed both: modular, task-oriented, with a full
  control-protocol and telemetry reference that neither prior version documents.
