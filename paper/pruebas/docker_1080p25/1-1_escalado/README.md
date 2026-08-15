# Performance — camera scaling

**Scenario:** Docker · **Format:** 1080p25 (1920×1080 @ 25 fps)
**Hardware:** Intel Core i9-10900X, 128 GB RAM, Ubuntu 22.04 (other applications closed).

## What is measured
CPU (%) and RAM (%) usage read from /proc (the same source as htop) while cameras 1→4 are activated in turn. Starts with 15 min at 0 cameras (baseline), then 15 min per camera.

## Result
| # cameras | Median CPU | Median RAM |
|---|---|---|
| 0 | 29.8% | 7.4% |
| 1 | 36.8% | 8.4% |
| 2 | 45.3% | 9.2% |
| 3 | 60.95% | 10.0% |
| 4 | 89.1% | 10.7% |

## Files
`datos.csv` (raw data), `resumen.csv` (statistics), `datos.xlsx` (Excel). The output format
was verified with ffprobe (see `paper/pruebas/verificacion_formatos/`).
