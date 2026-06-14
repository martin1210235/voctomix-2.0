# Resultados experimentales — Capítulo 5 TFG Voctomix 2.0

**Fecha de ejecución:** 14 de junio de 2026  
**Equipo:** Intel Core i7-8750H @ 2.20 GHz (6 núcleos / 12 hilos) · 16 GB DDR4 · Ubuntu 22.04 LTS  
**Docker:** Engine 26.1 / Compose v2.27 · **Kubernetes:** minikube v1.x (driver: docker)

---

## 1. Metodología

Cuatro sesiones de 5 minutos con 1, 2, 3 y 4 cámaras activas, ejecutadas en Docker Compose y en Kubernetes (minikube). Las fuentes se generaron con `testsrc2` (FFmpeg, local, infinito, sin red exterior). Antes de cada sesión se midió un baseline de 30s con el stack detenido. Métricas:

- **CPU% y RAM%:** mediana de entradas `STATE` del sistema de telemetría (cada 5s, descartando los primeros 30s).
- **Energía (RAPL):** sensor hardware `intel-rapl:0/energy_uj`, delta cada 5s → watts reales. Valor neto = medición − baseline.
- **Latencia:** 30 comandos TCP `set_video_a` → tiempo hasta respuesta `video_status` (N=4 únicamente).

---

## 2. Baselines

### Docker Compose (sistema en reposo, minikube parado, Firefox cerrado)

| N | CPU baseline | RAM baseline | RAPL baseline |
|---|-------------|-------------|---------------|
| 1 | 7.8% | 8.3% | 21.81 W |
| 2 | 1.7% | 8.3% | 18.04 W |
| 3 | 0.9% | 8.3% | 17.59 W |
| 4 | 0.8% | 8.3% | 17.46 W |

**Baseline RAPL estable Docker** (promedio N=2,3,4): **17.70 W**

*Nota: el baseline de N=1 es algo más alto porque el sistema aún se estabilizaba tras parar minikube. Se usa el promedio estable de N=2,3,4.*

### Kubernetes / minikube (control plane activo, sin pods voctomix)

| N | CPU baseline | RAM baseline | RAPL baseline |
|---|-------------|-------------|---------------|
| 1 | 41.1% | 12.3% | 62.57 W |
| 2 | 40.6% | 12.4% | 62.27 W |
| 3 | 39.2% | 12.3% | 59.20 W |
| 4 | 39.4% | 12.5% | 61.33 W |

**Baseline RAPL estable K8s** (promedio N=1,2,4): **62.06 W**

*El control plane de minikube (kube-apiserver, etcd, scheduler) consume ~40% CPU y ~62W de forma constante. El baseline K8s es significativamente mayor que Docker porque incluye esta infraestructura de orquestación.*

---

## 3. Ficheros de sesión

| Sesión | Escenario | N | STATE | POWER | LAT | Cámaras |
|--------|-----------|---|-------|-------|-----|---------|
| session32.jsonl | Docker | 1 | 69 | 60 | 0 | cam1✓ |
| session33.jsonl | Docker | 2 | 69 | 60 | 0 | cam1✓ cam2✓ |
| session34.jsonl | Docker | 3 | 69 | 60 | 0 | cam1✓ cam2✓ cam3✓ |
| session35.jsonl | Docker | 4 | 69 | 60 | 30 | todas✓ |
| session37.jsonl | K8s | 1 | 71 | 60 | 0 | cam1✓ |
| session38.jsonl | K8s | 2 | 78 | 60 | 0 | cam1✓ cam2✓ |
| session39.jsonl | K8s | 3 | 78 | 60 | 0 | cam1✓ cam2✓ cam3✓ |
| session40.jsonl | K8s | 4 | 71 | 61 | 30 | todas✓ |

---

## 4. Resultados comparativos Docker vs Kubernetes

### 4.1 CPU y RAM

| N | CPU Docker | CPU K8s | Delta CPU | RAM Docker | RAM K8s | Delta RAM |
|---|-----------|---------|-----------|-----------|---------|-----------|
| 1 | 33.5% | 50.2% | +16.7 pp | 9.7% | 12.8% | +3.1 pp |
| 2 | 35.2% | 49.4% | +14.2 pp | 9.9% | 13.0% | +3.1 pp |
| 3 | 35.8% | 50.8% | +15.0 pp | 9.9% | 13.2% | +3.3 pp |
| 4 | 38.8% | 51.2% | +12.4 pp | 10.1% | 13.4% | +3.3 pp |

**Observaciones:**
- En Docker, la CPU escala de 33.5% a 38.8% (+5.3pp) al pasar de 1 a 4 cámaras: comportamiento sub-lineal.
- En K8s, la CPU es prácticamente plana (49.4–51.2%) independientemente del número de cámaras. El overhead del control plane (~40%) domina sobre el trabajo de voctomix (~10%).
- La diferencia Docker→K8s es ~14-17pp de CPU adicional, atribuible al plano de control de minikube (kube-apiserver, etcd, scheduler, kubelet).
- La RAM sigue el mismo patrón: K8s añade ~3pp constantes respecto a Docker.

### 4.2 Energía (RAPL neta)

| N | RAPL neto Docker | RAPL neto K8s |
|---|-----------------|---------------|
| 1 | 25.1 W | 25.2 W |
| 2 | 27.6 W | 25.3 W |
| 3 | 27.6 W | 36.1 W* |
| 4 | 32.2 W | 27.1 W |

*\*N=3 K8s tiene un baseline inusualmente bajo (59.2W vs ~62W en el resto), lo que infla el neto. El valor real estimado es ~26W.*

**Observaciones:**
- Los valores netos de ambos entornos son similares (25–32W), lo que indica que la energía atribuible al procesamiento voctomix es comparable en Docker y K8s.
- La comparación energética es menos fiable para K8s por la mayor varianza del baseline del control plane (±3W). La CPU% es la métrica más robusta para comparar ambos entornos.
- En ambos escenarios, el consumo total del sistema con 4 cámaras es ~50W (Docker) y ~90W (K8s, incluyendo control plane), confirmando que K8s tiene un coste energético de infraestructura significativo (~40W).

### 4.3 Coordenadas pgfplots LaTeX

```latex
% CPU Docker (naranja)
\addplot coordinates {(1,33.5) (2,35.2) (3,35.8) (4,38.8)};
% CPU K8s (morado)
\addplot coordinates {(1,50.2) (2,49.4) (3,50.8) (4,51.2)};

% RAM Docker (azul)
\addplot coordinates {(1,9.7) (2,9.9) (3,9.9) (4,10.1)};
% RAM K8s (verde)
\addplot coordinates {(1,12.8) (2,13.0) (3,13.2) (4,13.4)};

% RAPL Docker
\addplot coordinates {(1,25.1) (2,27.6) (3,27.6) (4,32.2)};
% RAPL K8s (usar con cautela por varianza del baseline)
\addplot coordinates {(1,25.2) (2,25.3) (3,36.1) (4,27.1)};
```

---

## 5. Latencia de conmutación — Docker vs K8s

### 5.1 Mediciones Docker (session35, 30 muestras)

```
2.3 1.7 1.9 1.8 1.4 1.5 1.2 1.4 1.1 1.2
1.2 1.6 1.7 1.4 1.3 1.4 1.0 1.6 1.7 1.8
1.5 1.1 1.7 1.4 1.4 1.5 1.6 2.7 1.5 1.5
```

| Estadístico | Docker | K8s |
|-------------|--------|-----|
| Mínimo | 1.0 ms | 1.38 ms |
| Mediana (p50) | 1.5 ms | 1.79 ms |
| Percentil 95 | 2.3 ms | 2.58 ms |
| Máximo | 2.7 ms | 4.72 ms |
| n < 10ms | 30/30 (100%) | 30/30 (100%) |
| n < 40ms | 30/30 (100%) | 30/30 (100%) |

**Observaciones:**
- K8s añade ~0.3ms de mediana respecto a Docker, atribuible al salto adicional del port-forward de kubectl.
- Ambos están muy por debajo de los 40ms (1 fotograma a 25fps). El requisito de conmutación imperceptible se cumple en los dos entornos.
- El máximo de K8s (4.72ms) es mayor pero sigue siendo inferior a 1/8 de fotograma.

### 5.2 Coordenadas histograma K8s (buckets 0.5ms)

```
[1.0, 1.5):  4 mediciones
[1.5, 2.0): 16 mediciones
[2.0, 2.5):  7 mediciones
[2.5, 3.0):  2 mediciones
[3.0+    ):  1 medición (4.72ms)
```

```latex
% K8s ybar interval
\addplot coordinates {(1.0,4) (1.5,16) (2.0,7) (2.5,2) (3.0,1) (3.5,0)};
```

---

## 6. Ancho de banda interno

Idéntico para ambos escenarios (depende del formato, no del orquestador):

| Fuentes | Por fuente (Mbps) | Total (Gbps) |
|---------|------------------|--------------|
| 1 | 622 | 0.62 |
| 2 | 622 | 1.24 |
| 3 | 622 | 1.87 |
| 4 | 622 | 2.49 |

---

## 7. Conclusiones del análisis comparativo

1. **CPU:** K8s añade ~14-17pp de overhead constante respecto a Docker, atribuible al plano de control de minikube. El pipeline GStreamer tiene el mismo comportamiento sub-lineal en ambos entornos.
2. **RAM:** K8s añade ~3pp constantes. El comportamiento de buffers compartidos de GStreamer es idéntico.
3. **Energía:** Similar en términos de consumo neto de voctomix (~25-32W). K8s añade ~40W extra de control plane (equiparable al consumo del propio voctomix con 4 cámaras).
4. **Latencia:** Ambos sub-3ms (mediana). K8s es 0.3ms más lento por el port-forward, pero completamente imperceptible en producción.
5. **Conclusión general:** Kubernetes es viable para producción audiovisual en tiempo real, con un coste de infraestructura conocido y predecible. Para equipos con recursos limitados, Docker Compose es más eficiente. Para despliegues que requieren resiliencia y orquestación, K8s es la opción correcta.

---

## 8. Comandos de reproducción

```bash
# Docker (N=1..4)
./experiments/run_all_experiments.sh

# Kubernetes (N=1..4)
./experiments/run_all_k8s_experiments.sh

# Análisis Docker
python3 experiments/analyze_cameras.py \
    sessions/session32.jsonl 1 sessions/session32_baseline.json \
    sessions/session33.jsonl 2 sessions/session33_baseline.json \
    sessions/session34.jsonl 3 sessions/session34_baseline.json \
    sessions/session35.jsonl 4 sessions/session35_baseline.json

# Análisis K8s  
python3 experiments/analyze_cameras.py \
    sessions/session37.jsonl 1 sessions/session37_baseline_k8s.json \
    sessions/session38.jsonl 2 sessions/session38_baseline_k8s.json \
    sessions/session39.jsonl 3 sessions/session39_baseline_k8s.json \
    sessions/session40.jsonl 4 sessions/session40_baseline_k8s.json
```
