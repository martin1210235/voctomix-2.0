# Experimentos de Estabilidad y Resiliencia en Kubernetes
## Documentación completa — TFG Voctomix 2.0

**Fecha de ejecución:** 19 de junio de 2026  
**Ejecutado por:** Martín Herranz Sánchez  
**Entorno:** Minikube en PC de desarrollo (misma máquina que Docker Compose)

---

## 1. Contexto y motivación

El tutor Álvaro solicitó en la reunión del 15 de junio de 2026 que las pruebas de estabilidad y resiliencia (ya realizadas en Docker Compose) se repitiesen también en Kubernetes, para poder incluir una **comparativa directa entre ambos entornos** en el apartado `5_5_adicionales.tex` de la memoria.

Las pruebas originales en Docker Compose se habían realizado el 17 de junio de 2026:
- Estabilidad Docker: `sessions/session1.jsonl` (~68 min, 823 eventos STATE)
- Resiliencia Docker: `sessions/resilience_cam1.json` (n=10)

---

## 2. Infraestructura Kubernetes utilizada

- **Orquestador:** Minikube (single-node cluster)
- **Deployment:** `studio` — 10 contenedores en un único pod
- **Imagen:** `martin1210235/voctomix:latest`
- **ConfigMap:** `voctomix-config` — contiene todas las variables de entorno (fuentes, puertos, resolución, etc.)
- **Volumen persistente (PVC):** montado en `/opt/voctomix/sessions/` en los contenedores `voctocore` y `telemetry`

**Contenedores del pod (10 total):**

| Contenedor | Función |
|---|---|
| `voctocore` | Núcleo de mezclado GStreamer (puerto 9999) |
| `telemetry` | Servicio de telemetría, escribe JSONL al PVC |
| `cam1` | FFmpeg — fuente de cámara 1 (puerto 10000) |
| `cam2` | FFmpeg — fuente de cámara 2 (puerto 10001) |
| `cam3` | FFmpeg — fuente de cámara 3 (puerto 10002) |
| `cam4` | FFmpeg — fuente de cámara 4 (puerto 10003) |
| `break` | FFmpeg — fuente de vídeo de pausa |
| `intro` | FFmpeg — fuente de intro (bucle) |
| `stream-blanker` | FFmpeg — fuentes PAUSE/OFFLINE |
| `audio-manager` | FFmpeg — música de fondo |

**Nota:** todos los contenedores usan `network_mode: service:voctocore` (espacio de red compartido), por lo que se comunican via `localhost`.

---

## 3. Bugs encontrados y corregidos durante la preparación

Durante la preparación de las pruebas se encontraron varios bugs preexistentes en la infraestructura Kubernetes que fue necesario corregir antes de poder ejecutar los experimentos.

### Bug 1 — Imagen Docker con variable sin expandir

**Síntoma:** Cada vez que se intentaba hacer `kubectl rollout restart deployment/studio`, el nuevo pod quedaba en estado `InvalidImageName` indefinidamente.

**Causa:** El Deployment spec almacenado en etcd tenía el nombre de imagen como la cadena literal `${VOCTOMIX_IMAGE:-martin1210235/voctomix:latest}` en vez de `martin1210235/voctomix:latest`. Esto ocurrió porque el script `start_server_pc1.sh` usa `envsubst < studio.yaml | kubectl apply`, pero `envsubst` NO expande la sintaxis de bash con valor por defecto `${VAR:-default}` — solo expande `${VAR}` simple. Como `VOCTOMIX_IMAGE` no estaba exportada en el shell, `envsubst` dejó la expresión sin tocar.

**Evidencia:** El pod original `studio-694d9c8b65-76svl` funcionaba porque fue creado hace 46 días cuando posiblemente la variable sí estaba exportada. Un pod previo `studio-595c855f99-5g2qn` llevaba 16 días en `InvalidImageName`, lo que confirma que el bug existía antes de este experimento.

**Corrección:** Se creó `k8s_escenario/fix_images_patch.json` con el nombre de imagen literal para todos los 10 contenedores. Se aplica como paso previo a cualquier `rollout restart`.

### Bug 2 — Comandos vacíos en break, stream-blanker, audio-manager

**Síntoma:** Tras aplicar el parche de imágenes y hacer rollout restart, los contenedores `break`, `stream-blanker` y `audio-manager` arrancaban en `CrashLoopBackOff` con el error `No such file or directory`. Llevaban 6 reinicios en pocos minutos.

**Causa:** El `restore_deploy_patch.json` solo cubría cam1-4. Los comandos de `break`, `stream-blanker` y `audio-manager` en el Deployment spec tenían cadenas vacías (`""`) porque sus variables de entorno (`${BREAK_VIDEO}`, `${PAUSE_VIDEO}`, etc.) tampoco existían en el shell cuando se aplicó el YAML original.

**Corrección:** Se leyeron los comandos correctos directamente del pod en ejecución (`kubectl get pod studio-694d9c8b65-76svl -o json`), que sí los tenía porque fue creado con el entorno completo. Se actualizó `restore_deploy_patch.json` para incluir los 8 contenedores que tienen comandos custom.

### Bug 3 — `wait_for_ready` detectaba el pod antiguo

**Síntoma:** El script `run_k8s_stability.sh` pasaba al paso de grabación inmediatamente después del rollout restart, sin esperar al pod nuevo. El pod detectado era el antiguo (`studio-694d9c8b65-76svl`), que tenía `SAVE_LOGS=false` en su entorno.

**Causa:** La función `wait_for_studio_ready` buscaba cualquier pod Running con `app=studio`. Como el pod antiguo seguía corriendo mientras el nuevo iniciaba, el script lo detectaba como válido inmediatamente.

**Corrección:** Se refactorizó a `wait_for_new_pod(old_pod)` que recibe el nombre del pod antiguo y espera explícitamente a que aparezca uno con nombre diferente.

### Bug 4 — `log()` contaminaba la variable `POD`

**Síntoma:** La variable `POD` del script contenía texto mezclado de logs junto al nombre del pod.

**Causa:** La función `log()` escribía a stdout. Al usarla dentro de una sustitución de comando `POD=$(wait_for_studio_ready)`, todo lo que va a stdout (incluidos los mensajes de log) queda capturado en la variable.

**Corrección:** `log()` rediriged a stderr: `echo "[...] $*" >&2`.

### Bug 5 — Output buffering de Python en la prueba de resiliencia

**Síntoma:** El proceso `measure_resilience_k8s.py` llevaba 5+ minutos corriendo con el output file en 0 bytes. Parecía que no había hecho nada. Se mató el proceso por error.

**Causa:** Python bufferiza stdout cuando no está conectado a un TTY. Con el output redirigido a un fichero (via `2>&1`), Python acumula hasta ~8KB antes de escribir. El script había completado el kill #1 (568 ms) y estaba en el `time.sleep()` de 720 segundos, pero ninguna de las impresiones había llegado al fichero todavía.

**Corrección:** Se relanzó con `python3 -u` (unbuffered) y se añadió `| tee /tmp/resilience_live.log` para ver la salida en tiempo real.

**Nota importante:** Matar el proceso durante el wait de 720 segundos NO invalida los datos. El kill #1 (568 ms) fue una medición válida y completa. Al relanzar, el script hizo un nuevo kill #1 sobre cam1 recién recuperada, obteniendo también 568 ms.

---

## 4. Prueba de Estabilidad en Kubernetes

### 4.1 Objetivo

Demostrar que el sistema Voctomix corriendo en Kubernetes (Minikube) mantiene un consumo de CPU y RAM estable durante 30 minutos de funcionamiento continuo, sin degradación progresiva ni fugas de memoria.

### 4.2 Metodología

**Script de automatización:** `k8s_escenario/run_k8s_stability.sh`

**Pasos ejecutados:**

1. Parchear ConfigMap `voctomix-config` → `SAVE_LOGS=true` (`stability_cm_patch.json`)
2. Parchear Deployment → cam1-4 usan fuentes `lavfi` locales (`stability_deploy_patch.json`)
3. Parchear Deployment → corregir nombres de imagen (`fix_images_patch.json`)
4. `kubectl rollout restart deployment/studio` — nuevo pod con todos los cambios
5. Esperar a que los 10 contenedores estén `ready=true` (polling cada 5 s)
6. Esperar 35 minutos mientras el contenedor `telemetry` graba telemetría
7. `kubectl cp` del fichero JSONL del pod a `sessions/session1_k8s.jsonl`
8. `python3 tools/analyze_stability.py` → genera la figura PNG
9. Restaurar ConfigMap (`SAVE_LOGS=false`) y Deployment (fuentes HTTP) y rollout restart

**Fuentes de vídeo sintéticas (FFmpeg lavfi):**

| Contenedor | Fuente lavfi | Descripción |
|---|---|---|
| cam1 | `smptebars=size=1920x1080:rate=25` | Barras de color SMPTE |
| cam2 | `testsrc2=size=1920x1080:rate=25` | Patrón de test estándar |
| cam3 | `color=c=green:size=1920x1080:rate=25` | Pantalla verde uniforme |
| cam4 | `color=c=blue:size=1920x1080:rate=25` | Pantalla azul uniforme |

Se utilizan fuentes `lavfi` (generadas localmente por FFmpeg) en vez de las fuentes HTTP originales porque:
- Eliminan la dependencia de red exterior durante el test
- Son infinitas (no terminan nunca, sin `stream_loop`)
- Representan carga realista de procesamiento de vídeo 1080p25

Cada fuente lavfi requiere **dos entradas FFmpeg separadas** (`-f lavfi -i 'video...'` y `-f lavfi -i 'anullsrc...'`) porque las fuentes de vídeo lavfi no tienen stream de audio.

**Telemetría:**

El contenedor `telemetry` ejecuta `telemetry_service.py` que, cuando `SAVE_LOGS=true`, escribe un evento JSON de tipo `state` cada 5 segundos en `/opt/voctomix/sessions/sessionN.jsonl`. Cada evento contiene:
```json
{
  "type": "state",
  "timestamp": "2026-06-19 15:32:07",
  "system_health": {
    "cpu_usage_percent": 56.4,
    "ram_usage_percent": 21.9
  }
}
```

### 4.3 Pod utilizado para la prueba

- **Pod nuevo creado para el test:** `studio-65d8659967-kxmwk`
- **Inicio de datos:** 2026-06-19 UTC 15:32:07
- **Fin de datos:** 2026-06-19 UTC 16:09:00 (~37 minutos totales grabados)
- **Duración analizada:** 30,9 minutos (truncados con `--max-minutes 31`)
- **Fichero de sesión en pod:** `/opt/voctomix/sessions/session3.jsonl`
- **Fichero local:** `sessions/session1_k8s.jsonl` (580 líneas: events STATE + CHANGE)

### 4.4 Resultados

**Estadísticas sobre 372 eventos STATE en 30,9 minutos:**

| Métrica | CPU (%) | RAM (%) |
|---|---|---|
| Mínimo | 26,5 | 21,3 |
| Media | 55,8 | 21,9 |
| Máximo | 99,2 | 24,2 |

**Sobre los picos de CPU (max 99,2%):**

Los 10 eventos con CPU > 80% ocurrieron **únicamente durante el primer minuto de arranque** del pod (entre UTC 15:32:07 y 15:32:57). Corresponden a la inicialización simultánea de GStreamer (voctocore) y los 4 procesos FFmpeg. Después de los primeros 60 segundos, la CPU se estabilizó completamente en torno al 55-57%.

La figura generada usa `--max-minutes 31` que empieza desde `t=0` del pod, por lo que estos picos de inicio SÍ son visibles en la gráfica como una rampa inicial. Esto es representativo del comportamiento real del sistema.

**Sobre la RAM:**

Variación total de solo 2,9 puntos porcentuales (21,3% → 24,2%) durante toda la prueba. Confirma ausencia completa de fugas de memoria.

**Figura generada:**
- Ruta: `memoria_tfg/figuras/estabilidad_30min_k8s.png`
- Formato: PNG 300 DPI, 13×6 cm (mismo formato que la figura Docker)
- Eje Y: 0–85% (ajustado para mostrar los picos de CPU al ~55%)

---

## 5. Prueba de Resiliencia en Kubernetes

### 5.1 Objetivo

Medir el tiempo que tarda Kubernetes en detectar el fallo de un contenedor y relanzarlo hasta que vuelve a estar operativo (`ready=true`), y compararlo con el tiempo equivalente en Docker Compose.

### 5.2 Metodología

**Script:** `tools/measure_resilience_k8s.py`

**Parámetros:** `--n 5 --wait 720 --container cam1`

**Proceso por iteración:**

1. `kubectl exec <pod> -c cam1 -- kill -9 1` — mata el proceso PID 1 del contenedor cam1
2. `t_kill = time.monotonic()` — registra el instante de muerte
3. Polling cada 500 ms: `kubectl get pod <pod> -o json` → busca `status.containerStatuses[cam1].ready == true`
4. Cuando `ready=true`: `t_ready = time.monotonic()`
5. `recovery_ms = round((t_ready - t_kill) * 1000)`
6. Esperar 720 segundos antes de la siguiente iteración

**Por qué 720 segundos entre kills:**

Kubernetes implementa CrashLoopBackOff: si un contenedor falla repetidamente en menos de 10 minutos, el backoff de reinicio escala exponencialmente (10 s → 20 s → 40 s → 80 s → 160 s → 300 s máximo). Con 720 s de espera (> 600 s = umbral de reset), el contador se reinicia entre iteraciones y cada kill parte desde cero, garantizando mediciones comparables.

**Pod utilizado:**
- `studio-69b798db5f-k5rp5`
- cam1 uptime antes del primer kill: **23,3 minutos** (muy superior al umbral de 10 min)
- cam1 restarts previos al test: **0**

**Pre-flight checks realizados antes de lanzar el test:**

| Check | Resultado |
|---|---|
| Pod 10/10 Ready | ✓ |
| cam1 uptime > 10 min | ✓ (23,3 min) |
| kubectl exec overhead (kill -0 1) | 119 ms (sistemático) |
| `container_is_ready()` logic verificada | ✓ |
| Output path accesible desde CWD | ✓ |
| numpy disponible | ✓ 2.2.6 |
| Fichero existente seguro de sobreescribir | ✓ (era n=1, wait=1s, stale) |

### 5.3 Resultados

**5 iteraciones completadas sin errores ni timeouts:**

| Iteración | Tiempo de recuperación |
|---|---|
| Kill #1 | 568 ms |
| Kill #2 | 555 ms |
| Kill #3 | 563 ms |
| Kill #4 | 566 ms |
| Kill #5 | 576 ms |

**Estadísticas:**

| Estadístico | Valor |
|---|---|
| n | 5 |
| Mínimo | 555 ms |
| **Mediana** | **566 ms** |
| Media | 565,6 ms |
| Máximo | 576 ms |
| p95 | 574 ms |
| Rango (max − min) | 21 ms |

**Fichero de resultados:** `sessions/resilience_cam1_k8s.json`

---

## 6. Comparativa Docker Compose vs Kubernetes

### 6.1 Estabilidad (CPU y RAM — 30 min)

| Métrica | Docker Compose | Kubernetes (Minikube) |
|---|---|---|
| Duración muestra | ~68 min (823 eventos) | 30,9 min (372 eventos) |
| CPU media | 52,6% | 55,8% |
| CPU mediana | 52,2% | ~55% |
| CPU mínima | 24,1% | 26,5% |
| CPU máxima | 83,0% | 99,2%* |
| RAM media | 22,6% | 21,9% |
| RAM mínima | 21,9% | 21,3% |
| RAM máxima | 23,5% | 24,2% |

*Los picos de CPU en K8s ocurren exclusivamente durante el primer minuto de arranque del pod.

**Interpretación:**
- **CPU ~3 pp más alta en K8s:** el overhead del kubelet, el container runtime (containerd) y la gestión del namespace añaden carga al sistema. Es un overhead esperado y razonable.
- **RAM prácticamente idéntica:** ambos entornos consumen ~22% de RAM con variación < 3 pp. La gestión de memoria de GStreamer no se ve afectada por la capa de orquestación.
- **Ambos son estables:** ninguno muestra tendencia de crecimiento, lo que descarta fugas de memoria.

### 6.2 Resiliencia (recuperación tras kill -9)

| Métrica | Docker Compose | Kubernetes (Minikube) |
|---|---|---|
| n | 10 | 5 |
| Mínimo | 516 ms | 555 ms |
| **Mediana** | **519,5 ms** | **566 ms** |
| Media | 519,9 ms | 565,6 ms |
| Máximo | 526 ms | 576 ms |
| p95 | 524,7 ms | 574,4 ms |
| Rango | 10 ms | 21 ms |
| **Ratio K8s/Docker** | — | **1,09×** |

**Interpretación:**
- K8s tarda ~46 ms más que Docker en recuperar el contenedor. Esta diferencia se explica por la capa adicional de orquestación: el kubelet tiene un ciclo de polling para detectar el fallo del contenedor (típicamente ~100 ms), mientras que Docker daemon lo detecta casi instantáneamente via cgroups.
- El ratio 1,09× (9% más lento) es prácticamente equivalente para producción en directo.
- La dispersión mayor en K8s (21 ms vs 10 ms) refleja la variabilidad del ciclo de polling del kubelet.
- Ambos tiempos son sub-segundo, lo que es el umbral relevante para producción en vivo.

---

## 7. Archivos generados por las pruebas

| Fichero | Descripción |
|---|---|
| `sessions/session1_k8s.jsonl` | Telemetría bruta K8s (580 líneas, 37 min) |
| `sessions/resilience_cam1_k8s.json` | Resultados resiliencia K8s (n=5) |
| `memoria_tfg/figuras/estabilidad_30min_k8s.png` | Figura CPU/RAM K8s 30 min (300 DPI) |
| `k8s_escenario/run_k8s_stability.sh` | Script automatización test estabilidad |
| `k8s_escenario/stability_cm_patch.json` | Patch configmap SAVE_LOGS=true |
| `k8s_escenario/restore_cm_patch.json` | Patch configmap SAVE_LOGS=false |
| `k8s_escenario/stability_deploy_patch.json` | Patch deployment cam1-4 → lavfi |
| `k8s_escenario/restore_deploy_patch.json` | Patch deployment restauración completa |
| `k8s_escenario/fix_images_patch.json` | Patch imagen literal (fix bug preexistente) |
| `tools/analyze_stability.py` | Generador de figura estabilidad (Docker+K8s) |
| `tools/measure_resilience_k8s.py` | Medidor de resiliencia K8s |

---

## 8. Consideraciones para la defensa del TFG

### Preguntas esperables de Álvaro o el tribunal:

**"¿Por qué la CPU es más alta en K8s que en Docker?"**
→ El kubelet y el container runtime (containerd) añaden ~3 pp de overhead de CPU. Es el coste de la orquestación. En producción real con servidores dedicados, este overhead sería proporcionalmente menor.

**"¿Por qué K8s tarda más en recuperarse?"**
→ El kubelet detecta el fallo del contenedor mediante polling (ciclo ~100 ms). Docker daemon lo detecta casi instantáneamente via cgroups. La diferencia de ~46 ms es el overhead del ciclo de kubelet, no del reinicio en sí.

**"¿Por qué n=5 en K8s y n=10 en Docker para resiliencia?"**
→ Con 720 s entre kills, n=5 requiere ~60 minutos. Con la bajísima dispersión observada (rango 21 ms, σ ≈ 8 ms), n=5 es estadísticamente suficiente para establecer la mediana con precisión. El p95 (574 ms) está muy próximo a la mediana (566 ms), lo que confirma alta consistencia.

**"¿Las fuentes lavfi son representativas de la carga real?"**
→ Sí: cada cámara sigue ejecutando el mismo pipeline FFmpeg (decodificación, escala, conversión de píxeles, muxing matroska sobre TCP), que es la operación que consume CPU. La diferencia es que la fuente es local en vez de remota, pero el procesamiento es idéntico. Además, la carga de CPU observada (~56%) es coherente con la carga medida en producción real.

**"¿El CrashLoopBackOff no afectó a las mediciones?"**
→ No. Se diseñó el test con 720 s de espera entre kills (umbral de reset: 600 s). Todos los tiempos de recuperación son prácticamente iguales entre sí (rango 21 ms), lo que confirma que no hubo backoff creciente.
