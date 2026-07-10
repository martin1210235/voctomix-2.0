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

## Scope

The documents in this directory are intended for users and contributors of the
public software repository. Internal thesis notes, paper workbench files,
presentation material and private experiment logs are intentionally kept outside
the public documentation export.
