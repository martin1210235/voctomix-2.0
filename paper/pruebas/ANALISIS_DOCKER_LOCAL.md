# Análisis riguroso Docker vs Local (2026-07-28)

Comparación de sentido físico de los resultados de los escenarios Docker y Local (los 4
formatos). Sirve de base para la discusión del paper y para decidir qué repetir.

## Coherente (no requiere acción)

- **RAM escalado**: sube con la resolución (1080p ~6-9 % → 4K ~9-16 %) y con el nº de cámaras.
  **Docker > Local** (4K: 16 % vs 10 %) = sobrecarga de memoria de los contenedores. Coherente.
- **Latencia 2.1 (conmutación de cámara)**: depende del **framerate**, no de la resolución.
  25 fps ≈ 293-329 ms, 50 fps ≈ 176-204 ms (~mitad, por el periodo de frame 40 vs 20 ms).
  2160p25 ≈ 1080p25 y 2160p50 ≈ 1080p50. Coherente.
- **Resiliencia MTTR**: total ~1,2-1,9 s, estable, Docker ≈ Local. El reparto detección/
  restablecimiento varía con la resolución de forma explicable (a 4K los buffers drenan más
  rápido → detección baja, restablecimiento más lento). Coherente.

## Requiere revisión (ver pruebas_pendientes_paper)

### 1. Incongruencia CPU a 4 cámaras
| CPU 4 cams | 1080p25 | 1080p50 | 2160p25 | 2160p50 |
|---|---|---|---|---|
| Docker | 84 % | 82 % | 93 % | 86 % |
| Local  | 85 % | 81 % | 89 % | 85 % |

A 1-2 cámaras el orden es correcto (50 fps > 25 fps, 4K > 1080p). A **4 cámaras** 50 fps sale
≤ 25 fps y 2160p50 < 2160p25. Hipótesis (se repite idéntico en Docker Y Local): **saturación +
descarte de frames** al llegar la máquina a ~90-93 %. Sería hallazgo real (techo de HW), no bug.
**Acción**: confirmar con `ffprobe` que 2160p50 corre de verdad a 3840×2160@50 en Docker/Local.
En K8s ya se verifica por celda; si el K8s 4K50 muestra la misma anomalía → confirma saturación.

### 2. Fuga de RAM en la sostenida — Docker, solo a 4K
| RAM (10 %→50 %→90 % del run 2h) | |
|---|---|
| docker_2160p50 | 12,0 → 14,9 → 16,0 % (sube continuo) |
| local_2160p50 | 10,0 → 10,0 → 10,0 % (plano) |
| docker_1080p25 | 8,9 → 9,0 → 9,0 % (plano) |

**Docker fuga RAM continua SOLO a 4K; Local nunca.** Coincide con lo que observó Alberto.
**Acción**: caracterizar con la sostenida de 24 h en Docker 4K; confirmar que no es artefacto.

### 3. Outlier de latencia 2.2 (composición) a 2160p50
docker_2160p50 = 334 ms, local = 243 ms (esperado ~200 a 50 fps). Rompe el patrón del framerate
y Docker ≠ Local. **Acción**: repetir esa celda concreta (barato, ~5 min/celda).

## Veredicto
Los datos tienen sentido físico salvo la incongruencia de CPU (probable saturación real, a
confirmar con ffprobe) y el outlier de latencia 2.2@2160p50 (repetir). No hay que repetir todo:
verificar formatos + rehacer los escalados (que ya tocaba por el baseline de 0 cámaras) + esa
celda de latencia.
