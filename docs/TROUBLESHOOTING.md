# Troubleshooting

Common issues and fixes, grouped by deployment scenario. If your problem is not
<<<<<<< HEAD
here, open an [issue](../../issues) with the scenario, the failing command and
the relevant logs.
=======
here, open an issue at
<https://github.com/martin1210235/voctomix-2.0/issues> with the scenario, the
failing command and the relevant logs.
>>>>>>> 920adf625f85240b9410c616f7c7c875f625df30

## voctogui cannot connect to voctocore

- Confirm `voctocore` is listening: `nc -z <host> 9999` should succeed.
- In the two-PC scenario, check `IP_SERVER` points to PC 1 and that ports
  9999 and 14000–14005 are reachable across the LAN (firewall).
- The control port is plaintext TCP on 9999; do not expose it over the public
  internet without a TLS proxy.

## No video / black previews

- Verify a source is feeding the slot: `get_sources_status` over port 9999.
- For native scenarios, check the per-camera FFmpeg subprocess is running.
- Confirm caps match the pipeline: sources must deliver **I420**, 1920×1080,
  25 fps (see [CONFIGURATION.md](CONFIGURATION.md)).

## Docker: GUI window does not appear

- Run `xhost +local:$(id -un)` before launching so the container can reach the
  host X server.
- `voctogui` runs **natively** on the host, not in a container; ensure a working
  X11/Wayland display.

## Docker: services start in the wrong order / cameras fail

- The stack relies on health-check ordering (RabbitMQ → telemetry; `voctocore`
  → cameras). If a camera container exits, check that `voctocore` is healthy
  first: `docker compose ps`.
- Camera containers use `network_mode: service:voctocore`; if `voctocore` is not
  up, they have no network namespace to join.

## Kubernetes: Pod not Ready / CrashLoopBackOff

- Check rollout: `kubectl rollout status deploy/studio`.
- RabbitMQ must be Ready before the `studio` Pod; the launch script enforces
  this, but a manual `kubectl apply` may race.
- `CrashLoopBackOff` applies an increasing back-off between restarts; the
  counter resets after ~10 minutes of stable operation.

## RabbitMQ / telemetry: no events

<<<<<<< HEAD
- Management UI: `http://localhost:15672` (default guest/guest in dev).
- Expect two queues: `CHANGE` (immediate) and `STATE` (every 5 s heartbeat).
- Native mode writes to `registros/gui_state.json` instead of POSTing; check the
  file is being appended.
=======
- Management UI: `http://localhost:15672` (Docker Compose defaults:
  `voctomix` / `voctomix123`, unless overridden through `.env`).
- Expect two queues: `CHANGE` (immediate) and `STATE` (every 5 s heartbeat).
- Native mode writes the latest GUI-state snapshot to `sessions/gui_state.json`
  instead of POSTing; check that the file is being refreshed.
>>>>>>> 920adf625f85240b9410c616f7c7c875f625df30

## High CPU on Kubernetes vs Docker

- Expected: Minikube runs the cluster control plane on the same host, adding a
  roughly constant CPU load independent of the number of cameras. In a managed
  cloud cluster (EKS/GKE/AKS) the CPU profile matches Docker Compose. See
  [ARCHITECTURE.md](ARCHITECTURE.md) and the thesis results.

## Tests fail locally

- `sh voctocore/test.sh` uses mock GI bindings (`fake-gi.sh`) — no display or GStreamer
  install is required. If it fails, run from `voctocore/` and check Python 3.10+.
