# Rendimiento — escalado de cámaras

**Escenario:** Docker · **Formato:** 2160p25 (3840×2160 @ 25 fps)
**Hardware:** Intel Core i9-10900X, 128 GB RAM, Ubuntu 22.04 (aplicaciones cerradas).

## Qué se mide
Uso de CPU (%) y RAM (%) leídos de /proc (misma fuente que htop) mientras se activan las cámaras 1→4. Empieza con 15 min a 0 cámaras (baseline) y luego 15 min por cada cámara.

## Resultado
| nº cámaras | CPU mediana | RAM mediana |
|---|---|---|
| 0 | 41.2% | 10.2% |
| 1 | 51.7% | 12.9% |
| 2 | 64.9% | 14.7% |
| 3 | 80.0% | 16.8% |
| 4 | 92.5% | 18.2% |

## Ficheros
`datos.csv` (datos crudos), `resumen.csv` (estadística), `datos.xlsx` (Excel). El formato de
la salida se verificó con ffprobe (ver `paper/pruebas/verificacion_formatos/`).
