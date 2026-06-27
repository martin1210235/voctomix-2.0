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

## Documentation plan (status)

This is a living plan for publishing complete, public, GATV-grade documentation.

- [x] `docs/` index (this file)
- [x] ARCHITECTURE.md — first draft
- [x] CONTROL_PROTOCOL.md — first draft
- [x] TELEMETRY.md — first draft
- [ ] DEPLOYMENT.md — expand beyond README quick start (per-scenario, screenshots)
- [ ] CONFIGURATION.md — full INI key reference
- [ ] TROUBLESHOOTING.md — port from `.claude/TROUBLESHOOTING.md`, make public
- [ ] Root `CONTRIBUTING.md`, `CHANGELOG.md` (1.x → 2.0), `.env.example`
- [ ] Add real `.github/workflows/` or remove the reference from top README

## README audit (2026-06-27)

Gaps detected between the top-level `README.md` and the actual repository:

- README references `docs/`, `.github/workflows/`, `.env.example` — **these did
  not exist** (this `docs/` tree starts to close the gap).
- README says *"validated across three real deployment scenarios"* — the paper
  and TFG validate **four** (Single-PC, Two-PC, Docker, Kubernetes). Align to four.
- README "Quick Start" clone URL is a placeholder (`<your-username>/voctomix2.0`);
  set it to the real public repository URL used in the paper's data-availability
  statement.

## Comparison with prior documentation

- The original **C3VOC Voctomix** README is correct but minimal (subproject
  split, dependency install, Docker readme).
- The **GATV `voctomix1`** README is an unfinished placeholder (GitLab default
  template + unresolved git merge-conflict markers). Not a model to imitate.
- This documentation aims to exceed both: modular, task-oriented, with a full
  control-protocol and telemetry reference that neither prior version documents.
