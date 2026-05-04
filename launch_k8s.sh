#!/bin/bash
set -e

echo "--- Cleaning up previous session ---"
pkill -f "kubectl port-forward" 2>/dev/null || true
pkill -f "voctogui.py" 2>/dev/null || true
sleep 1

MINIKUBE_IP=$(minikube ip 2>/dev/null)
if [ -z "$MINIKUBE_IP" ]; then
  echo "ERROR: minikube is not running. Start it with: minikube start"
  exit 1
fi

POD=$(kubectl get pod -l app=studio --field-selector=status.phase=Running \
  -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
if [ -z "$POD" ]; then
  echo "ERROR: studio pod not running. Deploy first with: kubectl apply -f k8s/"
  exit 1
fi

echo "Studio pod: $POD"

READY=$(kubectl get pod "$POD" -o jsonpath='{.status.containerStatuses[*].ready}' 2>/dev/null)
NOT_READY=$(echo "$READY" | tr ' ' '\n' | grep -c "false" || true)
if [ "$NOT_READY" -gt 0 ]; then
  echo "WARNING: $NOT_READY container(s) not ready yet. Waiting..."
  kubectl wait --for=condition=ready pod/"$POD" --timeout=60s 2>/dev/null || true
fi

echo "Setting up port-forward..."
kubectl port-forward pod/$POD \
  9999:9999 9998:9998 11000:11000 12000:12000 \
  14000:14000 14001:14001 14002:14002 \
  14003:14003 14004:14004 14005:14005 > /tmp/voctomix-pf.log 2>&1 &
PF_PID=$!

cleanup() {
  echo ""
  echo "--- Shutting down ---"
  kill $PF_PID 2>/dev/null || true
  kill $LOG_PID 2>/dev/null || true
}
trap cleanup EXIT

echo "Waiting for port-forward..."
for i in $(seq 1 15); do
  sleep 1
  if grep -q "Forwarding from" /tmp/voctomix-pf.log 2>/dev/null; then
    break
  fi
  if ! kill -0 $PF_PID 2>/dev/null; then
    echo "ERROR: port-forward failed."
    cat /tmp/voctomix-pf.log
    exit 1
  fi
done

echo "Port-forward ready."
echo "--- Telemetry ---"
kubectl logs -f pod/$POD -c telemetry --since=1s 2>/dev/null &
LOG_PID=$!

cd "$(dirname "$0")/voctogui"

while true; do
  python3 voctogui.py -H localhost 2>/dev/null
  EXIT_CODE=$?
  if [ $EXIT_CODE -eq 0 ] || [ $EXIT_CODE -eq 130 ]; then
    break
  fi
  echo "GUI crashed (exit $EXIT_CODE), restarting in 2s... (Ctrl+C to stop)"
  sleep 2
done
