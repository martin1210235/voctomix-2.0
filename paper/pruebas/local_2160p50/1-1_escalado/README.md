# Performance — camera scaling

**Scenario:** Local (native) · **Format:** 2160p50 (3840×2160 @ 50 fps)
**Hardware:** Intel Core i9-10900X, 128 GB RAM, Ubuntu 22.04 (other applications closed).

## What is measured
CPU (%) and RAM (%) usage read from /proc (the same source as htop) while cameras 1→4 are activated in turn. Starts with 15 min at 0 cameras (baseline), then 15 min per camera.

## Result
| # cameras | Median CPU | Median RAM |
|---|---|---|
| 0 | 48.7% | 8.3% |
| 1 | 56.9% | 9.2% |
| 2 | 67.0% | 10.0% |
| 3 | 77.4% | 10.8% |
| 4 | 87.0% | 11.6% |

## Files
`datos.csv` (raw data), `resumen.csv` (statistics), `datos.xlsx` (Excel). The output format
was verified with ffprobe (see `paper/pruebas/verificacion_formatos/`).
