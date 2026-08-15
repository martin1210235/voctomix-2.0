# Resilience — camera failure and recovery

**Scenario:** Kubernetes · **Format:** 1080p50 (1920×1080 @ 50 fps)
**Hardware:** Intel Core i9-10900X, 128 GB RAM, Ubuntu 22.04 (other applications closed).

## What is measured
A camera failure is forced and the MTTR (detection + recovery) is measured on the mix output. 100 repetitions.

Failure/recovery mechanism: kubectl delete pod (the Deployment recreates the pod = self-healing).

## Result
Median MTTR: **897.6 ms** (detection 827.1 ms + recovery 90.25 ms), n=100.

## Files
`datos.csv` (raw data), `resumen.csv` (statistics), `datos.xlsx` (Excel). The output format
was verified with ffprobe (see `paper/pruebas/verificacion_formatos/`).
