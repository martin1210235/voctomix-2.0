# Performance — camera scaling

**Scenario:** Kubernetes · **Format:** 1080p25 (1920×1080 @ 25 fps)
**Hardware:** Intel Core i9-10900X, 128 GB RAM, Ubuntu 22.04 (other applications closed).

## What is measured
CPU (%) and RAM (%) usage read from /proc (the same source as htop) while cameras 1→4 are activated in turn. Starts with 15 min at 0 cameras (baseline), then 15 min per camera.

## Result
| # cameras | Median CPU | Median RAM |
|---|---|---|
| 0 | 24.9% | 7.0% |
| 1 | 34.3% | 7.7% |
| 2 | 39.2% | 8.3% |
| 3 | 53.5% | 9.0% |
| 4 | 81.5% | 9.7% |

## Files
`datos.csv` (raw data), `resumen.csv` (statistics), `datos.xlsx` (Excel). The output format
was verified with ffprobe (see `paper/pruebas/verificacion_formatos/`).
