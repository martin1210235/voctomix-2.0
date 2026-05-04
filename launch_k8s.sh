#!/bin/bash
set -e

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
echo "Setting up port-forward..."

kubectl port-forward pod/$POD \
  9999:9999 9998:9998 11000:11000 12000:12000 \
  14000:14000 14001:14001 14002:14002 \
  14003:14003 14004:14004 14005:14005 > /tmp/voctomix-pf.log 2>&1 &
PF_PID=$!

cleanup() {
  kill $PF_PID 2>/dev/null
}
trap cleanup EXIT

sleep 3

if ! nc -zw2 localhost 9999 2>/dev/null; then
  echo "ERROR: port-forward failed. Check /tmp/voctomix-pf.log"
  exit 1
fi

echo "Port-forward ready. Launching GUI..."
cd "$(dirname "$0")/voctogui"
python3 voctogui.py -H localhost
