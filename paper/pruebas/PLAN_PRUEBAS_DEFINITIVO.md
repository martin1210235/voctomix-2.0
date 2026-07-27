# PLAN DE PRUEBAS DEFINITIVO — Voctomix 2.0 (paper MDPI + TFG)

**Última actualización:** 2026-07-24 (tras reunión con tutores Álvaro y Alberto)
**Ubicación canónica:** `paper/pruebas/` — aquí vive este plan y TODOS los documentos y datos de cada prueba.
**Estado:** APROBADO el enfoque. Ejecución MANUAL, incremental, empezando por prueba piloto.

---

## 0. DIRECTRICES DE LOS TUTORES (mandan sobre todo lo demás)

De la reunión / hilo de Teams con Álvaro Llorente y Alberto del Río, decisiones que son de OBLIGADO cumplimiento:

1. **Las pruebas las ejecuta Martín a mano.** Los tutores NO ejecutan. Martín maneja el código; ellos reciben los datos.
2. **Ejecución MANUAL, no automática.** → **El agente autónomo queda SUSPENDIDO** para esta primera tanda. Son pruebas iniciales "de prueba" antes de las pruebas buenas. Se ejecuta paso a paso, a mano, supervisando cada una.
3. **Entregable = datos numéricos crudos, NO gráficas.** Literal de Álvaro: *"saca los datos numéricos en excels o csvs, que no sea claude el que pinte las gráficas"*. Ellos pintan las gráficas y tablas a partir de los números. Si la figura ya viene generada, no pueden sacar sus propios resultados. → **NUNCA generar gráficas. Solo datos crudos + estadística en tablas de números.**
4. **Por cada prueba:** (a) una explicación breve de cómo se ha hecho esa prueba, (b) el fichero de datos con TODOS los datos de esa prueba, (c) capturas de pantalla de la ejecución.
5. **Pantallazos:** ir pasando capturas cuando se hacen los tests.
6. **Contexto del PC al medir:** literal de Alberto: *"no pasa nada si en el pc tienes cosas, pero intenta tener generalmente todo cerrado, rollo Teams, y que sea la terminal o lo que estés ejecutando. Así sacas el valor del consumo, no del PC a lo bruto, sino de eso en concreto."* → Cerrar aplicaciones (Teams, navegador, etc.) antes de medir. Dejar solo la terminal y lo que se está ejecutando. Al empezar cada bloque (Docker, luego Kubernetes) avisar a los tutores: "no tengo nada abierto en el PC, mirad lo que me sale".
7. **Kubernetes: NO usar minikube.** Literal de Alberto: *"no uses minikube que eso es docker. Utiliza kind o k3s, que se instalan con 2 comandos igualmente en el PC."* → El escenario Kubernetes se rehace con **kind o k3s**, no con minikube. Esto invalida el approach de las pruebas anteriores para K8s.
8. **Orden:** Docker primero, Kubernetes lo último. (Local en medio.)

---

## 1. QUÉ HAY QUE MEDIR (plan de tutores, sin recortes)

**Matriz: 3 escenarios × 4 formatos de vídeo = 12 celdas.**

- **Escenarios:** local, docker, kubernetes (con kind/k3s).
- **Formatos:** 1080p25, 1080p50, 2160p25, 2160p50.

En cada celda (escenario × formato), tres análisis:

### Análisis 1 — Rendimiento
- **1.1 Escalado de cámaras:** activar cámara 1 → 2 → 3 → 4, **una cada 15 minutos**. Medir **CPU (%)** y **RAM (%)**.
- **1.2 Carga sostenida:** con las **4 cámaras activas, 2 horas**. Medir **CPU (%)** y **RAM (%)**.

### Análisis 2 — Latencia de conmutación
> **DEFINICIÓN CONFIRMADA POR LOS TUTORES (2026-07-24):** miden la **latencia de vídeo real**, es decir, *"el tiempo que tarda en hacerse el cambio"* hasta que se ve en la salida, **en milisegundos** — NO la confirmación del plano de control. Ejemplos que dieron: el tiempo que tarda el cambio de cámara **en corte directo**, y el tiempo que tarda el cambio a **side-by-side**.

- **2.1 Conmutación entre cámaras (corte directo):** tiempo desde que se ejecuta el comando de cambio de cámara hasta que la nueva cámara es visible en la salida de programa. **100 veces.** Métrica en ms.
- **2.2 Conmutación entre modos de composición** (p. ej. a side-by-side): tiempo desde el comando hasta que el nuevo modo de composición es visible en la salida. **100 veces.** Métrica en ms.

**Cómo se mide la latencia de vídeo real (implementación, VERIFICADO 2026-07-24):** cada cámara lleva un marcador de color único quemado en la esquina superior-izquierda (cam1=rojo, cam2=verde, cam3=azul, cam4=amarillo). Un lector de frames sobre la **salida del mix** detecta, por análisis de píxeles de esa esquina (sin guardar vídeo), el primer frame que ya muestra el color de la cámara destino. `latencia_ms = t(primer frame con el cambio) − t(envío del comando)`. Se registra **adicionalmente** la latencia de plano de control (comando→confirmación, con el `tools/measure_composite_latency.py` ya existente) como dato secundario. La métrica PRINCIPAL entregada es la de vídeo real en ms.

> **PUNTO DE MEDICIÓN CORREGIDO:** el vídeo compositado sale por el **puerto 11000 (mix crudo)** y **12000 (preview JPEG)**, NO por el 15000. El 15000 es la salida de *programa* que pasa por el stream-blanker (al arrancar está en negro/offline). Verificado: los marcadores de color se ven perfectamente en 11000/12000. Colores medidos: rojo (255,23,0), verde (0,214,0), azul (0,14,255), amarillo (255,238,0) — bien separados, clasificación trivial.

**Nota sobre 2.2 (corte vs transición):** el cambio de cámara (2.1) es en **corte directo**. Para composición (2.2), voctomix puede hacer el cambio en corte (`set_composite_mode`, inmediato) o con **transición animada** (`transition`, 750 ms fijos por configuración). Como los tutores hablan de *"el tiempo que tarda en hacerse el cambio"*, se mide el tiempo real hasta que el nuevo layout está visible. Se capturan ambos (corte y transición) etiquetados, para que los tutores elijan; si hay que dar uno solo, el corte es la métrica de rendimiento pura (la transición mide la constante de 750 ms de diseño).

### Análisis 3 — Resiliencia y recuperación
- **3.1 Caída de una cámara:** forzar la caída de una cámara y medir el tiempo de recuperación, **~100 veces** (ajustable según lo que tarde el ciclo de caída + arranque).

---

## 2. ENTREGABLES POR PRUEBA (formato fijo)

Cada prueba individual (una combinación escenario × formato × análisis) genera una **subcarpeta** dentro de `paper/pruebas/` con:

```
paper/pruebas/
└── <NN>_<escenario>_<formato>_<analisis>/
    ├── README.md          # explicación breve: qué se midió, cómo, comandos usados, condiciones del PC
    ├── datos.csv          # TODOS los datos crudos (fuente de verdad)
    ├── resumen.csv        # estadística agregada (n, media, mediana, P95, P99, min, max, std)
    ├── datos.xlsx         # (opcional) mismo contenido en Excel, para comodidad de los tutores
    └── capturas/          # pantallazos de la ejecución
        ├── 01_pc_limpio.png
        ├── 02_arranque.png
        └── ...
```

**Regla de oro:** el `datos.csv` contiene los números crudos, uno por muestra/iteración. Nada de gráficas. Los tutores construyen figuras y tablas a partir de estos ficheros.

---

## 3. CSV vs EXCEL — decisión

**Formato canónico: CSV.** Adicionalmente, y solo por comodidad, un `.xlsx` por prueba que empaqueta lo mismo.

Razones para que el CSV sea la fuente de verdad:
- Se genera desde Python con la librería estándar (`csv`), sin dependencias que puedan fallar a mitad de una prueba de 2 horas.
- No se corrompe, es diffeable, y se versiona limpio en git.
- Se abre nativamente en Excel, LibreOffice y Google Sheets: los tutores pueden hacer tablas/gráficas directamente.
- Un CSV = una serie de datos limpia (una fila por muestra o por iteración).

El `.xlsx` (generado A PARTIR del CSV, así que sin riesgo de pérdida de datos) aporta poder juntar en un solo fichero varias hojas (p. ej. "datos crudos" + "resumen"). Como los tutores nombraron "excels", se lo damos también, pero **si la generación de xlsx fallara por lo que sea, el CSV ya garantiza todos los datos**. Por eso el CSV manda.

---

## 4. HALLAZGOS TÉCNICOS DEL CÓDIGO REAL (verificados, no asunciones)

### 4.1 Cambio de formato de vídeo
| Componente | Estado | Acción |
|---|---|---|
| `docker-compose.yml` | Ya parametrizado con `${WIDTH}`, `${HEIGHT}`, `${FRAMERATE}` | Cambiar formato = exportar 3 variables de entorno |
| `voctocore/default-config.ini` | `videocaps` **hardcodeado** (1920×1080@25). voctocore no lee las env del compose | Pre-generar **4 configs** (una por formato); voctocore arranca con `-i <config>` |
| K8s manifests (`cameras.yaml`) | `testsrc2=size=1920x1080:rate=25` hardcodeado | Templatizar por formato (se rehace con kind/k3s de todos modos) |
| Escenario local (`start_studio_single_pc.sh`) | ffmpeg nativo por proceso | Templatizar resolución/fps de los comandos ffmpeg |
| Reconfiguración en caliente | **NO existe** (caps fijados al construir el pipeline GStreamer) | Cada cambio de formato = parada + arranque completo del stack |

Conclusión: 4 configs pre-generadas + variables de entorno + plantillas. Reinicio completo por celda con verificación de que el formato REAL cargado es el declarado (gate anti "formato asumido").

### 4.2 Protocolo de control (puerto 9999, verificado en `voctocore/lib/commands.py`)
- **Conmutar cámara (2.1):** `set_video_a <cam>` → respuesta `video_status`.
- **Conmutar composición (2.2):** `set_composite_mode <modo>` / `cut` (corte inmediato) **o** `transition <modo>(A,B)` (transición animada de **750 ms fijos**, definidos en `[transitions]` del config).
- Ya existe `tools/measure_composite_latency.py` que mide comando→confirmación (latencia de plano de control, histograma previo 1–8 ms).

### 4.3 Caída/recuperación de UNA cámara (3.1)
| Escenario | Matar la cámara | Quién la recupera |
|---|---|---|
| Local | `pkill -f "tcp://localhost:1000N"` | Bucle `while true` del script de fuente |
| Docker | `docker kill camN` | Política `restart` + reconexión ffmpeg |
| Kubernetes (kind/k3s) | `kubectl delete pod camN-...` | kubelet recrea el pod |

### 4.4 Medición CPU%/RAM%
`example-scripts/ffmpeg/telemetry_service.py` lee `/proc/stat` y `/proc/meminfo` del **host** → STATE events con `cpu_usage_percent` y `ram_usage_percent`. Métrica a nivel host, **comparable entre los 3 escenarios**. Se reutiliza tal cual. **Ojo con la directriz 6:** cerrar Teams y demás antes de medir para que el consumo refleje la prueba, no el ruido del PC.

---

## 5. PROBLEMAS QUE HAY QUE RESOLVER ANTES DE EMPEZAR

**P1 — Fuentes de cámara distintas entre escenarios (crítico para validez).** Docker descarga MP4 reales por HTTPS (¡red externa en mitad de un test de CPU!); K8s usa `testsrc2` sintético. Comparar CPU% entre escenarios con fuentes distintas es inválido para el paper. → **Unificar la fuente en los 3 escenarios** con ficheros de vídeo locales en bucle (`-stream_loop -1`): realista (hay decodificación H.264), reproducible (sin red), idéntico en local/docker/k8s. Para 2160p, el material fuente es 1080p → habría upscaling: conseguir material 4K o documentar el upscaling.

**P2 — El healthcheck de las cámaras no comprueba la cámara.** Comprueba el puerto 9999 de voctocore (comparten namespace de red). El MTTR anterior medía "contenedor arrancado + voctocore vivo", no "la cámara volvió". → Señal de recuperación real: **conexión TCP restablecida en el puerto de la fuente (10000+N) con tráfico**, verificable con `ss` en el host en los 3 escenarios.

**P3 — Verificar el mecanismo de reinicio en Docker.** Usar `docker kill` (SIGKILL, caída no limpia, representativa) y confirmar en el piloto qué lo reinicia exactamente.

**P4 — Riesgo de saturación en 2160p50.** 4 cámaras crudas I420 4K50 ≈ 2,5 GB/s por loopback + composición 4K50 software. Puede saturar el i9. Si satura, es un **resultado publicable** (techo de rendimiento), pero hay que descubrirlo pronto con un smoke test, no en mitad de la tanda. Los pods K8s piden `cpu: 250m` (insuficiente para 4K): escalar requests por formato.

**P5 — Contaminación térmica entre celdas.** 2 h a 4K pueden provocar throttling. → Registrar temperatura/frecuencia de CPU junto a cada muestra (legible sin sudo en `/sys/class/thermal` y `/proc/cpuinfo`), enfriar 5–10 min entre celdas, vigilar disco (~46 GB libres; **nunca** guardar vídeo crudo).

**P6 — kind/k3s en vez de minikube.** El escenario Kubernetes se rehace con kind o k3s (directriz 7). Elegir uno en su momento (k3s es más ligero y "más Kubernetes real"; kind corre sobre Docker pero es lo estándar para pruebas). Se decide al llegar a la fase de Kubernetes. **kind y k3s NO están instalados aún** (verificado); minikube sí (a desinstalar/parar).

**P7 — El entorno actual está sucio (revisión 2026-07-24).** Hay un stack Docker de hace 7 días corriendo con casi todos los contenedores en estado **unhealthy** (voctocore, cam1–4, break, stream_blanker, audio_manager, intro), y **minikube lleva 7 días arrancado**. Esto contamina cualquier medida y NO es el "PC limpio" que piden los tutores. → **Antes de cualquier prueba: `docker compose down`, parar/eliminar minikube, y arrancar un stack fresco con la config del formato que toque.** Disco al 92% (44 GB libres): suficiente solo si NUNCA se guarda vídeo crudo.

**P8 — No existen los ficheros `sources_camN.txt` ni hay material de vídeo adecuado.** Verificado: `experiments/sources_cam*.txt` NO existen. Las fuentes de cámara viven realmente en (a) los comandos ffmpeg del `docker-compose.yml` (con URLs remotas `CAM_SOURCE`), (b) `k8s_escenario/experiments/cameras.yaml` (testsrc2), (c) scripts de `example-scripts/ffmpeg` para local. La referencia de Álvaro a "sources_cam1..." es conceptual: el cambio de formato se aplica en esos 3 sitios reales + el `.ini`. Además, en `videos/` solo hay clips pequeños (intro, slides, cuenta atrás), **no hay material de cámara real ni 4K**. → El BLOQUE A (A1/A2) tiene que conseguir vídeo(s) fuente locales, idealmente 4K, antes de poder unificar fuentes. **RESUELTO:** descargado Big Buck Bunny 4K 60fps (CC-BY, Blender), en `videos/bbb_sunflower_2160p_60fps_normal.mp4`.

**P9 — voctocore exige colorimetría bt709 en las fuentes (VERIFICADO/RESUELTO).** Al unificar las cámaras al máster local, voctocore las rechazaba: `incoming caps colorimetry=2:0:0:0` ≠ `configured caps colorimetry=bt709`. Causa: las cámaras no etiquetaban bt709 (las remotas originales sí lo traían del propio fichero). Solución aplicada en `docker-compose.experiment.yml`: `setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709` en el filtro + flags `-color_primaries/-color_trc/-colorspace bt709 -color_range tv` en la salida. Tras el arreglo, las 4 cámaras conectan y alimentan vídeo correctamente (verificado en 11000/12000).

### ESTADO DEL BLOQUE A (2026-07-24) — COMPLETO Y VERIFICADO
Toda la herramienta de medida construida y probada en vivo. Guía operativa: **`paper/pruebas/RUNBOOK.md`**.
- Entorno limpio; `docker-compose.yml` con conflictos de merge resueltos y validado.
- `set_format.sh` — cambio de formato (config voctocore + `.env` con SAVE_LOGS=true), probado en los 4 formatos.
- `docker-compose.experiment.yml` (BBB + marcadores, para Análisis 1 y 3) y `docker-compose.latency.yml` (color sólido, para Análisis 2), ambos con bt709, validados y probados en vivo.
- Medidores probados contra el stack real:
  - `run_performance.py` + `parse_performance.py` (1.1/1.2): CPU escala 39%→67% de 1 a 4 cámaras. ✓
  - `measure_latency_camera.py` (2.1): ~275-315 ms. ✓
  - `measure_latency_composite.py` (2.2, fs↔sbs con `cut`): ~278 ms. ✓
  - `measure_camera_recovery.py` (3.1, crash `pkill` + auto-restart): MTTR ~1.8 s. ✓
- Mecanismos clave verificados: medir en puerto **11000**; conmutar composición con **`cut`** (no `set_composite_mode`); caída con **`docker exec pkill -9 ffmpeg`** (no `docker kill`).
- **Siguiente:** ejecutar la PILOTO Docker+1080p25 (5 análisis con las duraciones reales) y enviarla a los tutores.

---

## 6. QUÉ EMPEZAMOS HACIENDO (detallado)

Ejecución **manual e incremental**. No se lanza la matriz entera de golpe. Se hace celda a celda, empezando por una **prueba piloto** que sirve de plantilla y se envía a los tutores para validar el formato de entrega antes de escalar.

### Etapa 0 — Preparación (medio día, sin medir aún)
1. Resolver P1: descargar 1–2 vídeos fuente locales y unificar las fuentes de cámara en Docker (y luego local/k8s). Idealmente material 4K para no hacer upscaling.
2. Pre-generar las 4 configs de voctocore (una por formato) + fichero `.env` de formato para Docker.
3. Construir las **herramientas manuales** (que Martín ejecuta a mano, no un agente):
   - cambio de formato + verificación,
   - medidor de rendimiento (1.1 y 1.2) → CSV,
   - medidor de latencia cámara (2.1) → CSV,
   - medidor de latencia composición (2.2) → CSV,
   - medidor de resiliencia cámara (3.1) → CSV,
   - exportador CSV→XLSX + cálculo de `resumen.csv`.
4. Verificar a mano que el cambio de formato funciona en Docker (arranca, formato correcto, 4 fuentes conectadas).

### Etapa 1 — PRUEBA PILOTO: Docker + 1080p25 (1 día supervisado)
Ejecutar los 3 análisis completos sobre la celda más ligera y mejor entendida:
- Cerrar todo en el PC (Teams, navegador…). Captura del PC "limpio".
- 1.1 escalado (4×15 min) → CSV + capturas.
- 1.2 sostenida (2 h) → CSV + capturas.
- 2.1 y 2.2 latencia (100+100) → CSV + capturas.
- 3.1 resiliencia (~100) → CSV + capturas.
- Redactar el `README.md` de cada prueba y generar `resumen.csv` + `datos.xlsx`.
- **Enviar a los tutores** el paquete de la piloto: explicaciones + CSVs + capturas. Esperar su OK sobre el formato antes de escalar.

> Opcional recomendado: antes de la piloto "de verdad", un **ensayo en seco** con duraciones cortas (p. ej. sostenida de 15 min en vez de 2 h) solo para validar que toda la cadena de scripts y CSVs funciona. Esos datos NO se envían como resultados; es solo para no descubrir un bug a las 2 horas.

### Etapa 2 — Resto de formatos en Docker
1080p50 → 2160p25 → 2160p50 (una celda por sesión). Antes de 2160p50, **smoke test** para ver si satura.

### Etapa 3 — Escenario Local
Los 4 formatos, misma metodología, con las fuentes ya unificadas.

### Etapa 4 — Escenario Kubernetes (kind o k3s) — LO ÚLTIMO
Instalar kind/k3s, rehacer los manifests con la fuente unificada y requests escalados por formato, y ejecutar los 4 formatos. Avisar a los tutores al empezar este bloque.

### Cierre
Entregar el conjunto completo de CSVs + explicaciones + capturas de las 12 celdas. Los tutores hacen las figuras y tablas del paper; Martín redacta cap5 del TFG con esos mismos números.

---

## 6-BIS. ORDEN CRONOLÓGICO COMPLETO — TODO LO QUE HAY QUE HACER, PASO A PASO

Lista maestra de cada acción y cada prueba, en el orden exacto en que se ejecutan. Cada prueba de medición genera su subcarpeta con `README.md` + `datos.csv` + `resumen.csv` + `datos.xlsx` + `capturas/`. Los pasos de preparación y los smoke tests NO son entregables de datos (salvo que se indique), son de validación.

### BLOQUE A — PREPARACIÓN GLOBAL (una sola vez, sin medir)
- **A1.** Descargar 1–2 vídeos fuente locales a `videos/` (idealmente material 4K nativo; si no, se documenta upscaling para 2160p).
- **A2.** Unificar las fuentes de cámara para que en local, Docker y K8s usen el MISMO vídeo local en bucle (resuelve P1). 
- **A3.** Pre-generar las 4 configs de voctocore (1080p25, 1080p50, 2160p25, 2160p50) + `.env` de formato para Docker + plantillas de manifests para K8s.
- **A4.** Construir las herramientas MANUALES (un comando → una prueba → un CSV): cambio de formato+verificación, medidor rendimiento (1.1/1.2), medidor latencia cámara (2.1), medidor latencia composición (2.2), medidor resiliencia (3.1), exportador CSV→XLSX + resumen.
- **A5.** Verificar a mano el cambio de formato en Docker (arranca, formato REAL correcto, 4 fuentes conectadas).
- **A6. (Ensayo en seco, opcional pero recomendado):** una pasada con duraciones cortas (sostenida de 15 min, latencias de 10, resiliencia de 5) en Docker+1080p25 para validar que toda la cadena de scripts y CSVs funciona. **Estos datos NO se envían.**

### BLOQUE B — DOCKER (escenario 1, el primero)
> Antes de empezar: cerrar Teams/navegador/etc. Captura del PC limpio. Avisar a tutores: "no tengo nada abierto, mirad lo que sale".

**Celda B1 — Docker + 1080p25 (PRUEBA PILOTO → se envía y se espera OK de tutores):**
- B1.1 Rendimiento: escalado de cámaras (baseline 0 + cam1→2→3→4, 15 min cada una).
- B1.2 Rendimiento: sostenida 4 cámaras, 2 h.
- B1.3 Latencia: conmutación entre cámaras (corte), 100 veces.
- B1.4 Latencia: conmutación de composición (side-by-side), 100 veces.
- B1.5 Resiliencia: caída de cámara + recuperación, ~100 veces.
- → Empaquetar, redactar READMEs, generar resumen+xlsx, **ENVIAR A TUTORES. Esperar visto bueno del formato antes de seguir.**

**Celda B2 — Docker + 1080p50:** B2.1, B2.2, B2.3, B2.4, B2.5 (mismos 5 análisis).

**Celda B3 — Docker + 2160p25:** B3.1, B3.2, B3.3, B3.4, B3.5.

- **SMOKE TEST S1 — Docker 2160p50:** antes de la celda B4, arranque + 4 cámaras 4K50 durante ~2–3 min para ver si el i9 satura (CPU/RAM/ancho de banda). Si satura → se documenta como techo de rendimiento y se acuerda con tutores cómo presentar la celda. Captura del resultado.

**Celda B4 — Docker + 2160p50:** B4.1, B4.2, B4.3, B4.4, B4.5 (o versión "techo de rendimiento" según S1).

### BLOQUE C — LOCAL (escenario 2)
> Recordatorio: PC limpio + captura + aviso a tutores.

- **A5-local.** Verificar a mano el cambio de formato en el arranque local (`start_studio_single_pc.sh` templatizado).
**Celda C1 — Local + 1080p25:** C1.1…C1.5.
**Celda C2 — Local + 1080p50:** C2.1…C2.5.
**Celda C3 — Local + 2160p25:** C3.1…C3.5.
- **SMOKE TEST S2 — Local 2160p50:** ~2–3 min de 4 cámaras 4K50 para comprobar saturación en modo nativo.
**Celda C4 — Local + 2160p50:** C4.1…C4.5.

### BLOQUE D — KUBERNETES con kind o k3s (escenario 3, EL ÚLTIMO)
> Recordatorio: PC limpio + captura + aviso a tutores al empezar este bloque.

- **D0a.** Instalar kind o k3s (2 comandos). **NO minikube.**
- **D0b.** Rehacer los manifests con la fuente unificada y requests de CPU/memoria escalados por formato.
- **D0c.** Verificar despliegue: pods arriba, 4 fuentes conectadas, formato real correcto.
- **SMOKE TEST S3 — K8s arranque básico:** desplegar en 1080p25 y comprobar que voctocore responde y las 4 cámaras conectan antes de medir nada.
**Celda D1 — K8s + 1080p25:** D1.1…D1.5.
**Celda D2 — K8s + 1080p50:** D2.1…D2.5.
**Celda D3 — K8s + 2160p25:** D3.1…D3.5.
- **SMOKE TEST S4 — K8s 2160p50:** comprobar saturación en K8s.
**Celda D4 — K8s + 2160p50:** D4.1…D4.5.

### BLOQUE E — CIERRE
- **E1.** Consolidar los CSVs de las 12 celdas (60 pruebas de datos en total).
- **E2.** Entregar el conjunto completo a los tutores (ellos hacen figuras/tablas del paper).
- **E3.** Martín redacta cap5 del TFG con esos mismos números.

**Resumen de volumen:** 3 escenarios × 4 formatos = 12 celdas × 5 análisis = **60 pruebas de datos**, + 4 smoke tests (S1–S4) + 1 ensayo en seco (A6). Cada prueba de datos = 1 subcarpeta con explicación + CSV + resumen + xlsx + capturas.

---

## 7. TIMELINE ORIENTATIVO

| Fase | Contenido | Duración | Entregable |
|---|---|---|---|
| Etapa 0 | Preparación: fuentes unificadas + configs + herramientas manuales | ~medio día | Herramientas listas, formato verificado en Docker |
| Etapa 1 | Piloto Docker+1080p25 (3 análisis) | ~1 día supervisado (incluye 2 h de sostenida) | Paquete piloto → tutores, esperar OK |
| Etapa 2 | Docker 1080p50 / 2160p25 / 2160p50 | ~1 celda por sesión (~4–5 h cada una) | 3 paquetes de datos |
| Etapa 3 | Local ×4 formatos | ~4 sesiones | 4 paquetes de datos |
| Etapa 4 | Kubernetes (kind/k3s) ×4 formatos | ~4 sesiones + setup | 4 paquetes de datos |
| Cierre | Consolidación y entrega final | ~medio día | 12 celdas completas |

Cada "celda completa" (3 análisis) ≈ 4,8 h de ejecución real, dominada por las 2 h de la sostenida (1.2) y ~1 h de resiliencia (3.1). Como es manual y supervisado, se hace por sesiones, no del tirón.

**Nota de recorte (si el tiempo aprieta):** lo primero a proponer a los tutores sería bajar la sostenida (1.2) de 2 h a 1 h (ahorra ~12 h en la matriz completa) o reducir resiliencia a n=50 (el IC ya es estrecho con el CV<2% observado). Pero el punto de partida es el plan completo tal cual lo pidieron.

---

## 8. PREGUNTAS A LOS TUTORES

**RESUELTAS:**
- ✅ **Definición de latencia (2.1/2.2):** CONFIRMADO (2026-07-24) → **latencia de vídeo real en ms** (tiempo hasta que el cambio se ve en la salida). 2.1 = cambio de cámara en corte directo; 2.2 = cambio a modo de composición (side-by-side). Se registra también la de control como dato secundario.

**PENDIENTES:**
1. **2.2 corte vs transición:** se medirán ambos y se etiquetan; confirmar cuál prefieren como principal (recomendación: corte para rendimiento puro).
2. **Fuentes de cámara:** OK a unificar con vídeo local en los 3 escenarios. ¿Conseguimos material fuente 4K o documentamos upscaling para 2160p?
3. **2160p50:** si el smoke test satura, ¿lo presentamos como techo de rendimiento (resultado válido)?
4. **kind vs k3s:** confirmar preferencia (o lo elige Martín; k3s más ligero, kind más estándar).
5. **n de resiliencia:** confirmar ~100 iteraciones.

---

## 9. ESTADO DEL AGENTE AUTÓNOMO

**SUSPENDIDO** por decisión de los tutores (ejecución manual para esta tanda inicial). Todo el trabajo de diseño del agente (arquitectura, recuperación, auditoría en tiempo real) queda archivado y se podrá retomar para las "pruebas buenas" posteriores si los tutores lo aprueban. Las herramientas que se construyan ahora se diseñan para ejecución **manual** (un comando → una prueba → un CSV), pero de forma que en el futuro se puedan encadenar automáticamente sin reescribirlas.
