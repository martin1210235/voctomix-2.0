# Resumen global de resultados (3 escenarios × 4 formatos)

CPU/RAM leídos de /proc (igual que htop). Latencia = vídeo real (glass-to-glass). Formatos verificados con ffprobe.

## Rendimiento — CPU mediana por nº de cámaras (0→4)


**1080p25**

| escenario | 0c | 1c | 2c | 3c | 4c |
|---|---|---|---|---|---|
| docker | 30% | 37% | 45% | 61% | 89% |
| local | 29% | 36% | 44% | 60% | 90% |
| k8s | 34% | 35% | 43% | 59% | 89% |

**1080p50**

| escenario | 0c | 1c | 2c | 3c | 4c |
|---|---|---|---|---|---|
| docker | 37% | 44% | 54% | 71% | 86% |
| local | 36% | 43% | 53% | 70% | 86% |
| k8s | 39% | 44% | 54% | 71% | 86% |

**2160p25**

| escenario | 0c | 1c | 2c | 3c | 4c |
|---|---|---|---|---|---|
| docker | 41% | 52% | 65% | 80% | 92% |
| local | 39% | 50% | 63% | 79% | 92% |
| k8s | 44% | 50% | 63% | 80% | 91% |

**2160p50**

| escenario | 0c | 1c | 2c | 3c | 4c |
|---|---|---|---|---|---|
| docker | 49% | 58% | 68% | 80% | 90% |
| local | 49% | 57% | 67% | 77% | 87% |
| k8s | 53% | 58% | 68% | 78% | 88% |

## Rendimiento — RAM mediana a 4 cámaras (escalado)

| escenario | 1080p25 | 1080p50 | 2160p25 | 2160p50 |
|---|---|---|---|---|
| docker | 11% | 10% | 18% | 18% |
| local | 10% | 10% | 12% | 12% |
| k8s | 10% | 10% | 12% | 12% |

## Sostenida (2 h) — CPU mediana

| escenario | 1080p25 | 1080p50 | 2160p25 | 2160p50 |
|---|---|---|---|---|
| docker | 90% | 87% | 94% | 87% |
| local | 89% | 86% | 91% | 84% |
| k8s | 88% | 87% | 91% | 86% |

## Sostenida (2 h) — RAM mediana

| escenario | 1080p25 | 1080p50 | 2160p25 | 2160p50 |
|---|---|---|---|---|
| docker | 9% | 9% | 14% | 15% |
| local | 9% | 9% | 10% | 11% |
| k8s | 10% | 10% | 12% | 12% |

## Latencia 2.1 — conmutación de cámara (mediana)

| escenario | 1080p25 | 1080p50 | 2160p25 | 2160p50 |
|---|---|---|---|---|
| docker | 293 ms | 194 ms | 295 ms | 177 ms |
| local | 330 ms | 176 ms | 295 ms | 204 ms |
| k8s | 292 ms | 193 ms | 254 ms | 116 ms |

## Latencia 2.2 — conmutación de composición (mediana)

| escenario | 1080p25 | 1080p50 | 2160p25 | 2160p50 |
|---|---|---|---|---|
| docker | 296 ms | 197 ms | 257 ms | 335 ms |
| local | 296 ms | 196 ms | 258 ms | 243 ms |
| k8s | 296 ms | 193 ms | 219 ms | 205 ms |

## Resiliencia — MTTR (mediana)

| escenario | 1080p25 | 1080p50 | 2160p25 | 2160p50 |
|---|---|---|---|---|
| docker | 1794 ms | 1255 ms | 1660 ms | 1887 ms |
| local | 1797 ms | 1178 ms | 1539 ms | 1577 ms |
| k8s | 2078 ms | 898 ms | 796 ms | 1957 ms |

## Hallazgos clave

- **CPU**: escala con nº de cámaras y con la resolución. A 4 cámaras el sistema satura (~90%) y a 4K/50fps descarta frames (techo de hardware). Los 3 escenarios son comparables.
- **RAM**: sobrecarga de despliegue **Docker > K8s > Local** (contenedores añaden memoria).
- **RAM sostenida**: Docker a 4K crece hasta ~17,7% y se estabiliza (no es leak descontrolado; confirmado con sostenida de 24 h). Local y K8s planos.
- **Latencia**: depende del framerate (≈mitad a 50 fps), no de la resolución. Docker a 4K50 muestra composición inestable por saturación.
- **MTTR**: ~1–2 s en los 3 escenarios; recuperación por restart-policy (Docker) / supervisor (Local) / self-healing del ReplicaSet (K8s).
