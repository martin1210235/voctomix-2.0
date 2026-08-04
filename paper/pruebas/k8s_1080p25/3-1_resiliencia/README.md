# Resiliencia — caída y recuperación de cámara

**Escenario:** Kubernetes · **Formato:** 1080p25 (1920×1080 @ 25 fps)
**Hardware:** Intel Core i9-10900X, 128 GB RAM, Ubuntu 22.04 (aplicaciones cerradas).

## Qué se mide
Se fuerza la caída de una cámara y se mide el MTTR (detección + restablecimiento) sobre la salida del mix. 100 repeticiones.

Mecanismo de caída/recuperación: kubectl delete pod (el Deployment recrea el pod = self-healing).

## Resultado
MTTR mediana: **2078.45 ms** (detección 1077.65 ms + restablecimiento 1000.05 ms), n=100.

## Ficheros
`datos.csv` (datos crudos), `resumen.csv` (estadística), `datos.xlsx` (Excel). El formato de
la salida se verificó con ffprobe (ver `paper/pruebas/verificacion_formatos/`).
