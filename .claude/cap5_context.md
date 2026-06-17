# Contexto completo — Capítulo 5 TFG Voctomix 2.0

Este fichero documenta todo el trabajo realizado en el Capítulo 5 de la memoria
del TFG "Desarrollo y optimización de Voctomix 2.0" (ETSIT-UPM). Está pensado
para alimentar de contexto a una nueva conversación de IA.

---

## Estructura del capítulo 5

El capítulo se llama **"Pruebas de validación del sistema de producción remota de vídeo"**
y se compone de los siguientes ficheros LaTeX:

| Fichero | Contenido |
|---|---|
| `memoria_tfg/capitulos/cap5/5_1_escenarios_despliegue.tex` | Introducción al capítulo: escenarios analizados |
| `memoria_tfg/capitulos/cap5/5_2_pruebas_validacion.tex` | Secciones 5.1 (entorno de pruebas) y 5.2 (validación funcional) |
| `memoria_tfg/capitulos/cap5/5_3_resultados.tex` | Secciones 5.3 (rendimiento) y 5.4 (latencia, con subsecciones 5.4.1 y 5.4.2) |
| `memoria_tfg/capitulos/cap5/5_5_adicionales.tex` | Secciones 5.5 (estabilidad), 5.6 (overhead telemetría), 5.7 (resiliencia — pendiente) |

Todos estos ficheros están incluidos en `memoria_tfg/main.tex` mediante `\import`.

---

## Sección 5.1 — Entorno de pruebas

**Hardware del equipo:**
- CPU: Intel Core i9-10900X @ 3,70 GHz (10 núcleos / 20 hilos)
- RAM: 128 GB DDR4
- SO: Ubuntu 22.04.5 LTS (kernel 6.8.0-111)
- Docker Compose: Engine 29.1.3 / Compose v2.37.1
- Kubernetes: Minikube v1.38.1 / kubectl v1.36.0
- Red interna: Loopback (sin interfaz física)

**Señal de vídeo:** 4 fuentes FFmpeg a 1920×1080 @ 25 fps, formato RAW I420 sin compresión.
Cada cámara genera 622 Mbps. Con 4 cámaras: 2,49 Gbps total, todo por loopback.

**Dos escenarios analizados:**
1. Docker Compose (todos los servicios en un solo equipo)
2. Kubernetes con Minikube (clúster local, mismo equipo)

Los escenarios de 1 PC y 2 PCs en red local se validaron funcionalmente pero
no se instrumentaron para rendimiento.

---

## Sección 5.2 — Validación funcional

Se comprobó que cada módulo funciona correctamente en los dos escenarios.
No hay columna de "Resultado" en la tabla — se dice en el párrafo final que
"Todas las funcionalidades se verificaron con éxito en los dos escenarios".

**Tabla de validación (7 módulos verificados):**

| Módulo | Qué se verificó |
|---|---|
| Composites | Los 4 modos de combinación visual y variante mirror se aplican correctamente |
| Transiciones | Cambio animado entre composites, sin salto brusco |
| Overlay | Rótulo aparece/desaparece con animación, se desactiva automáticamente en cada corte |
| Stream blanker | Cambia entre LIVE, PAUSE y NOSTREAM al pulsar el botón |
| Audio Follows Video | Al cambiar cámara, el audio hace fundido cruzado automático |
| Telemetría (STATE) | Cada 5 s se publica en RabbitMQ con latencia < 50 ms |
| Telemetría (CHANGE) | Cada acción genera evento inmediato con latencia < 50 ms |

---

## Sección 5.3 — Rendimiento del sistema

Sesiones de 5 minutos por número de cámaras (1, 2, 3, 4) en cada entorno.
Los valores son la **mediana** de muestras tomadas cada 5 s por la telemetría.
El consumo energético se midió con sensor RAPL (`/sys/class/powercap/intel-rapl`).
Los valores netos descuentan el baseline en reposo.

### CPU en función del número de cámaras

| Cámaras | Docker Compose | Kubernetes |
|---|---|---|
| 1 | 33,5 % | 50,2 % |
| 2 | 35,2 % | 49,4 % |
| 3 | 35,8 % | 50,8 % |
| 4 | 38,8 % | 51,2 % |

**Explicación K8s vs Docker (CPU):** Kubernetes ejecuta en el mismo equipo los
4 procesos del plano de control (kube-apiserver, etcd, kube-scheduler,
kube-controller-manager). Estos elevan el consumo hasta 50,2 % incluso con
1 sola cámara. En Docker no hay equivalente. El trabajo real de mezcla es
idéntico en ambos entornos.

### RAM en función del número de cámaras

| Cámaras | Docker Compose | Kubernetes |
|---|---|---|
| 1 | 9,7 % | 12,8 % |
| 2 | 9,9 % | 13,0 % |
| 3 | 9,9 % | 13,2 % |
| 4 | 10,1 % | 13,4 % |

Diferencia de ~3 puntos entre entornos = memoria del plano de control de K8s.
GStreamer reutiliza búferes internos → añadir cámaras no incrementa RAM significativamente.

### Consumo energético neto (RAPL, W)

| Cámaras | Docker Compose | Kubernetes |
|---|---|---|
| 1 | 25,1 W | 25,2 W |
| 2 | 27,6 W | 25,3 W |
| 3 | 27,6 W | 36,1 W |
| 4 | 32,2 W | 27,1 W |

- Docker total con 4 cámaras: ~50 W (30 % del TDP del procesador de 165 W)
- Kubernetes total: >90 W (Voctomix + plano de control)
- El rango amplio en K8s (25–36 W) es porque el baseline del plano de control
  varía entre 59 y 63 W según actividad interna del clúster.

### Nota sobre K8s en la nube

El overhead de CPU/RAM de K8s es específico de Minikube local. En Amazon EKS,
Google GKE o Azure AKS, el plano de control corre en servidores del proveedor
y los recursos disponibles para Voctomix serían equivalentes a Docker Compose.

### Ancho de banda

Cálculo: 1920×1080×25×1,5×8 / 1.000.000 = **622 Mbps por cámara**
Con 4 cámaras: 4 × 622 = **2,49 Gbps**, todo por loopback interno.

---

## Sección 5.4 — Latencia del sistema

### Tabla resumen de tiempos de respuesta (4 cámaras)

| Métrica | Docker Compose | Kubernetes |
|---|---|---|
| Tiempo arranque sistema (s) | ≈20 | ≈90 |
| Tiempo pods/servicios listos (s) | ≈15 | ≈60 |
| Latencia conmutación mediana (ms) | 1,5 | 1,8 |
| Latencia conmutación p95 (ms) | 2,3 | 2,6 |

**Arranque:** Docker ≈ 35 s en total (20 s servicios + 15 s healthcheck).
Kubernetes ≈ 150 s en total (90 s Minikube + 60 s pods Ready).
En producción esto es asumible: el sistema se despliega una sola vez antes del evento.

### 5.4.1 — Latencia de conmutación de fuente

**Qué mide:** tiempo desde que se envía `set_video_a` hasta que voctocore responde
`video_status` (confirmación de que GStreamer ha procesado el cambio).

**Metodología:** 30 cambios de fuente automatizados por entorno.
Sin búfer de códec: vídeo RAW I420 sin compresión.

**Resultados:**

| Estadístico | Docker | Kubernetes |
|---|---|---|
| Mínimo | 1,0 ms | 1,4 ms |
| Mediana | 1,5 ms | 1,8 ms |
| Máximo | 2,7 ms | 4,7 ms |
| < 45 ms (ITU-R BT.1359-1) | 30/30 | 30/30 |

**Referencia ITU-R BT.1359-1:** umbral de 45 ms a partir del cual el ojo humano
detecta desincronización audio-vídeo. Docker queda 27× por debajo, K8s 25× por debajo.
Un fotograma a 25 fps = 40 ms → cualquier latencia < 40 ms es imperceptible.

La pequeña diferencia Docker/K8s se debe al salto del port-forward de kubectl.

**Histograma (distribución Docker):** la mayoría de mediciones en el rango 1,0–1,5 ms.
**Histograma (distribución K8s):** la mayoría en el rango 1,5–2,0 ms.

### 5.4.2 — Latencia de transición de composite

**Qué mide:** tiempo desde que se envía `transition <modo>(cam1,cam2)` hasta que
voctocore responde `composite <modo>`. Esta operación es DIFERENTE a la conmutación:
GStreamer tiene que calcular fotograma a fotograma la mezcla entre el modo anterior
y el nuevo durante la animación, esperando al siguiente ciclo de fotograma (cada 40 ms
a 25 fps).

**Metodología:** 32 mediciones por entorno, ciclando entre los 4 modos disponibles:
fs (fullscreen), sbs (side-by-side), pip (picture-in-picture), lec (lecture).

**Resultados:**

| Estadístico | Docker Compose | Kubernetes |
|---|---|---|
| Mínimo | 1,6 ms | 69,5 ms |
| Mediana | 2,8 ms | 79,8 ms |
| Máximo | 5,3 ms | 136,6 ms |
| Percentil 95 | 4,2 ms | 87,4 ms |

**Comparativa directa conmutación vs transición:**

| Operación | Docker Compose | Kubernetes |
|---|---|---|
| Conmutación de fuente | 1,5 ms | 1,8 ms |
| Transición de composite | 2,8 ms | 79,8 ms |

**Por qué Docker es rápido (2,8 ms):** CPU libre → GStreamer alcanza el siguiente
ciclo de fotograma casi inmediatamente → respuesta en < 1 fotograma (40 ms).

**Por qué K8s es lento (79,8 ms):** el plano de control ocupa ~50 % de CPU →
el hilo de GStreamer llega tarde al primer ciclo disponible y tiene que esperar
al siguiente. 2 ciclos × 40 ms = 80 ms. Equivale exactamente a la mediana medida.

**Verificación:** se probó NodePort (minikube IP:30999) Y port-forward (localhost:19999).
Ambos dieron resultados idénticos (~79-80 ms), confirmando que la latencia no es
de red sino de CPU.

**Impacto real:** en Docker el cambio es instantáneo. En K8s hay un retardo de
~80 ms perceptible para el operador, pero la animación se ejecuta correctamente.
En un clúster gestionado en la nube (EKS, GKE, AKS) desaparecería.

**Fichero de datos:** `sessions/composite_latency_docker.json` y `sessions/composite_latency_kubernetes.json`
**Script de medición:** `tools/measure_composite_latency.py`

**Hay dos histogramas TikZ en la memoria** (uno por entorno, escalas diferentes):
- Docker: eje X 1–6 ms, color naranja
- K8s: eje X 65–140 ms, color violeta

---

## Sección 5.5 — Estabilidad a largo plazo

**Setup:** Docker Compose con 4 cámaras + todos los servicios (stream_blanker,
audio_manager, intro, break). Fuentes generadas con FFmpeg `lavfi` (smptebars,
testsrc2, color=green, color=blue) para garantizar fuentes infinitas sin fallos.

**Fichero de configuración usado:** `docker-compose.stability.yml` (override):
- `SAVE_LOGS=true` en telemetría
- cam1: `smptebars=size=1920x1080:rate=25`
- cam2: `testsrc2=size=1920x1080:rate=25`
- cam3: `color=c=green:size=1920x1080:rate=25` (importante: testsrc tiene incompatibilidad de colorimetría con voctocore que requiere bt709; color= es compatible)
- cam4: `color=c=blue:size=1920x1080:rate=25`
- break: `color=c=black:size=1920x1080:rate=25`
- audio_manager: `anullsrc=r=48000:cl=stereo`

**Duración:** 31 minutos, 372 eventos STATE (uno cada 5 s exactos).

**Resultados:**

| Estadístico | CPU (%) | RAM (%) |
|---|---|---|
| Mediana | 51,9 | 22,2 |
| Media | 52,7 | 22,4 |
| Mínimo | 24,1 | 21,9 |
| Máximo | 83,0 | 23,5 |
| Desviación típica | 3,9 | 0,4 |
| Percentil 95 | 58,8 | 23,4 |

**Hallazgos clave:**
- RAM: desv. típica de solo 0,4 pp en 31 min → **cero fuga de memoria**
- Deriva RAM: de 22,81 % (primeros 5 min) a 22,40 % (últimos 5 min) → −0,41 pp (despreciable)
- CPU: 96,8 % del tiempo entre 40 y 60 %
- Un único pico de 83 % al minuto 4 → arranque del pipeline GStreamer (los 4 procesos de fuente negociando formatos)
- 0 reinicios de contenedor
- 6 eventos CHANGE: todos en los primeros 8 segundos (sincronización inicial), ninguno durante la retransmisión

**Script de análisis:** `tools/analyze_stability.py`
**Fichero de datos:** `sessions/session1.jsonl` (creció hasta 68 min mientras el stack seguía activo)
**Figura generada:** `memoria_tfg/figuras/estabilidad_30min.png` (matplotlib, 300 DPI, 13×6 cm)

---

## Sección 5.6 — Overhead de la telemetría

**Pregunta que responde:** ¿cuánta CPU extra consume el servicio de telemetría?
Si fuera significativa, los datos del apartado 5.3 estarían inflados.

**Metodología:**
1. CPU con telemetría activa: mediana de últimos 5 min de sesión → 53,1 %
2. `docker compose stop telemetry` → espera 30 s → leer `/proc/stat` del host cada 5 s durante 5 min

**Resultados:**

| | Con telemetría | Sin telemetría |
|---|---|---|
| CPU mediana (%) | 53,1 | 55,2 |
| CPU media (%) | 53,3 | 55,4 |
| Desviación típica | — | 1,7 |
| Diferencia | −2,1 pp (dentro del ruido) | |

**Conclusión:** la diferencia de −2,1 pp (con signo negativo: sin telemetría la CPU
fue por azar ligeramente más alta) está dentro de la variación natural del sistema
(desv. típica 1,7 pp). El overhead de la telemetría es **indistinguible del ruido
de medición**. Los datos del capítulo reflejan el coste real de Voctomix, no del
sistema de monitorización.

**Fichero de datos:** `sessions/cpu_no_telemetry.json` (60 muestras de 5 s)

---

## Sección 5.7 — Resiliencia y recuperación (EN EJECUCIÓN al cierre del contexto)

**Qué mide:** tiempo desde `docker stop cam1` hasta que el contenedor vuelve a
estar `healthy`. Incluye: detección del fallo → restart automático de Docker
(`restart: on-failure`) → FFmpeg arranca → se conecta al socket TCP de voctocore
→ healthcheck pasa.

**Metodología:** 10 iteraciones, contenedor `cam1`, espera 2 s entre iteraciones.
El script hace polling cada 0,5 s sobre `docker inspect`.

**Script:** `tools/measure_resilience.py`
**Estado al cierre del contexto:** prueba en ejecución, resultados pendientes de escribir en sección 5.7.

**Resultado esperado:** ~5–15 s de recuperación en Docker. Voctocore no debe caer
(fallo de fuente ≠ fallo del núcleo mezclador).

---

## Estructura de ficheros creados para las pruebas

```
sessions/
  session1.jsonl                      — JSONL con STATE/CHANGE events (68 min, SAVE_LOGS=true)
  composite_latency_docker.json       — 32 mediciones transición composite Docker
  composite_latency_kubernetes.json   — 32 mediciones transición composite K8s (NodePort)
  composite_latency_kubernetes_pf.json — 32 mediciones K8s vía port-forward (confirmación)
  cpu_no_telemetry.json               — 60 muestras CPU sin contenedor telemetría
  resilience_cam1.json                — PENDIENTE: 10 iteraciones stop/recovery cam1

tools/
  analyze_stability.py                — lee JSONL, genera estabilidad_30min.png
  measure_composite_latency.py        — mide latencia transition → composite (args: --host --port --n --label)
  measure_resilience.py               — mide tiempo recovery tras docker stop (args: --container --n)

docker-compose.stability.yml          — override: SAVE_LOGS=true + fuentes lavfi para todas las cámaras
```

---

## Detalles técnicos importantes del protocolo de voctocore

- Puerto de control: **9999 TCP**, protocolo línea a línea
- Conmutación de fuente: `set_video_a cam1` → respuesta: `video_status cam1 cam2`
- Transición de composite: `transition sbs(cam1,cam2)` → respuesta: `composite sbs(cam1,cam2)`
  - ⚠️ `set_composite_mode` NO funciona — voctogui usa `cut`/`transition` con formato `modo(srcA,srcB)`
- Modos de composite disponibles: `fs`, `sbs`, `pip`, `lec` (definidos en `voctocore/default-config.ini`, línea `composites=sbs,pip,lec` más `fs` implícito)
- La respuesta a `transition` es **una sola línea** `composite <modo(srcA,srcB)>`, no `composite_mode_and_video_status`

---

## Formato y estilo LaTeX del capítulo 5

- Todas las tablas: `\begin{table}[H]`, `\centering`, `\caption{...}`, `\label{...}`, `\small`, `\begin{tabular}{|l|c|c|}`, `\hline` entre cada fila (no solo header y footer)
- Gráficas de barras: TikZ con `pgfplots`, `ybar interval`, `width=12cm, height=5.5cm`
- Figuras externas: `\includegraphics[width=\textwidth]{figuras/nombre.png}` con `[H]`
- Lenguaje: español, registro sencillo y directo, evitar tecnicismos innecesarios
- Sin guiones ortográficos (—), sustituir por coma o dos puntos
- Sin subsecciones con `\subsection*` en secciones cortas

---

## Números clave para defender ante el tribunal

| Pregunta del tribunal | Respuesta |
|---|---|
| ¿Cuánto tarda el sistema en cambiar de cámara? | 1,5 ms mediana en Docker, 1,8 ms en K8s. 27× por debajo del umbral ITU-R de 45 ms |
| ¿Y en cambiar el modo de composición? | 2,8 ms en Docker. En K8s sube a 79,8 ms por la contención de CPU del plano de control |
| ¿Es estable durante una retransmisión larga? | Sí: 31 min sin reinicios, RAM con desv. típica de 0,4 pp, cero fuga de memoria |
| ¿La telemetría afecta al rendimiento? | No: overhead indistinguible del ruido (diferencia −2,1 pp, dentro de la variación natural de 1,7 pp std) |
| ¿Qué pasa si cae una cámara? | Docker la recupera automáticamente en ~X s (sección 5.7 pendiente) |
| ¿Por qué K8s consume más CPU? | El plano de control de Minikube (4 procesos) añade ~16 pp fijos independientemente del número de cámaras |
| ¿Por qué Kubernetes en vez de la nube? | Validación funcional local. En EKS/GKE/AKS el plano de control corre en servidores del proveedor y los costes se equiparan a Docker Compose |
| ¿Cuánto ancho de banda genera el sistema? | 622 Mbps por cámara (RAW I420 1080p25). Con 4 cámaras: 2,49 Gbps por loopback interno |
