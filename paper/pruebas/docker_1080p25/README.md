# Docker · 1080p25

Celda del escenario Docker, formato 1080p25 (1920×1080 @ 25 fps). Parte de la matriz de
pruebas (3 escenarios × 4 formatos × 5 análisis).

**Hardware:** Intel Core i9-10900X, 128 GB RAM, Ubuntu 22.04. PC con aplicaciones cerradas.
**Fecha:** 2026-07-25.

## Resultados (medianas; datos completos en cada subcarpeta)

| Análisis | n | Métrica | Mediana | P95 | Rango |
|---|---|---|---|---|---|
| 2.1 Latencia conmutación de cámara (corte) | 100/100 | ms | **293,0** | 296,1 | 285,7–297,2 |
| 2.2 Latencia conmutación composición fs↔sbs (corte) | 100/100 | ms | **296,3** | 297,9 | 283,0–299,5 |
| 3.1 Resiliencia — MTTR (caída+recuperación cámara) | 100/100 | ms | **1794** | 1837 | 1717–1838 |

Detalle de 3.1: detección mediana 758 ms + restablecimiento mediana 1000 ms.
Rendimiento (1.1 escalado y 1.2 sostenida): ver sus subcarpetas. Cero fallos.

## Estructura de entrega (por análisis)
Cada subcarpeta contiene: `README.md` (cómo se hizo), `datos.csv` (crudo), `resumen.csv`
(estadística), `datos.xlsx` (Excel), `run.log`, `capturas/`.

- `1-1_escalado/`
- `1-2_sostenida/`
- `2-1_lat_camara/`
- `2-2_lat_composicion/`
- `3-1_resiliencia/`
