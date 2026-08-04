# Latencia — conmutación de composición

**Escenario:** Kubernetes (k3s) · **Formato:** 2160p25 (3840×2160 @ 25 fps)
**Hardware:** Intel Core i9-10900X, 128 GB RAM, Ubuntu 22.04 (aplicaciones cerradas).

## Qué se mide
Latencia de vídeo real al cambiar de composición (pantalla completa ↔ side-by-side) en corte. 100 repeticiones.

## Resultado
Latencia mediana: **219.1 ms** (n=100).

## Ficheros
`datos.csv` (datos crudos), `resumen.csv` (estadística), `datos.xlsx` (Excel). El formato de
la salida se verificó con ffprobe (ver `paper/pruebas/verificacion_formatos/`).
