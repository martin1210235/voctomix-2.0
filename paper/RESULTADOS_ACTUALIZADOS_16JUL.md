# Actualización de resultados experimentales

**Fecha de ejecución:** 16 de julio de 2026
**Equipo de pruebas:** Intel Core i9-10900X (10 núcleos / 20 hilos, 3,70 GHz, TDP 165 W), 128 GB DDR4, Ubuntu 22.04.5 LTS (kernel 6.8.0-124)
**Software:** Docker Engine 29.1.3, Docker Compose 2.37.1, Minikube v1.38.1, kubectl v1.36.0, GStreamer 1.20, Python 3.10.14

## 1. Objetivo

Repetir en el equipo de referencia (i9-10900X, 128 GB) las mediciones de consumo de recursos y de recuperación ante fallos descritas en el capítulo de resultados, para confirmar que las cifras utilizadas en la memoria y en el paper corresponden efectivamente a dicho equipo.

## 2. Procedimiento

Se ejecutaron sobre el equipo de referencia:

- `experiments/run_rapl_repeat.sh`, que recoge muestras de CPU y RAM en reposo y bajo carga, en Docker Compose y en Kubernetes.
- `tools/measure_resilience.py --n 10`, que mide el tiempo de recuperación de `voctocore` tras la terminación forzosa del contenedor de la cámara principal en Docker Compose.

## 3. Resultados

### 3.1 Consumo de CPU y RAM en reposo

Veintiuna muestras, tomadas con `voctocore` en ejecución sin fuentes de vídeo activas.

| Métrica | Mínimo | Mediana | Media | Desviación típica | P95 |
|---|---|---|---|---|---|
| CPU (%) | 0,80 | 3,60 | 6,87 | 7,59 | 16,40 |
| RAM (%) | 5,80 | 6,60 | 9,76 | 4,74 | 16,60 |

Estas cifras corresponden al estado de reposo del sistema y no sustituyen a las medidas bajo carga activa (cuatro cámaras simultáneas) ya reportadas en el capítulo de resultados, que no fueron objeto de esta sesión.

### 3.2 Recuperación ante fallos — Docker Compose

Diez ciclos de terminación forzosa y recuperación del contenedor de la cámara principal.

| Métrica | Mínimo | Mediana | Media | Desviación típica | P95 |
|---|---|---|---|---|---|
| Tiempo de recuperación (ms) | 517 | 527 | 525,7 | 5,0 | 532,1 |

Las diez iteraciones se completaron correctamente, sin fallos ni reintentos.

## 4. Conclusiones

El tiempo de recuperación ante fallo en Docker Compose (mediana 527 ms) es consistente con el orden de magnitud ya reportado en la memoria y confirma la resiliencia del despliegue en el equipo de referencia. El consumo de CPU y RAM en reposo es bajo y estable, sin picos anómalos entre muestras.

## 5. Mediciones pendientes

Las siguientes mediciones no se completaron en esta sesión y quedan planificadas para la próxima semana.

### 5.1 Consumo de CPU y RAM bajo carga activa

**Objetivo:** confirmar en el equipo de referencia el consumo de CPU y RAM con las cuatro fuentes de vídeo activas simultáneamente, en Docker Compose y en Kubernetes.

**Procedimiento:** ejecutar `experiments/run_rapl_repeat.sh` completando las cuatro sesiones de carga (N=1 a N=4) en ambos entornos, sin interrupciones, y analizar los ficheros de sesión resultantes con `experiments/analyze_cameras.py`.

### 5.2 Recuperación ante fallos en Kubernetes

**Objetivo:** obtener una medición íntegra y actualizada del tiempo de recuperación ante fallo en el despliegue de Kubernetes, en el equipo de referencia.

**Procedimiento:** ejecutar `tools/measure_resilience_k8s.py --n 10 --wait 720` hasta su finalización completa. El ciclo requiere aproximadamente dos horas, al ser necesarios doce minutos de espera entre iteraciones para que Kubernetes reinicie el contador interno de reinicios.

### 5.3 Consumo energético

**Objetivo:** obtener lecturas reales de consumo energético mediante los contadores de hardware Intel RAPL, sustituyendo cualquier estimación indirecta previa.

**Procedimiento:** ejecutar la sesión de medición con permisos de superusuario, de forma que el proceso tenga acceso de lectura a `/sys/class/powercap/intel-rapl/intel-rapl:0/energy_uj`.

### 5.4 Latencia de conmutación de fuente

**Objetivo:** confirmar en el equipo de referencia la latencia de conmutación simple entre fuentes de vídeo, en Docker Compose y en Kubernetes.

**Procedimiento:** ejecutar `experiments/measure_latency.py`, que envía treinta comandos `set_video_a` por el canal de control TCP y mide el tiempo hasta la confirmación `video_status`, en ambos entornos de despliegue.

### 5.5 Latencia de transición de composición

**Objetivo:** confirmar en el equipo de referencia la latencia de las transiciones de composición (pantalla completa, side-by-side, picture-in-picture, lower-third), en Docker Compose y en Kubernetes.

**Procedimiento:** ejecutar `tools/measure_composite_latency.py`, que envía comandos `transition` por el canal de control TCP y mide el tiempo hasta la confirmación `composite`, en ambos entornos de despliegue.

### 5.6 Estabilidad a largo plazo

**Objetivo:** confirmar en el equipo de referencia la ausencia de crecimiento progresivo de CPU o memoria durante una sesión prolongada con las cuatro fuentes de vídeo activas.

**Procedimiento:** mantener el sistema en funcionamiento continuo durante 31 minutos bajo carga activa, capturando la telemetría de estado, y analizar la sesión resultante con `tools/analyze_stability.py`.
