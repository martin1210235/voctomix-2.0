# Performance — sustained load

**Scenario:** Kubernetes · **Format:** 1080p25 (1920×1080 @ 25 fps)
**Hardware:** Intel Core i9-10900X, 128 GB RAM, Ubuntu 22.04 (other applications closed).

## What is measured
CPU (%) and RAM (%) usage with 4 active cameras over 2 h.

## Result
Median CPU: **88.5%** · Median RAM: **10.4%** (2 h, 4 cameras).

## Files
`datos.csv` (raw data), `resumen.csv` (statistics), `datos.xlsx` (Excel). The output format
was verified with ffprobe (see `paper/pruebas/verificacion_formatos/`).
