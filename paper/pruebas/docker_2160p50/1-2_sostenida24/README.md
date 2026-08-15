# Performance — 24 h sustained load (memory-leak study)

**Scenario:** Docker · **Format:** 2160p50 (3840×2160 @ 50 fps)
**Hardware:** Intel Core i9-10900X, 128 GB RAM, Ubuntu 22.04 (other applications closed).

## What is measured
CPU (%) and RAM (%) usage with 4 active cameras over 24 continuous hours. This test is the
long-run version of the 2 h sustained test, run specifically to rule out a memory leak in the
most demanding scenario (Docker at 4K/50 fps).

## Result
Median CPU: **82.1%** · Median RAM: **17.9%** (24 h, 4 cameras).

RAM grows over the first ~2 hours until it stabilizes around 18%, then stays flat for the rest
of the test with no cumulative growth. There is therefore no memory leak: the initial increase
is a transient buffer fill-up that saturates and then remains constant.

## Files
`datos.csv` (raw data), `resumen.csv` (statistics), `datos.xlsx` (Excel). The output format
was verified with ffprobe (see `paper/pruebas/verificacion_formatos/`).
The CPU/RAM evolution chart is at `paper/pruebas/graficas/fig_docker_2160p50_sostenida24h.png` (and `.pdf`).
