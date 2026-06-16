# Deployment Guide

Three deployment scenarios. Choose based on available hardware.

---

## Prerequisites (all scenarios)

```bash
git clone <repo-url>
cd voctomix
cp .env.example .env     # fill in HOST_IP and optional camera sources
```

---

## Scenario 1 — Single PC (Native)

**Requires:** Python 3.8+, GStreamer 1.20+, GTK 3, FFmpeg. See [DEPENDENCIES.md](DEPENDENCIES.md).

```bash
./start_studio_single_pc.sh
```

This script starts voctocore, synthetic camera sources (FFmpeg), and voctogui in sequence.

**Stop:** `Ctrl+C` or `killall python3 ffmpeg`

---

## Scenario 2 — Two PCs (Native)

**PC1** runs voctocore. **PC2** runs voctogui and connects over LAN.

```bash
# PC1 (server):
./2pc_escenario2/start_voctocore_pc1.sh

# PC2 (operator):
IP_SERVER=<PC1_LAN_IP> ./2pc_escenario2/start_voctogui_pc2.sh
```

Verify PC1's IP with `hostname -I`. Ensure ports 9999 and 14000-14005 are open on PC1's firewall.

---

## Scenario 3 — Docker (Recommended)

**Requires:** Docker Engine 24+, Docker Compose plugin 2.20+.

```bash
# Allow Docker to open GUI windows:
xhost +local:$(id -un)

# Build images and start all 10 services:
./launch_docker_studio.sh

# Monitor startup:
docker compose ps        # wait until voctocore shows healthy
docker compose logs -f voctocore
```

**Stop:**
```bash
docker compose down
```

**Rebuild after code changes:**
```bash
docker compose build
./launch_docker_studio.sh
```

### Verifying Docker Health

```bash
docker compose ps
# Expected: all services show (healthy) except telemetry (no health check)

# Test control port:
echo "get_video" | nc localhost 9999

# Test telemetry:
curl http://localhost:8080/health

# Test RabbitMQ:
# Navigate to http://localhost:15672
```

---

## Scenario 4 — Kubernetes (Development with minikube)

```bash
# Start minikube:
minikube start --cpus=4 --memory=4096

# Build and load image:
minikube image build -t voctomix:latest .

# Create credentials secret:
kubectl create secret generic rabbitmq-creds \
  --from-literal=user=voctomix \
  --from-literal=pass=<your-password>

# Deploy all services:
./k8s_escenario/launch_k8s.sh

# Monitor:
kubectl get pods -w

# Forward ports to localhost:
POD=$(kubectl get pods -l app=voctocore -o jsonpath="{.items[0].metadata.name}")
kubectl port-forward $POD 9999:9999 8080:8080 &

# Teardown:
./k8s_escenario/teardown_k8s.sh
```

---

## Custom Camera Sources

To replace the default demo videos with real inputs, edit `.env`:

```bash
# Network camera (RTSP):
CAM1_SOURCE=rtsp://192.168.1.50/stream

# Local file:
CAM1_SOURCE=/path/to/video.mp4

# Test pattern (no external source needed):
CAM1_SOURCE=lavfi:testsrc2=size=1920x1080:rate=25
```

---

## Telemetry Configuration

### Native mode

Telemetry writes to `registros/gui_state.json`. Create the directory first:
```bash
mkdir -p registros
```

### Docker mode

Set `SAVE_LOGS=true` in `.env` to also persist logs to disk inside the container. Default: `false` (RabbitMQ only).
