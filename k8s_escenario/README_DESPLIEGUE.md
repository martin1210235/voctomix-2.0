# Despliegue de Voctomix en Kubernetes (k3s)

Cómo está montado el escenario de Kubernetes para las pruebas del paper. Pensado para
consultar y para justificar la implementación.

## ¿Por qué k3s y no minikube?
Los tutores pidieron **kind o k3s, no minikube**. Motivo: minikube levanta el clúster
**dentro de un contenedor de Docker**, así que medirlo sería medir Docker otra vez. **k3s**
es una distribución de Kubernetes **real y ligera instalada directamente en el host** (usa
containerd, sin Docker), así que mide la **orquestación real** sobre el hardware. Es la
comparación honesta que necesita el paper: nativo < Docker < Kubernetes.

## Instalación (los "2 comandos")
```bash
# 1) Instalar k3s (kubeconfig legible para usar kubectl sin sudo)
curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="--write-kubeconfig-mode 644" sh -
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

# 2) Importar nuestra imagen al containerd de k3s (OJO: namespace k8s.io)
docker save voctomix-voctocore:latest | sudo k3s ctr -n k8s.io images import -

# Comprobar
kubectl get nodes                                  # -> Ready, control-plane
sudo k3s ctr -n k8s.io images ls | grep voctomix   # -> imagen presente
```
Detalle importante: la imagen debe ir al namespace de containerd **`k8s.io`** (donde mira el
kubelet). Sin `-n k8s.io`, los pods dan `ErrImageNeverPull`.

## Arquitectura del despliegue
Todo corre como **pods** en el namespace `voctomix-exp`, con `hostNetwork: true` (usan la red
del host, así las cámaras hablan al núcleo por `localhost`, igual que en Docker/Local → medida
comparable):
- **voctocore** (Deployment): el mezclador. Lee el formato de un **ConfigMap**.
- **support** (Deployment): fuentes de apoyo (stream-blanker, audio, break, intro).
- **cam1..cam4** (Deployments): las 4 cámaras (BBB con marcador de color o color sólido).

## Ficheros clave
| Fichero | Qué hace |
|---|---|
| `experiments/namespace.yaml` | Crea el namespace aislado `voctomix-exp`. |
| `experiments/voctocore.yaml` | Manifiesto del núcleo: `hostNetwork`, ConfigMap de formato, `strategy: Recreate` (evita conflicto de puertos al reiniciar), sin límite de CPU. |
| `experiments/gen_camera_manifests.py` | Genera los Deployments de las 4 cámaras por formato y perfil (experiment=BBB+marcador, latency=color sólido), con bt709 y el vídeo montado por hostPath. |
| `experiments/gen_support_manifest.py` | Genera el Deployment de soporte (stream-blanker, audio, break, intro) por formato. |
| `experiments/k8s_scenario.sh` | **Gestor**: `up/cams/scale/crash/verify-format/mix-frame/down`. Despliega, cambia formato, activa cámaras y simula caídas. |
| `../experiments/comprehensive/measure_performance_k8s.py` | Rendimiento (1.1/1.2): CPU/RAM por `/proc`, con baseline de 0 cámaras. |
| `../experiments/comprehensive/run_matrix_k8s.py` | Orquestador de la matriz (4 formatos × 5 análisis) con checkpoints, reintentos, gate y verificación ffprobe por celda. |

## Cómo se despliega y se controla (gestor)
```bash
bash experiments/k8s_scenario.sh up 1080p25            # namespace + configmap + soporte + voctocore
bash experiments/k8s_scenario.sh cams 1080p25 experiment   # las 4 cámaras
bash experiments/k8s_scenario.sh verify-format 1080p25     # ffprobe de la salida real
kubectl get pods -n voctomix-exp                        # ver todo Running
bash experiments/k8s_scenario.sh down                   # borrar el namespace = limpiar
```

## Cambio de formato (ConfigMap)
`k8s_scenario.sh up <fmt>` ejecuta `set_format.sh` (reescribe los `videocaps`), crea un
**ConfigMap** `voctocore-config` con esa config y lo monta en el pod de voctocore. Cambiar de
formato = nuevo ConfigMap + reinicio. Se verifica con `ffprobe` que la salida sale a la
resolución pedida.

## Auto-recuperación (self-healing) — análisis de resiliencia
La caída de una cámara se simula borrando su pod:
```bash
kubectl delete pod -n voctomix-exp -l app=cam1 --grace-period=0 --force
```
El **Deployment (ReplicaSet) recrea el pod automáticamente** y la cámara se reconecta al núcleo.
El tiempo hasta que el vídeo vuelve es el **MTTR** que medimos. Eso es el self-healing de
Kubernetes, la ventaja frente a Docker/nativo.

## Medición
- **CPU/RAM**: se leen de `/proc` (misma fuente que htop); los pods corren en el host, así que
  el consumo global = k3s + pods = coste del despliegue Kubernetes.
- **Latencia y resiliencia**: por `hostNetwork` se miden igual que en los otros escenarios
  (puerto de control 9999, salida del mix 11000).
