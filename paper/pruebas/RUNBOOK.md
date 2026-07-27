# RUNBOOK — Cómo ejecutar cada prueba (claridad absoluta)

Guía operativa exacta: qué fichero se usa, qué hay que modificar y qué comando lanzar en cada prueba. Todo verificado contra el stack real el 2026-07-24.

---

## 1. INVENTARIO — todos los ficheros que intervienen y su papel

### Herramientas (en `experiments/comprehensive/`)
| Fichero | Papel | Se ejecuta a mano |
|---|---|---|
| `set_format.sh` | **Fuente única de verdad del formato.** Escribe el `videocaps` de voctocore + el `.env` de las cámaras (WIDTH/HEIGHT/FRAMERATE) + `SAVE_LOGS=true`. | Sí, antes de cada celda |
| `run_performance.py` | Driver Análisis 1: levanta el stack, activa cámaras (escalado) o mantiene 4 (sostenida), y parsea a CSV. | Sí (1.1 y 1.2) |
| `parse_performance.py` | Convierte una sesión de telemetría en `datos.csv`/`resumen.csv`/`datos.xlsx` (lo llama `run_performance.py`). | Automático |
| `measure_latency_camera.py` | Análisis 2.1: latencia de conmutación de cámara (corte). | Sí (2.1) |
| `measure_latency_composite.py` | Análisis 2.2: latencia de conmutación de composición fs↔sbs (corte). | Sí (2.2) |
| `measure_camera_recovery.py` | Análisis 3.1: caída de cámara (crash) y tiempo de recuperación. | Sí (3.1) |
| `lib_common.py` | Estadística + escritura CSV/XLSX (compartida). | Nunca directo |
| `lib_video.py` | Lector de la salida del mix + clasificación de color (compartida). | Nunca directo |

### Configuración Docker (en la raíz del repo)
| Fichero | Papel |
|---|---|
| `docker-compose.yml` | Stack base (10 servicios). Ya con los conflictos de merge resueltos. NO se toca. |
| `docker-compose.experiment.yml` | **Override REALISTA:** 4 cámaras = máster BBB 4K local, cada una con marcador de color (cam1=rojo, cam2=verde, cam3=azul, cam4=amarillo) + offset distinto. **Se usa en Análisis 1 (rendimiento) y 3 (resiliencia).** |
| `docker-compose.latency.yml` | **Override COLOR SÓLIDO:** 4 cámaras = color pleno (cam1=rojo, cam2=verde, cam3=azul, cam4=amarillo). **Se usa en Análisis 2 (latencia)** para detección de conmutación infalible. |
| `.env` | Lo genera `set_format.sh`. Contiene WIDTH/HEIGHT/FRAMERATE/AUDIORATE/SAVE_LOGS. |
| `voctocore/default-config.ini` | Config de voctocore; `set_format.sh` reescribe su línea `videocaps`. |
| `voctocore/default-config.ini.orig` | Copia pristine (1080p25) desde la que `set_format.sh` regenera. NO borrar. |
| `videos/bbb_sunflower_2160p_60fps_normal.mp4` | Máster de vídeo 4K CC-BY (Big Buck Bunny, Blender). Fuente de las cámaras realistas. NO borrar. |

### Salidas
- Telemetría cruda: `sessions/sessionN.jsonl` (autoincremental; solo si `SAVE_LOGS=true`).
- Resultados por prueba: subcarpeta en `paper/pruebas/` con `datos.csv` + `resumen.csv` + `datos.xlsx` + `README.md` + `capturas/`.

---

## 2. CONCEPTOS CLAVE VERIFICADOS (para no equivocarse)

- **Puerto de medida del vídeo = 11000** (mix crudo). El 15000 NO (es programa tras stream-blanker, sale en negro).
- **Conmutar cámara:** comando `set_video_a <cam>` (corte). **Conmutar composición:** `cut <modo>(A,B)` — OJO: `set_composite_mode` NO funciona, usar `cut`.
- **Caída de cámara realista:** `docker exec camN pkill -9 ffmpeg` (crash del proceso → auto-restart de Docker). NO `docker kill camN` (eso la deja parada sin reiniciar).
- **Colorimetría:** las cámaras deben emitir bt709 (ya está en los overrides). Sin ello voctocore las rechaza.
- **Latencia observada (~280-310 ms a 1080p25):** es latencia real de la tubería de voctocore, no artefacto (medida idéntica en 11000 y 12000).

---

## 3. PROCEDIMIENTO POR CELDA (escenario × formato)

> **Antes de empezar CUALQUIER celda:** cerrar Teams, navegador y demás. Dejar solo la terminal. Captura del PC limpio (`capturas/01_pc_limpio.png`). Al empezar un bloque nuevo (Docker/Local/K8s) avisar a los tutores.

### Paso 0 — Fijar el formato (siempre)
```bash
cd /home/sonda/Documentos/voctomix
experiments/comprehensive/set_format.sh <1080p25|1080p50|2160p25|2160p50>
```

### Análisis 1.1 — Escalado de cámaras (rendimiento)
Config: **experiment (BBB)**. Duración real: 15 min/paso.
```bash
python3 experiments/comprehensive/run_performance.py escalado \
    paper/pruebas/<NN>_docker_1080p25_1-1_escalado --step-min 15
```
Genera CSV con CPU%/RAM% etiquetado por nº de cámaras (0,1,2,3,4). El driver levanta y baja el stack solo.

### Análisis 1.2 — Carga sostenida (rendimiento)
Config: **experiment (BBB)**. Duración real: 120 min.
```bash
python3 experiments/comprehensive/run_performance.py sostenida \
    paper/pruebas/<NN>_docker_1080p25_1-2_sostenida --duration-min 120
```

### Análisis 2.1 y 2.2 — Latencia
Config: **latency (color sólido)**. Hay que levantar el stack a mano primero:
```bash
docker compose -f docker-compose.yml -f docker-compose.latency.yml up -d
# esperar ~40s a que las 4 cámaras estén 'healthy'
bash experiments/comprehensive/show_gui.sh          # monitor del mix en pantalla
python3 experiments/comprehensive/measure_latency_camera.py \
    paper/pruebas/<NN>_docker_1080p25_2-1_lat_camara --n 100
python3 experiments/comprehensive/measure_latency_composite.py \
    paper/pruebas/<NN>_docker_1080p25_2-2_lat_composicion --n 100
docker compose -f docker-compose.yml -f docker-compose.latency.yml down
```

### Análisis 3.1 — Resiliencia
Config: **experiment (BBB)**. Levantar a mano:
```bash
docker compose -f docker-compose.yml -f docker-compose.experiment.yml up -d
# esperar ~40s a que las 4 cámaras estén 'healthy'
bash experiments/comprehensive/show_gui.sh          # monitor del mix en pantalla
python3 experiments/comprehensive/measure_camera_recovery.py \
    paper/pruebas/<NN>_docker_1080p25_3-1_resiliencia --n 100
docker compose -f docker-compose.yml -f docker-compose.experiment.yml down
```

### Paso final de cada prueba
- Rellenar el `README.md` de la subcarpeta (cómo se hizo, comando exacto, formato, estado del PC).
- Guardar capturas de la ejecución en `capturas/`.
- Verificar que `datos.csv` y `resumen.csv` tienen datos coherentes.

---

## 4. VER LA GUI EN DIRECTO (OBLIGATORIO en cada prueba)
Con el stack levantado, mostrar el monitor del mix fijado encima:
```bash
bash experiments/comprehensive/show_gui.sh
```
Abre el mix (puerto 11000) con gst `xvimagesink` (X11 puro, sin OpenGL → funciona sobre
AnyDesk/remoto) y lo eleva + fija "siempre encima" con Wnck. Se ve la salida compositada en
directo (conmutaciones de cámara, cambios de composición, caídas/recuperaciones). Volver a
ejecutarlo en cualquier momento lo trae al frente. El driver `run_performance.py` ya lo lanza
solo tras arrancar el stack (para 1.1 y 1.2). Para 2.x y 3.1, se ejecuta a mano tras el `up -d`.
Cerrar al terminar: `pkill -f "gst-launch.*port=11000"`.
> Nota: `ffplay` NO sirve aquí (falla por GLX sobre AnyDesk). El visor válido es el de `show_gui.sh`.

---

## 5. ORDEN DE EJECUCIÓN (resumen; detalle en PLAN_PRUEBAS_DEFINITIVO.md §6-BIS)
Docker (los 4 formatos, con smoke test antes de 2160p50) → Local (4 formatos) → Kubernetes con kind/k3s (4 formatos). 5 análisis por celda. Empezar por la **piloto Docker+1080p25** y enviarla a los tutores antes de escalar.

---

## 6. REFERENCIA RÁPIDA DE VALORES (validación en runs cortos 1080p25, NO definitivos)
Sirven solo para saber que "un número tiene sentido" al ejecutar:
- Rendimiento escalado: CPU ~39% (1 cam) → ~67% (4 cams); RAM ~8.7% → ~10.6%.
- Latencia cámara (2.1): ~275-315 ms.
- Latencia composición (2.2): ~278 ms.
- Resiliencia (3.1): MTTR ~1.8 s (detección ~0.8 s + restablecimiento ~1.0 s).

Si un valor se sale mucho de esto sin explicación (p. ej. formato más pesado), revisar antes de dar la prueba por buena.
