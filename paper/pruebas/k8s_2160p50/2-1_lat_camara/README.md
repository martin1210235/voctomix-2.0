# Latency — camera switching

**Scenario:** Kubernetes · **Format:** 2160p50 (3840×2160 @ 50 fps)
**Hardware:** Intel Core i9-10900X, 128 GB RAM, Ubuntu 22.04 (other applications closed).

## What is measured
Real (glass-to-glass) video latency when switching cameras via a hard cut, detected by colour in the mix output. 100 repetitions.

## Result
Median latency: **116.25 ms** (n=100).

## Files
`datos.csv` (raw data), `resumen.csv` (statistics), `datos.xlsx` (Excel). The output format
was verified with ffprobe (see `paper/pruebas/verificacion_formatos/`).
