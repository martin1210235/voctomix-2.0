# Sostenida 24 h — Local (nativo) · 1080p25

**Escenario:** Local (nativo) · **Formato:** 1080p25 (1920×1080 @ 25 fps) · **Duración:** 24 h
**Hardware:** Intel Core i9-10900X, 128 GB RAM, Ubuntu 22.04 (aplicaciones cerradas).

## Qué se mide
Uso de CPU (%) y RAM (%) del sistema (leídos de /proc, misma fuente que htop) con 4 cámaras
activas durante 24 h seguidas. Análoga a la sostenida de 24 h de Docker 2160p50, aquí para
estudiar la evolución de la RAM en el escenario nativo a largo plazo (memory-leak).

## Resultado (mediana / tendencia)
CPU mediana: **88.5%** · RAM: 10.4% → 10.4% → 10.5% (inicio→mitad→fin).
Tendencia de RAM: **PLANA (sin leak, esperado en Local)**. Muestras: 16962 (~24.0 h), 100% del tiempo con 4 cámaras.

## Ficheros
`datos.csv` (crudo, escritura incremental), `resumen.csv` (estadística), `datos.xlsx` (Excel).
