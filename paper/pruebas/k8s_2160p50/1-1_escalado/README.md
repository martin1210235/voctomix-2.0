# Performance — camera scaling

**Scenario:** Kubernetes · **Format:** 2160p50 (3840×2160 @ 50 fps)
**Hardware:** Intel Core i9-10900X, 128 GB RAM, Ubuntu 22.04 (other applications closed).

## What is measured
CPU (%) and RAM (%) usage read from /proc (the same source as htop) while cameras 1→4 are activated in turn. Starts with 15 min at 0 cameras (baseline), then 15 min per camera.

## Result
| # cameras | Median CPU | Median RAM |
|---|---|---|
| 0 | 39.7% | 7.9% |
| 1 | 43.7% | 9.0% |
| 2 | 51.4% | 9.8% |
| 3 | 60.2% | 10.7% |
| 4 | 70.7% | 11.4% |

## Files
`datos.csv` (raw data), `resumen.csv` (statistics), `datos.xlsx` (Excel). The output format
was verified with ffprobe (see `paper/pruebas/verificacion_formatos/`).
