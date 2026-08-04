# Latencia — conmutación de cámara

**Escenario:** Kubernetes · **Formato:** 1080p50 (1920×1080 @ 50 fps)
**Hardware:** Intel Core i9-10900X, 128 GB RAM, Ubuntu 22.04 (aplicaciones cerradas).

## Qué se mide
Latencia de vídeo real (glass-to-glass) al conmutar de cámara en corte, detectada por color en la salida del mix. 100 repeticiones.

## Resultado
Latencia mediana: **193.25 ms** (n=100).

## Ficheros
`datos.csv` (datos crudos), `resumen.csv` (estadística), `datos.xlsx` (Excel). El formato de
la salida se verificó con ffprobe (ver `paper/pruebas/verificacion_formatos/`).
