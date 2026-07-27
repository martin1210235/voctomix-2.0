# Resumen de mis pruebas — Escenario DOCKER

En este documento explico las pruebas que he hecho para el escenario Docker: qué he
medido en cada una, cómo he cambiado los parámetros entre mediciones, y qué ficheros y
scripts he usado en cada prueba (con la ruta completa para que podáis abrirlos y verlos).

**Hardware:** Intel Core i9-10900X (10C/20T), 128 GB RAM, Ubuntu 22.04.
**Vídeo fuente:** Big Buck Bunny 4K 60fps (licencia Creative Commons BY, Blender). Uso el
mismo máster para todos los formatos (nativo en 4K, reescalado a 1080p), así que no hay
*upscaling*.
**Estado:** las 20 pruebas de Docker (4 formatos × 5 pruebas) están hechas, con datos y 0 fallos.

---

## 1. Cómo he diseñado las pruebas
He montado una matriz de **1 escenario (Docker) × 4 formatos × 5 pruebas = 20 mediciones**.

- **Los 4 formatos** son combinación de resolución × framerate: **1080p25, 1080p50, 2160p25, 2160p50**.
- **Las 5 pruebas** que hago en cada formato:
  1. **Rendimiento – escalado:** mido CPU% y RAM% activando las cámaras 1→2→3→4 (una cada 15 min).
  2. **Rendimiento – sostenida:** mido CPU% y RAM% con las 4 cámaras a la vez durante 2 h.
  3. **Latencia – conmutación de cámara** (corte directo), 100 veces.
  4. **Latencia – conmutación de composición** (pantalla completa ↔ side-by-side), 100 veces.
  5. **Resiliencia:** fuerzo la caída de una cámara y mido el tiempo de recuperación, 100 veces.

---

## 2. Cómo cambio los parámetros entre mediciones

**Para cambiar el formato de vídeo** (resolución + framerate) uso un único script que lo deja
todo coherente:
- `/home/sonda/Documentos/voctomix/experiments/comprehensive/set_format.sh`
  → reescribe la resolución y el framerate en la configuración de voctocore
  (`/home/sonda/Documentos/voctomix/voctocore/default-config.ini`, tanto el mix como las
  *previews*) y en el fichero `/home/sonda/Documentos/voctomix/.env` que usan las cámaras.
  *(Un detalle importante que descubrí: el mix y las previews tienen que ir al mismo framerate;
  si no, a 50fps voctocore no puede enlazar su tubería de vídeo y se cae.)*

**Para cambiar el contenido de las cámaras** uso dos configuraciones distintas según la prueba:
- **Vídeo real (Big Buck Bunny) con un marcador de color por cámara** → en rendimiento y
  resiliencia, porque ahí importa el coste real de decodificar vídeo.
- **Color sólido** (cam1=rojo, cam2=verde, cam3=azul, cam4=amarillo) → en latencia, porque la
  latencia de conmutación no depende del contenido y el color me deja detectar el instante
  exacto del cambio sin ambigüedad.

**Para cambiar el número de cámaras activas** (en la prueba de escalado) arranco los
contenedores de cámara de uno en uno cada 15 minutos.

---

## 3. Qué hago en cada prueba y qué ficheros uso

> Nota: todos los scripts están en la carpeta
> `/home/sonda/Documentos/voctomix/experiments/comprehensive/` y los datos en
> `/home/sonda/Documentos/voctomix/paper/pruebas/`.

### Prueba 1.1 — Rendimiento (escalado de cámaras)
**Qué mido:** CPU% y RAM% del equipo según voy activando 1, 2, 3 y 4 cámaras (una cada 15 min).
**Cómo lo hago:** la telemetría lee el uso del sistema y voy arrancando las cámaras; luego
convierto esa telemetría en tablas.
**Ficheros usados:**
- `/home/sonda/Documentos/voctomix/experiments/comprehensive/run_performance.py` — arranca el
  stack, activa las cámaras de una en una con su tiempo y coordina la medición.
- `/home/sonda/Documentos/voctomix/experiments/comprehensive/parse_performance.py` — convierte
  la telemetría en `datos.csv` / `resumen.csv` / `datos.xlsx`, etiquetando cada muestra por nº de cámaras.
- `/home/sonda/Documentos/voctomix/docker-compose.experiment.yml` — configuración de cámaras con
  vídeo real (Big Buck Bunny) y marcador de color.
- `/home/sonda/Documentos/voctomix/experiments/comprehensive/set_format.sh` — fija el formato antes de la prueba.

### Prueba 1.2 — Rendimiento (carga sostenida)
**Qué mido:** CPU% y RAM% con las 4 cámaras a la vez durante 2 horas (para ver si hay degradación).
**Cómo lo hago:** igual que la anterior pero con las 4 cámaras fijas 2 h.
**Ficheros usados:**
- `/home/sonda/Documentos/voctomix/experiments/comprehensive/run_performance.py` — mismo script, en modo "sostenida".
- `/home/sonda/Documentos/voctomix/experiments/comprehensive/parse_performance.py` — genera las tablas de resultados.
- `/home/sonda/Documentos/voctomix/docker-compose.experiment.yml` — cámaras con vídeo real.
- `/home/sonda/Documentos/voctomix/experiments/comprehensive/set_format.sh` — fija el formato.

### Prueba 2.1 — Latencia de conmutación de cámara
**Qué mido:** los milisegundos que tarda en verse el cambio al conmutar de una cámara a otra (corte directo).
**Cómo lo hago:** envío la orden de cambio por el puerto de control y detecto, en la salida del
mix, el primer fotograma que ya muestra el color de la cámara destino.
**Ficheros usados:**
- `/home/sonda/Documentos/voctomix/experiments/comprehensive/measure_latency_camera.py` — envía las
  100 conmutaciones y mide la latencia de cada una.
- `/home/sonda/Documentos/voctomix/experiments/comprehensive/lib_video.py` — lee la salida del mix y
  clasifica el color de la esquina (para saber qué cámara se está viendo).
- `/home/sonda/Documentos/voctomix/docker-compose.latency.yml` — cámaras de color sólido (rojo/verde/azul/amarillo).
- `/home/sonda/Documentos/voctomix/experiments/comprehensive/set_format.sh` — fija el formato.

### Prueba 2.2 — Latencia de conmutación de composición
**Qué mido:** los milisegundos que tarda en verse el cambio de modo de composición
(pantalla completa ↔ side-by-side).
**Cómo lo hago:** ordeno el cambio de composición y detecto en la salida del mix cuándo aparece
el nuevo layout (mirando el color de la zona centro-derecha).
**Ficheros usados:**
- `/home/sonda/Documentos/voctomix/experiments/comprehensive/measure_latency_composite.py` — hace las
  100 conmutaciones de composición y mide la latencia.
- `/home/sonda/Documentos/voctomix/experiments/comprehensive/lib_video.py` — lee la salida del mix y detecta el cambio de layout.
- `/home/sonda/Documentos/voctomix/docker-compose.latency.yml` — cámaras de color sólido.
- `/home/sonda/Documentos/voctomix/experiments/comprehensive/set_format.sh` — fija el formato.

### Prueba 3.1 — Resiliencia (caída y recuperación de cámara)
**Qué mido:** el tiempo que tarda el sistema en recuperar el feed de una cámara tras caerse (MTTR).
**Cómo lo hago:** simulo la caída matando el proceso de la cámara dentro del contenedor; Docker la
reinicia automáticamente y mido hasta que el feed vuelve a verse. Lo repito 100 veces.
**Ficheros usados:**
- `/home/sonda/Documentos/voctomix/experiments/comprehensive/measure_camera_recovery.py` — provoca las
  100 caídas y mide detección + recuperación (MTTR).
- `/home/sonda/Documentos/voctomix/experiments/comprehensive/lib_video.py` — detecta en la salida del
  mix cuándo desaparece y cuándo vuelve la cámara.
- `/home/sonda/Documentos/voctomix/docker-compose.experiment.yml` — cámaras con vídeo real.
- `/home/sonda/Documentos/voctomix/experiments/comprehensive/set_format.sh` — fija el formato.

---

## 4. Ficheros comunes a todas las pruebas
- `/home/sonda/Documentos/voctomix/experiments/comprehensive/run_matrix.py` — el **orquestador**:
  ejecuta las 20 pruebas en orden, valida cada resultado, reintenta si algo falla, y va dejando
  todo registrado. Es lo que lanza automáticamente todas las pruebas anteriores.
- `/home/sonda/Documentos/voctomix/experiments/comprehensive/lib_common.py` — funciones de
  estadística (media, mediana, percentiles) y escritura de los CSV/Excel.
- `/home/sonda/Documentos/voctomix/docker-compose.yml` — el stack base de Docker (voctocore,
  telemetría, cámaras y demás servicios).
- `/home/sonda/Documentos/voctomix/voctocore/default-config.ini` — la configuración de voctocore
  (resolución, framerate…), que `set_format.sh` modifica para cada formato.
- `/home/sonda/Documentos/voctomix/videos/bbb_sunflower_2160p_60fps_normal.mp4` — el vídeo fuente (Big Buck Bunny 4K).
- `/home/sonda/Documentos/voctomix/paper/pruebas/AUDIT_MATRIX.md` — el registro con marcas de tiempo de toda la ejecución.

---

## 5. Dónde están los datos de cada prueba
Tengo una carpeta por cada formato, y dentro una carpeta por cada prueba:
```
/home/sonda/Documentos/voctomix/paper/pruebas/
├── piloto_docker_1080p25/     (formato 1080p25)
├── docker_1080p50/            (formato 1080p50)
├── docker_2160p25/            (formato 2160p25)
└── docker_2160p50/            (formato 2160p50)
     └── <prueba>/             (1-1_escalado, 1-2_sostenida, 2-1_lat_camara, 2-2_lat_composicion, 3-1_resiliencia)
          ├── datos.csv         ← TODAS las medidas crudas
          ├── resumen.csv       ← estadística (mediana, P95, P99, media, desviación)
          ├── datos.xlsx        ← lo mismo en Excel
          ├── run.log           ← traza de la ejecución
          └── capturas/
```
Así, para cualquier prueba podéis abrir su `datos.csv` o `datos.xlsx` y construir vuestras
propias gráficas y tablas (no genero figuras automáticamente, solo dejo los números crudos).

---

## 6. Ejemplos de resultados (para ver que tienen sentido)
- **Rendimiento 1080p25 (escalado):** CPU 0% → 40,7% (1 cám) → 45,6% → 62,3% → 90,2% (4 cám).
- **Rendimiento 2160p25 / 4K (escalado):** 0% → 56,4% → 71,0% → 86,1% → 94,9% (con 4 cámaras el
  4K casi satura, que me parece un resultado interesante).
- **Latencia de cámara y de composición:** del orden de ~290–300 ms (es la latencia real de la
  tubería de voctocore).
- **Resiliencia:** la cámara se recupera sola, con un MTTR del orden de ~1,8 s.

*(El formato 2160p50, que es 4K a 50fps, es el más exigente: sus datos reflejan el
comportamiento del sistema en el límite / techo de rendimiento.)*
