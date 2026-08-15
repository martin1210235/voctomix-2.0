# Performance — camera scaling

**Scenario:** Local (native) · **Format:** 1080p25 (1920×1080 @ 25 fps)
**Hardware:** Intel Core i9-10900X, 128 GB RAM, Ubuntu 22.04 (other applications closed).

## What is measured
CPU (%) and RAM (%) usage read from /proc (the same source as htop) while cameras 1→4 are activated in turn. Starts with 15 min at 0 cameras (baseline), then 15 min per camera.

## Result
| # cameras | Median CPU | Median RAM |
|---|---|---|
| 0 | 29.0% | 7.2% |
| 1 | 35.9% | 7.9% |
| 2 | 44.5% | 8.6% |
| 3 | 59.5% | 9.2% |
| 4 | 89.6% | 10.0% |

## Files
`datos.csv` (raw data), `resumen.csv` (statistics), `datos.xlsx` (Excel). The output format
was verified with ffprobe (see `paper/pruebas/verificacion_formatos/`).
