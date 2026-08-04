# Rendimiento — carga sostenida

**Escenario:** Docker · **Formato:** 2160p25 (3840×2160 @ 25 fps)
**Hardware:** Intel Core i9-10900X, 128 GB RAM, Ubuntu 22.04 (aplicaciones cerradas).

## Qué se mide
Uso de CPU (%) y RAM (%) con 4 cámaras activas durante 2 h.

## Resultado
CPU mediana: **94.4%** · RAM mediana: **13.8%** (2 h, 4 cámaras).

## Ficheros
`datos.csv` (datos crudos), `resumen.csv` (estadística), `datos.xlsx` (Excel). El formato de
la salida se verificó con ffprobe (ver `paper/pruebas/verificacion_formatos/`).
