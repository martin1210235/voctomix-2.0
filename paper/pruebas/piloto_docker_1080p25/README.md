# PILOTO — Docker · 1080p25

Prueba piloto para validar la metodología y el formato de entrega antes de escalar a las
12 celdas (3 escenarios × 4 formatos). Escenario Docker, formato 1080p25.

**Hardware:** Intel Core i9-10900X, 128 GB RAM, Ubuntu 22.04. PC con aplicaciones cerradas.
**Fecha:** 2026-07-25.

## Resultados de la tanda rápida (latencia + resiliencia)

| Análisis | n | Métrica | Mediana | P95 | Rango |
|---|---|---|---|---|---|
| 2.1 Latencia conmutación de cámara (corte) | 100/100 | ms | **293,0** | 296,1 | 285,7–297,2 |
| 2.2 Latencia conmutación composición fs↔sbs (corte) | 100/100 | ms | **296,3** | 297,9 | 283,0–299,5 |
| 3.1 Resiliencia — MTTR (caída+recuperación cámara) | 100/100 | ms | **1794** | 1837 | 1717–1838 |

Detalle de 3.1: detección mediana 758 ms + restablecimiento mediana 1000 ms.
Cero fallos en las tres pruebas.

## Pendiente en esta celda (rendimiento, tanda larga)
- 1.1 Escalado de cámaras (1→2→3→4, 15 min/paso, ~60 min).
- 1.2 Carga sostenida 4 cámaras (2 horas).

## Estructura de entrega (por análisis)
Cada subcarpeta contiene: `README.md` (cómo se hizo), `datos.csv` (crudo), `resumen.csv`
(estadística), `datos.xlsx` (Excel), `run.log`, `capturas/`.

- `2-1_lat_camara/`
- `2-2_lat_composicion/`
- `3-1_resiliencia/`
- (pendientes) `1-1_escalado/`, `1-2_sostenida/`
