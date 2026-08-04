# Comparación de re-ejecuciones (escalados) vs oficiales

CPU% mediana por nº de cámaras (0→4). RERUN = nueva medida comparable.


## Formato 1080p25

| escenario | fuente | 0c | 1c | 2c | 3c | 4c |
|---|---|---|---|---|---|---|
| docker | RERUN | 30% | 37% | 45% | 61% | 89% |
| docker | oficial | 0% | 41% | 46% | 62% | 90% |
| local | RERUN | 29% | 36% | 44% | 60% | 90% |
| local | oficial | — | 37% | 46% | 62% | 91% |
| k8s | RERUN | 25% | 34% | 39% | 54% | 82% |
| k8s | oficial | 25% | 30% | 38% | 53% | 83% |

**4 cams (RERUN): docker=89% local=90% k8s=82% → K8s SIGUE más bajo que docker/local → puede ser real; revisar**

## Formato 1080p50

| escenario | fuente | 0c | 1c | 2c | 3c | 4c |
|---|---|---|---|---|---|---|
| docker | RERUN | 37% | 44% | 54% | 71% | 86% |
| docker | oficial | 0% | 45% | 54% | 72% | 86% |
| local | RERUN | 36% | 43% | 53% | 70% | 86% |
| local | oficial | — | 43% | 53% | 70% | 85% |
| k8s | RERUN | 33% | 38% | 48% | 62% | 81% |
| k8s | oficial | 30% | 36% | 46% | 62% | 81% |

**4 cams (RERUN): docker=86% local=86% k8s=81% → K8s SIGUE más bajo que docker/local → puede ser real; revisar**

## Formato 2160p25

| escenario | fuente | 0c | 1c | 2c | 3c | 4c |
|---|---|---|---|---|---|---|
| docker | RERUN | 41% | 52% | 65% | 80% | 92% |
| docker | oficial | 0% | 56% | 71% | 86% | 95% |
| local | RERUN | 39% | 50% | 63% | 79% | 92% |
| local | oficial | — | 50% | 63% | 79% | 92% |
| k8s | RERUN | 28% | 36% | 46% | 59% | 78% |
| k8s | oficial | 29% | 37% | 47% | 60% | 80% |

**4 cams (RERUN): docker=92% local=92% k8s=78% → K8s SIGUE más bajo que docker/local → puede ser real; revisar**

## Formato 2160p50

| escenario | fuente | 0c | 1c | 2c | 3c | 4c |
|---|---|---|---|---|---|---|
| docker | RERUN | 49% | 58% | 68% | 80% | 90% |
| docker | oficial | 0% | 57% | 67% | 78% | 88% |
| local | RERUN | 49% | 57% | 67% | 77% | 87% |
| local | oficial | — | 57% | 66% | 77% | 86% |
| k8s | RERUN | 40% | 44% | 51% | 60% | 71% |
| k8s | oficial | 40% | 44% | 51% | 60% | 71% |

**4 cams (RERUN): docker=90% local=87% k8s=71% → K8s SIGUE más bajo que docker/local → puede ser real; revisar**
