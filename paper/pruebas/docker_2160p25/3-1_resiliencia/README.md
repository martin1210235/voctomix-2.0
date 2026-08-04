# Resiliencia — caída y recuperación de cámara

**Escenario:** Docker · **Formato:** 2160p25 (3840×2160 @ 25 fps)
**Hardware:** Intel Core i9-10900X, 128 GB RAM, Ubuntu 22.04 (aplicaciones cerradas).

## Qué se mide
Se fuerza la caída de una cámara y se mide el MTTR (detección + restablecimiento) sobre la salida del mix. 100 repeticiones.

Mecanismo de caída/recuperación: docker exec camN pkill -9 ffmpeg (restart policy del contenedor).

## Resultado
MTTR mediana: **1659.7 ms** (detección 76.35 ms + restablecimiento 1521.45 ms), n=100.

## Ficheros
`datos.csv` (datos crudos), `resumen.csv` (estadística), `datos.xlsx` (Excel). El formato de
la salida se verificó con ffprobe (ver `paper/pruebas/verificacion_formatos/`).
