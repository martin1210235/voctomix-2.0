# Resiliencia — caída y recuperación de cámara

**Escenario:** Kubernetes (k3s) · **Formato:** 2160p50 (3840×2160 @ 50 fps)
**Hardware:** Intel Core i9-10900X, 128 GB RAM, Ubuntu 22.04 (aplicaciones cerradas).

## Qué se mide
Se fuerza la caída de una cámara y se mide el MTTR (detección + restablecimiento) sobre la salida del mix. 100 repeticiones.

Mecanismo de caída/recuperación: kubectl delete pod (el Deployment recrea el pod = self-healing).

## Resultado
MTTR mediana: **1956.7 ms** (detección 96.0 ms + restablecimiento 1859.2 ms), n=100.

## Ficheros
`datos.csv` (datos crudos), `resumen.csv` (estadística), `datos.xlsx` (Excel). El formato de
la salida se verificó con ffprobe (ver `paper/pruebas/verificacion_formatos/`).
