# Rendimiento — carga sostenida de 24 h (estudio de memory-leak)

**Escenario:** Docker · **Formato:** 2160p50 (3840×2160 @ 50 fps)
**Hardware:** Intel Core i9-10900X, 128 GB RAM, Ubuntu 22.04 (aplicaciones cerradas).

## Qué se mide
Uso de CPU (%) y RAM (%) con 4 cámaras activas durante 24 h seguidas. Esta prueba es la versión larga de la sostenida de 2 h, ejecutada específicamente para descartar una fuga de memoria (memory-leak) en el escenario más exigente (Docker a 4K/50 fps).

## Resultado
CPU mediana: **82.1%** · RAM mediana: **17.9%** (24 h, 4 cámaras).

La RAM crece durante las ~2 primeras horas hasta estabilizarse en torno al 18% y se mantiene plana el resto de la prueba, sin crecimiento acumulativo. Por tanto no hay fuga de memoria: el aumento inicial es un llenado transitorio de buffers que satura y se mantiene constante.

## Ficheros
`datos.csv` (datos crudos), `resumen.csv` (estadística), `datos.xlsx` (Excel). El formato de
la salida se verificó con ffprobe (ver `paper/pruebas/verificacion_formatos/`).
La gráfica de la evolución de CPU y RAM está en `paper/pruebas/graficas/fig_docker_2160p50_sostenida24h.png` (y `.pdf`).
