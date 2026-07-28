# Justificación metodológica (para el paper y respuesta a revisores)

Notas de defensa metodológica de las pruebas. Cada punto está pensado para poder
justificarlo directamente si un revisor lo cuestiona.

---

## 1. Medición de CPU y RAM: misma fuente que `htop`

**Afirmación:** el punto exacto del que leemos CPU y RAM es **el mismo que utiliza el
comando `htop`** (y `top`, `free`, `vmstat`): las interfaces del kernel `/proc/stat` y
`/proc/meminfo`. No es una estimación propia ni una capa intermedia.

### CPU
- Se lee la línea agregada de `/proc/stat` y se calcula:
  `CPU% = 100 · (1 − Δidle / Δtotal)` sobre el intervalo de muestreo.
- Es **exactamente** el cálculo que hace `htop`/`top` para el porcentaje global de CPU
  (delta de jiffies ocupados frente a totales entre dos lecturas de `/proc/stat`).

### RAM
- Se lee `/proc/meminfo` y se calcula:
  `RAM% = 100 · (MemTotal − MemAvailable) / MemTotal`.
- Se usa `MemAvailable`, que es la métrica **recomendada por el propio kernel** para
  estimar la memoria realmente disponible (considera page cache reclamable). Es la misma
  fuente `/proc/meminfo` que lee `htop`.

### Consistencia entre escenarios
El mismo cálculo, **byte a byte**, se emplea en los dos caminos de medida del proyecto:
- Local (nativo): `experiments/comprehensive/measure_performance_local.py` (funciones
  `read_cpu` y `read_ram`).
- Docker: servicio de telemetría `example-scripts/ffmpeg/telemetry_service.py`
  (`update_system_health`, mismas líneas de fórmula).

Por tanto, verificar la coincidencia con `htop` en **un** escenario valida la metodología
de **ambos** (idéntico código de medida sobre idéntica fuente del kernel).

### Comprobación empírica realizada (una sola vez, interna)
Con las 4 cámaras activas, comparación en vivo de nuestra fórmula frente a las
herramientas estándar del sistema:

| Métrica | Nuestra fórmula (idéntica a la telemetría Docker) | Referencia del sistema |
|---|---|---|
| CPU | 90,4 % | `top`: 9,0 % idle → 91,0 % ocupado |
| RAM | 9,0 % | `free`: 9,0 % |

Coinciden dentro del margen del muestreo. **Esta comprobación es interna y no altera el
procedimiento de medida ni la forma de presentar los datos**, que se mantienen tal cual.

> Nota operativa: en el equipo de pruebas puede instalarse `htop` con `sudo apt install
> htop` para una captura visual equivalente; muestra los mismos valores porque lee los
> mismos contadores del kernel.

---

## 2. Latencia: método principal y validación

- **Método principal (el que se reporta):** latencia *glass-to-glass* medida sobre la
  salida real del mix (puerto 11000) por detección del cambio de color. Es la latencia de
  vídeo real percibida, y es la metodología estándar en broadcast (marcadores visuales).
  Validada: idéntica en dos salidas independientes (11000 y 12000), luego no es artefacto
  del lector; precisión acotada al periodo de frame.
- **Validación complementaria (a nivel de API):** el puerto de control 9999 devuelve un
  `video_status` cuando voctocore aplica el cambio. Medir ese instante da la latencia de
  control (pocos ms) y demuestra que los ~290 ms residen en el pipeline de vídeo
  (buffering + composición + codificación), no en el manejo del comando. Es una
  comprobación añadida, **no sustituye** al método principal.
