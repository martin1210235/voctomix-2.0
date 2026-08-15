# Deploying Voctomix on Kubernetes (k3s)

How the Kubernetes scenario is set up for the paper's tests. Intended as a
reference and as a justification for the implementation choices.

## Why k3s and not Minikube?
The supervisors asked for **kind or k3s, not Minikube**. Reason: Minikube runs
the cluster **inside a Docker container**, so measuring it would really mean
measuring Docker again. **k3s** is a **real, lightweight Kubernetes
distribution installed directly on the host** (it uses containerd, no
Docker), so it measures **genuine orchestration** overhead on the hardware.
That is the honest comparison the paper needs: native < Docker < Kubernetes.

## Installation (the "2 commands")
```bash
# 1) Install k3s (readable kubeconfig so kubectl works without sudo)
curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="--write-kubeconfig-mode 644" sh -
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

# 2) Import our image into k3s's containerd (note the k8s.io namespace)
docker save voctomix-voctocore:latest | sudo k3s ctr -n k8s.io images import -

# Check
kubectl get nodes                                  # -> Ready, control-plane
sudo k3s ctr -n k8s.io images ls | grep voctomix   # -> image present
```
Important detail: the image must go into the containerd namespace **`k8s.io`**
(the one the kubelet looks at). Without `-n k8s.io`, pods fail with
`ErrImageNeverPull`.

## Deployment architecture
Everything runs as **pods** in the `voctomix-exp` namespace, with
`hostNetwork: true` (they use the host network, so the cameras talk to the
core over `localhost`, the same as in Docker/Local, keeping the measurement
comparable):
- **voctocore** (Deployment): the mixer. Reads its format from a
  **ConfigMap**.
- **support** (Deployment): auxiliary sources (stream blanker, audio, break,
  intro).
- **cam1..cam4** (Deployments): the 4 cameras (Big Buck Bunny with a colour
  marker, or a solid colour).

## Key files
| File | What it does |
|---|---|
| `experiments/namespace.yaml` | Creates the isolated `voctomix-exp` namespace. |
| `experiments/voctocore.yaml` | Core manifest: `hostNetwork`, format ConfigMap, `strategy: Recreate` (avoids port conflicts on restart), no CPU limit. |
| `experiments/gen_camera_manifests.py` | Generates the 4 camera Deployments per format and profile (`experiment`=Big Buck Bunny+marker, `latency`=solid colour), with bt709 colorimetry and the video mounted via hostPath. |
| `experiments/gen_support_manifest.py` | Generates the support Deployment (stream blanker, audio, break, intro) per format. |
| `experiments/k8s_scenario.sh` | **Manager**: `up/cams/scale/crash/verify-format/mix-frame/down`. Deploys, changes format, activates cameras and simulates failures. |
| `../experiments/comprehensive/measure_performance_k8s.py` | Performance (1.1/1.2): CPU/RAM from `/proc`, with a 0-camera baseline. |
| `../experiments/comprehensive/run_matrix_k8s.py` | Test-matrix orchestrator (4 formats × 5 analyses) with checkpoints, retries, gating and per-cell ffprobe verification. |

## How to deploy and control it (manager script)
```bash
bash experiments/k8s_scenario.sh up 1080p25            # namespace + configmap + support + voctocore
bash experiments/k8s_scenario.sh cams 1080p25 experiment   # all 4 cameras
bash experiments/k8s_scenario.sh verify-format 1080p25     # ffprobe of the actual output
kubectl get pods -n voctomix-exp                        # check everything is Running
bash experiments/k8s_scenario.sh down                   # delete the namespace = clean up
```

## Changing format (ConfigMap)
`k8s_scenario.sh up <fmt>` runs `set_format.sh` (rewrites the `videocaps`),
creates a **ConfigMap** called `voctocore-config` with that configuration and
mounts it into the voctocore pod. Changing format means a new ConfigMap plus
a restart. `ffprobe` is used to verify the output actually comes out at the
requested resolution.

## Self-healing — resilience analysis
A camera failure is simulated by deleting its pod:
```bash
kubectl delete pod -n voctomix-exp -l app=cam1 --grace-period=0 --force
```
The **Deployment (ReplicaSet) automatically recreates the pod**, and the
camera reconnects to the core. The time until video returns is the **MTTR**
that gets measured. That is Kubernetes' self-healing, the advantage over
Docker/native.

## Measurement
- **CPU/RAM**: read from `/proc` (the same source as htop); the pods run on
  the host, so the total consumption = k3s + pods = the cost of the
  Kubernetes deployment.
- **Latency and resilience**: thanks to `hostNetwork`, these are measured the
  same way as in the other scenarios (control port 9999, mix output 11000).
