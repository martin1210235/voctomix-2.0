# Resiliencia — caída y recuperación de cámara

**Escenario:** Kubernetes (k3s) · **Formato:** 1080p50 (1920×1080 @ 50 fps)
**Hardware:** Intel Core i9-10900X, 128 GB RAM, Ubuntu 22.04 (aplicaciones cerradas).

## Qué se mide
Se fuerza la caída de una cámara y se mide el MTTR (detección + restablecimiento) sobre la salida del mix. 100 repeticiones.

Mecanismo de caída/recuperación: kubectl delete pod (el Deployment recrea el pod = self-healing).

## Resultado
MTTR mediana: **897.6 ms** (detección 827.1 ms + restablecimiento 90.2 ms), n=100.

## Ficheros
`datos.csv` (datos crudos), `resumen.csv` (estadística), `datos.xlsx` (Excel). El formato de
la salida se verificó con ffprobe (ver `paper/pruebas/verificacion_formatos/`).
