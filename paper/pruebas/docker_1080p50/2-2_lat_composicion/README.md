# Latencia — conmutación de composición

**Escenario:** Docker · **Formato:** 1080p50 (1920×1080 @ 50 fps)
**Hardware:** Intel Core i9-10900X, 128 GB RAM, Ubuntu 22.04 (aplicaciones cerradas).

## Qué se mide
Latencia de vídeo real al cambiar de composición (pantalla completa ↔ side-by-side) en corte. 100 repeticiones.

## Resultado
Latencia mediana: **196.6 ms** (n=100).

## Ficheros
`datos.csv` (datos crudos), `resumen.csv` (estadística), `datos.xlsx` (Excel). El formato de
la salida se verificó con ffprobe (ver `paper/pruebas/verificacion_formatos/`).
