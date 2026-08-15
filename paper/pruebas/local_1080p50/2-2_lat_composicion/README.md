# Latency — composite switching

**Scenario:** Local (native) · **Format:** 1080p50 (1920×1080 @ 50 fps)
**Hardware:** Intel Core i9-10900X, 128 GB RAM, Ubuntu 22.04 (other applications closed).

## What is measured
Real video latency when switching composite mode (fullscreen ↔ side-by-side) via a hard cut. 100 repetitions.

## Result
Median latency: **196.5 ms** (n=100).

## Files
`datos.csv` (raw data), `resumen.csv` (statistics), `datos.xlsx` (Excel). The output format
was verified with ffprobe (see `paper/pruebas/verificacion_formatos/`).
