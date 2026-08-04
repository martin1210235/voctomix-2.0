# Rendimiento — escalado de cámaras

**Escenario:** Local (nativo) · **Formato:** 1080p25 (1920×1080 @ 25 fps)
**Hardware:** Intel Core i9-10900X, 128 GB RAM, Ubuntu 22.04 (aplicaciones cerradas).

## Qué se mide
Uso de CPU (%) y RAM (%) leídos de /proc (misma fuente que htop) mientras se activan las cámaras 1→4. Empieza con 15 min a 0 cámaras (baseline) y luego 15 min por cada cámara.

## Resultado
| nº cámaras | CPU mediana | RAM mediana |
|---|---|---|
| 0 | 29.0% | 7.2% |
| 1 | 35.9% | 7.9% |
| 2 | 44.5% | 8.6% |
| 3 | 59.5% | 9.2% |
| 4 | 89.6% | 10.0% |

## Ficheros
`datos.csv` (datos crudos), `resumen.csv` (estadística), `datos.xlsx` (Excel). El formato de
la salida se verificó con ffprobe (ver `paper/pruebas/verificacion_formatos/`).
