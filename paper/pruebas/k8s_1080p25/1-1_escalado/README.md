# Rendimiento — escalado de cámaras

**Escenario:** Kubernetes (k3s) · **Formato:** 1080p25 (1920×1080 @ 25 fps)
**Hardware:** Intel Core i9-10900X, 128 GB RAM, Ubuntu 22.04 (aplicaciones cerradas).

## Qué se mide
Uso de CPU (%) y RAM (%) leídos de /proc (misma fuente que htop) mientras se activan las cámaras 1→4. Empieza con 15 min a 0 cámaras (baseline) y luego 15 min por cada cámara.

## Resultado
| nº cámaras | CPU mediana | RAM mediana |
|---|---|---|
| 0 | 33.9% | 7.5% |
| 1 | 35.3% | 8.2% |
| 2 | 43.0% | 8.9% |
| 3 | 59.1% | 9.5% |
| 4 | 89.1% | 10.2% |

## Ficheros
`datos.csv` (datos crudos), `resumen.csv` (estadística), `datos.xlsx` (Excel). El formato de
la salida se verificó con ffprobe (ver `paper/pruebas/verificacion_formatos/`).
