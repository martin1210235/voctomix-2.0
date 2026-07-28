# Justificación de la implementación de las pruebas (para tutores)

Documento para explicar y defender cómo está implementada cada parte de las pruebas.

---

## 0. Verificación del cambio de formato (lo que pedís ver)

### Evidencia A — El formato se fija con un único script (fuente de verdad)
`experiments/comprehensive/set_format.sh <formato>` reescribe los `videocaps` de voctocore.
Verificado que produce exactamente los caps correctos para los 4 formatos:

```
set_format.sh 1080p25 -> videocaps = video/x-raw,format=I420,width=1920,height=1080,framerate=25/1
set_format.sh 1080p50 -> videocaps = video/x-raw,format=I420,width=1920,height=1080,framerate=50/1
set_format.sh 2160p25 -> videocaps = video/x-raw,format=I420,width=3840,height=2160,framerate=25/1
set_format.sh 2160p50 -> videocaps = video/x-raw,format=I420,width=3840,height=2160,framerate=50/1
```
El mismo script escribe también el `.env` de las cámaras (WIDTH/HEIGHT/FRAMERATE), así que
**el compositor y las cámaras nunca pueden ir a formatos distintos**. Tiene una comprobación de
seguridad final que aborta si el config no refleja el formato pedido.

### Evidencia B — En Kubernetes se verifica el formato REAL con ffprobe
Además del config, en K8s se comprueba la salida real del mix (puerto 11000) con `ffprobe`:
```
width=1920
height=1080
r_frame_rate=25/1        -> confirmado 1920x1080@25 en la salida real
```
El orquestador de K8s ejecuta esta verificación `ffprobe` **en CADA celda** (los 4 formatos),
así que la matriz K8s deja registrado que cada formato corre de verdad a su resolución/fps.

### Estado honesto
- **Config (los 4 formatos)**: verificado correcto (evidencia A). Mismo mecanismo en local/docker/k8s.
- **Runtime (salida real)**: confirmado con ffprobe en K8s (1080p25 y el resto según avanza la
  matriz). La verificación ffprobe retroactiva de Docker/Local es una comprobación rápida que
  estamos completando (no cambia cómo se fijó el formato, solo lo re-confirma en la salida).

---

## 1. Escenarios (los 3)
- **Local (nativo)**: voctocore + fuentes como procesos del host (sin Docker).
- **Docker**: `docker compose`, cada componente en su contenedor.
- **Kubernetes (k3s)**: se usa **k3s** (no minikube, que sería "docker otra vez"); despliegue real
  sobre el host con containerd. voctocore, soporte y cámaras como Deployments con `hostNetwork`.
Justificación: comparar el coste de cada nivel de despliegue (nativo < contenedores < orquestación).

## 2. Medición de CPU y RAM (análisis 1)
- Se leen de `/proc/stat` (CPU = 1 − Δidle/Δtotal) y `/proc/meminfo` (RAM = (MemTotal−MemAvailable)/
  MemTotal). **Es la MISMA fuente que usa `htop`/`top`/`free`.** Verificado en vivo que coincide.
- Mismo cálculo, idéntico, en los 3 escenarios (código compartido). Con el PC despejado, el valor
  refleja el consumo del despliegue (en K8s incluye la sobrecarga de k3s, que es justo lo que
  queremos comparar).
- **1.1 escalado**: se activan las cámaras 1→4, midiendo cada 15 min; **añadido un baseline de
  15 min a 0 cámaras** al inicio (punto 0 del eje X limpio).
- **1.2 sostenida**: 4 cámaras durante 2 h (la de 24 h se hará al final para el estudio del leak).

## 3. Latencia (análisis 2) — VÍDEO REAL
- Se mide la **latencia glass-to-glass**: desde que se ordena el cambio hasta que se ve en la salida
  real del mix, NO la confirmación del protocolo. Es la metodología estándar en broadcast (detección
  por marcador de color).
- **Cómo**: cámaras de color sólido; se envía la orden por el puerto de control (9999), se marca t0,
  y un lector de la salida (11000) detecta el primer frame cuyo color ya es el destino → t1.
  Latencia = t1 − t0. 100 repeticiones.
- **2.1**: conmutación de cámara (corte directo). **2.2**: conmutación de composición
  (pantalla completa ↔ side-by-side). Se mide el corte, no la transición animada (que es una
  constante de 750 ms por configuración).
- Validado que no es artefacto del lector: medida idéntica en dos salidas independientes (11000 y 12000).

## 4. Resiliencia (análisis 3) — caída + recuperación
- Se fuerza la caída de una cámara y se mide el **MTTR** (detección + restablecimiento), 100 veces.
- El mecanismo de caída y recuperación es el propio de cada despliegue (por eso son comparables):
  - **Docker**: `docker exec camN pkill -9 ffmpeg` → la restart policy del contenedor la reinicia.
  - **Local**: se mata el proceso ffmpeg → un supervisor nativo (tipo systemd Restart=always) lo
    reinicia (el nativo puro no tiene auto-recuperación; se emula el supervisor real de producción).
  - **Kubernetes**: `kubectl delete pod` → el Deployment (ReplicaSet) recrea el pod = self-healing.
  En los tres casos el proceso revive y **se reconecta** a voctocore, mismo camino de recuperación.

## 5. Cámaras y contenido
- **Rendimiento y resiliencia**: máster realista Big Buck Bunny 4K (CC-BY), reescalado al formato,
  con un marcador de color por cámara (cam1=rojo, cam2=verde, cam3=azul, cam4=amarillo) para
  identificarla en el mix.
- **Latencia**: cámaras de color sólido (detección de conmutación infalible; la latencia es
  independiente del contenido).
- Todas emiten con colorimetría **bt709** (voctocore la exige; sin ella rechaza la fuente).

## 6. Datos de salida
- Por cada prueba: `datos.csv` (crudo), `resumen.csv` (estadística), `datos.xlsx` (Excel),
  `run.log` y `capturas/`. Se entregan los **números en CSV/Excel** para que podáis generar
  vuestras propias tablas y figuras.

---

## Resumen de resultados hasta ahora (Docker + Local completos; K8s en curso)
- CPU/RAM escala con nº de cámaras y con la resolución; Docker usa más RAM que Local (sobrecarga
  de contenedores).
- Latencia de conmutación depende del framerate (~290 ms a 25 fps, ~190 ms a 50 fps), no de la
  resolución.
- MTTR de recuperación ~1,2–1,9 s, estable entre escenarios.
- Dos puntos en estudio (honestidad): la CPU a 4 cámaras satura y a 4K/50fps parece descartar
  frames (a confirmar con ffprobe), y en Docker a 4K la RAM crece con el tiempo (posible leak,
  a caracterizar con la sostenida de 24 h).
