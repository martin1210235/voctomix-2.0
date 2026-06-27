# Deployment Scenarios

Voctomix 2.0 is validated across four deployment scenarios of increasing
infrastructure complexity. The top-level [README](../README.md#quick-start) has
the copy-paste quick start; this document explains each scenario and when to use
it.

| Scenario | Launch | Hosts | Runtime |
|---|---|---|---|
| Single-PC native | `start_studio_single_pc.sh` | 1 | Native processes |
| Two-PC native | `start_voctocore_pc1.sh` + `start_voctogui_pc2.sh` | 2 | Native processes |
| Docker Compose | `docker compose up` | 1 | 10 containers |
| Kubernetes | `start_server_pc1.sh` + `start_operator_pc2.sh` | 2 | Pod + StatefulSet |

## 1. Single-PC native

All components on one host. The launch script starts `voctocore` and `voctogui`
as local processes, spawns one FFmpeg subprocess per camera slot, and launches
the auxiliary processes (blanker sources, background audio, telemetry exporter).
The LAN IP is auto-detected (`ip route get 1.1.1.1`) and exported as `LOCAL_IP`.

```bash
./start_studio_single_pc.sh
```

Use it for feature development, integration testing and local demos. Requires
only a working Python 3 environment with GStreamer 1.20.

## 2. Two-PC native (REMI model)

Processing and control split across two hosts on a LAN — a direct
implementation of the Remote Integration Model.

```bash
# PC 1 (event site): mixing engine + camera ingest
./2pc_escenario2/start_voctocore_pc1.sh

# PC 2 (operator, any location): GUI pointing at PC 1
IP_SERVER=<IP_OF_PC1> ./2pc_escenario2/start_voctogui_pc2.sh
```

Multiple operator hosts may connect simultaneously; the broadcast nature of the
TCP control protocol keeps all operators in a consistent state.

## 3. Docker Compose (recommended)

The most reproducible deployment — the entire system as ten containerized
services launched with a single command.

```bash
xhost +local:$(id -un)     # allow the host GUI to receive the voctogui window
./launch_docker_studio.sh
```

Camera containers use `network_mode: service:voctocore`, sharing the mixer's
network namespace so all intra-stack traffic stays on loopback (no virtual
Ethernet overhead). `HOST_IP` is auto-detected at launch and injected into the
containers, making the same Compose file portable across hosts.

Stop the stack:

```bash
sudo docker compose down
```

## 4. Kubernetes (Minikube)

Orchestrated deployment mirroring the two-PC roles at the orchestration level.

```bash
# PC 1: starts Minikube, applies manifests, opens kubectl port-forward
./k8s_escenario/start_server_pc1.sh

# PC 2: runs voctogui against the forwarded address
./k8s_escenario/start_operator_pc2.sh
```

Key manifests in `k8s/`:

| File | Purpose |
|---|---|
| `studio.yaml` | `studio` Deployment: multi-container Pod (`voctocore` + 4 camera sidecars) |
| `rabbitmq.yaml` | RabbitMQ StatefulSet |
| `pvc.yaml` | PersistentVolumeClaim for queue durability |
| `configmap.yaml` | Mixer configuration |
| `secret.yaml.example` | Template for broker credentials (copy to `secret.yaml`) |

All Pod containers share one network namespace, replicating the
`network_mode: service:voctocore` pattern: intra-Pod TCP traffic stays on
loopback without `hostNetwork: true`. Camera video is injected on demand via
`inject_cam.sh` (`kubectl exec` → FFmpeg inside the target sidecar). The launch
script enforces deployment order with `kubectl rollout status` so RabbitMQ is
Ready before the `studio` Pod is applied.

## Production note: CyberNEMO at UPM

The Docker Compose stack has been used in production within the CyberNEMO
European research project at Universidad Politécnica de Madrid: two live feeds
(presenter and slides), branded PNG lower-thirds, the PAUSE blanker between
sessions, and the RabbitMQ telemetry channel retained for post-session analysis.
