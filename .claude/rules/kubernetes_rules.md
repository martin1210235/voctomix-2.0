# Kubernetes Rules

Rules for editing manifests under `k8s_escenario/`.

---

## Manifest Structure

```
k8s_escenario/
├── studio.yaml          ← voctocore Deployment + Service
├── rabbitmq.yaml        ← RabbitMQ StatefulSet + Service
├── telemetry.yaml       ← Telemetry Deployment + Service
├── cameras.yaml         ← cam1-cam4 Deployments
├── blanker.yaml         ← stream_blanker Deployment
├── launch_k8s.sh        ← Full deploy script (kubectl apply -f)
└── teardown_k8s.sh      ← Full teardown script
```

## Networking

- Cameras use `hostNetwork: true` to replicate the Docker `network_mode: service:voctocore` pattern — they must reach voctocore via `localhost` on their assigned port.
- voctocore Service exposes all ports (9999, 10000-10005, 11000, 12000-15000, 17000-17001, 18000) as `ClusterIP` for internal access.
- Telemetry uses a separate Service exposing port 8080 as `NodePort` (or `LoadBalancer` in production).
- RabbitMQ exposes 5672 (AMQP) and 15672 (management web UI) as `ClusterIP`.

## Health Checks

- voctocore readinessProbe: `exec: ['bash', '-c', 'echo "" | nc -zw1 localhost 9999']` with `initialDelaySeconds: 20`.
- RabbitMQ readinessProbe: `exec: ['rabbitmq-diagnostics', 'ping']`.
- Camera Deployments use `restartPolicy: Always` (Deployment default) with `backoffLimit`.

## Resource Limits

- voctocore: minimum `requests: {cpu: "1", memory: "512Mi"}`, `limits: {cpu: "4", memory: "2Gi"}`.
- Camera containers: minimum `requests: {cpu: "250m", memory: "128Mi"}`.
- RabbitMQ: minimum `requests: {cpu: "250m", memory: "256Mi"}`.

## Image Policy

- Use `imagePullPolicy: IfNotPresent` for local development with minikube.
- Build and load with `minikube image build -t voctomix:latest .` before applying manifests.
- In production, push to a registry and set `imagePullPolicy: Always`.

## Secrets

- RabbitMQ credentials must come from a Kubernetes Secret, not hardcoded in YAML.
- Create with: `kubectl create secret generic rabbitmq-creds --from-literal=user=voctomix --from-literal=pass=<PASSWORD>`
- Reference in manifest: `env: [{name: RABBITMQ_USER, valueFrom: {secretKeyRef: {name: rabbitmq-creds, key: user}}}]`

## Deployment Order

1. Apply `rabbitmq.yaml` and wait for Ready.
2. Apply `studio.yaml` (voctocore) and wait for Ready.
3. Apply remaining manifests (`cameras.yaml`, `blanker.yaml`, `telemetry.yaml`) — they depend on voctocore being healthy.

The `launch_k8s.sh` script enforces this order using `kubectl wait`.
