# Changelog

All notable changes to this project are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [2.0.0] — 2026

Voctomix 2.0 extends the original C3VOC Voctomix (`voctomix2` branch) with
production-focused features and a full container deployment stack, developed as
part of a Bachelor's Thesis in Telecommunication Engineering (UPM).

### Added

- **Stream Blanker** — three-state output control (LIVE / PAUSE / NOSTREAM),
  replacing the original binary on/off switch.
- **Dynamic on-air titling** — two independent text layers (lower-thirds)
  composited over the program output in real time.
- **Telemetry service** — exports the complete mixer state as JSON every second;
  writes to `registros/gui_state.json` (native) or HTTP-POSTs to the telemetry
  container, which publishes `CHANGE` and `STATE` events to RabbitMQ over AMQP.
- **Audio Follows Video (AFV)** — automatic audio cross-fade on every source
  switch.
- **Auto-off overlays** — overlays and titles are dismissed automatically on
  every cut or composite change.
- **Full Docker containerization** — ten-service `docker compose up` stack with
  health-check ordering; camera containers share the `voctocore` network
  namespace (localhost communication, no virtual-network overhead).
- **Kubernetes deployment** — Minikube manifests; `studio` Pod with camera
  sidecars and RabbitMQ as a StatefulSet.
- **Intro / VTR pre-loaded sources.**
- **In-depth documentation** — `docs/` tree (architecture, control protocol,
  telemetry, deployment, configuration, troubleshooting).

### Validated

- Functional validation across four deployment scenarios (single-PC, two-PC,
  Docker Compose, Kubernetes).
- Performance instrumented on Docker Compose and Kubernetes
  (Intel Core i9-10900X, 128 GB): 38.8 % CPU at four 1080p25 sources,
  source-switching latency below 5 ms (median 1.5 ms), 31-minute stability with
  no memory leak, and camera-failure recovery in ~520 ms.
- Production deployment within the CyberNEMO European research project at UPM.

### Based on

- [voc/voctomix](https://github.com/voc/voctomix) (branch `voctomix2`),
  originally developed by the C3VOC team.
