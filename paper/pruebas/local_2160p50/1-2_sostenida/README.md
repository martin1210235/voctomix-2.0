# Performance — sustained load

**Scenario:** Local (native) · **Format:** 2160p50 (3840×2160 @ 50 fps)
**Hardware:** Intel Core i9-10900X, 128 GB RAM, Ubuntu 22.04 (other applications closed).

## What is measured
CPU (%) and RAM (%) usage with 4 active cameras over 2 h.

## Result
Median CPU: **84.4%** · Median RAM: **10.7%** (2 h, 4 cameras).

## Files
`datos.csv` (raw data), `resumen.csv` (statistics), `datos.xlsx` (Excel). The output format
was verified with ffprobe (see `paper/pruebas/verificacion_formatos/`).
