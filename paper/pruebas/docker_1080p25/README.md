# Docker · 1080p25

Cell of the Docker scenario, 1080p25 format (1920×1080 @ 25 fps). Part of the test matrix
(3 scenarios × 4 formats × 5 analyses).

**Hardware:** Intel Core i9-10900X, 128 GB RAM, Ubuntu 22.04. PC con other applications closed.
**Date:** 2026-07-25.

## Results (medians; full data in each subfolder)

| Analysis | n | Metric | Median | P95 | Range |
|---|---|---|---|---|---|
| 2.1 Camera-switching latency (hard cut) | 100/100 | ms | **293,0** | 296,1 | 285,7–297,2 |
| 2.2 Composite-switching latency fs↔sbs (hard cut) | 100/100 | ms | **296,3** | 297,9 | 283,0–299,5 |
| 3.1 Resilience — MTTR (camera failure+recovery) | 100/100 | ms | **1794** | 1837 | 1717–1838 |

3.1 detail: median detection 758 ms + recovery mediana 1000 ms.
Performance (1.1 scaling and 1.2 sustained): see their subfolders. Zero failures.

## Delivery structure (per analysis)
Each subfolder contains: `README.md` (how it was done), `datos.csv` (raw), `resumen.csv`
(statistics), `datos.xlsx` (Excel), `run.log`, `capturas/`.

- `1-1_escalado/`
- `1-2_sostenida/`
- `2-1_lat_camara/`
- `2-2_lat_composicion/`
- `3-1_resiliencia/`
