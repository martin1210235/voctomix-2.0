# Rendimiento — escalado de cámaras

**Escenario:** Docker · **Formato:** 2160p50 (3840×2160 @ 50 fps)
**Hardware:** Intel Core i9-10900X, 128 GB RAM, Ubuntu 22.04 (aplicaciones cerradas).

## Qué se mide
Uso de CPU (%) y RAM (%) leídos de /proc (misma fuente que htop) mientras se activan las cámaras 1→4. Empieza con 15 min a 0 cámaras (baseline) y luego 15 min por cada cámara.

## Resultado
| nº cámaras | CPU mediana | RAM mediana |
|---|---|---|
| 0 | 48.6% | 10.1% |
| 1 | 57.5% | 12.8% |
| 2 | 68.2% | 14.9% |
| 3 | 79.5% | 16.8% |
| 4 | 89.7% | 17.8% |

## Ficheros
`datos.csv` (datos crudos), `resumen.csv` (estadística), `datos.xlsx` (Excel). El formato de
la salida se verificó con ffprobe (ver `paper/pruebas/verificacion_formatos/`).
