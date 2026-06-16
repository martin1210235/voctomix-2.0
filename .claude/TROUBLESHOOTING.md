# TROUBLESHOOTING.md — Problemas Conocidos y Soluciones

Soluciones rápidas para problemas recurrentes en Voctomix 2.0.

---

## GStreamer y Dependencias

### Error: "ModuleNotFoundError: No module named 'gi'"

**Síntomas:** Al ejecutar `voctocore.py` o `voctogui.py`:
```
ModuleNotFoundError: No module named 'gi'
```

**Causa:** GObject Introspection no instalado.

**Solución:**
```bash
sudo apt install python3-gi python3-gi-cairo python3-scipy python3-numpy
```

---

### Error: "Namespace Gst not available"

**Síntomas:**
```
gi.repository.GError: Namespace Gst not available
```

**Causa:** GStreamer 1.0 no instalado o sus bindings no disponibles.

**Solución:**
```bash
sudo apt install gir1.2-gstreamer-1.0 gir1.2-gst-plugins-base-1.0
```

**Adicional:** Verificar que GStreamer funciona:
```bash
gst-launch-1.0 --version
```

---

### Error: "No element named 'videomixer'"

**Síntomas:** voctocore arranca pero el pipeline no se construye:
```
No element named 'videomixer'
```

**Causa:** Plugins GStreamer faltantes.

**Solución:**
```bash
sudo apt install gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
  gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav
```

---

### Error: "No Xlib or GDK display"

**Síntomas:** Tests en voctocore fallan con este error.

**Causa:** Los tests necesitan mock GI bindings (no hay display real).

**Solución:**
```bash
cd voctocore
./voctocore/tests/helper/fake-gi.sh
./test.sh
```

O manualmente:
```bash
PYTHONPATH="tests/helper:$PYTHONPATH" python3 -m unittest discover -s tests -p 'test_*.py'
```

---

## Puertos y Red

### Error: "Address already in use" en puerto 9999

**Síntomas:**
```
OSError: [Errno 98] Address already in use
```
O al ejecutar `start_studio_single_pc.sh`: "port occupied".

**Causa:** Instancia anterior de voctocore sigue corriendo.

**Solución:**

```bash
# Opción 1: Matar procesos existentes
killall voctogui voctocore

# Opción 2: Ver qué está usando el puerto
lsof -i :9999

# Opción 3: Esperar 30 segundos (TIME_WAIT del kernel)
sleep 30
./start_studio_single_pc.sh
```

---

### Error: "Connection refused" en voctogui

**Síntomas:** voctogui abre pero no se conecta a voctocore:
```
ConnectionRefusedError: [Errno 111] Connection refused
```

**Causa:** voctocore no está corriendo o no escucha en 9999.

**Solución:**

```bash
# Verificar que voctocore está corriendo
ps aux | grep voctocore

# Si no está, iniciar:
./voctocore/voctocore.py &

# Esperar a que esté listo (5-10 segundos):
sleep 5

# Luego iniciar voctogui:
./voctogui/voctogui.py
```

---

### Error: "Network is unreachable" en Escenario 2 (2 PCs)

**Síntomas:** PC2 no puede conectar a PC1 (voctocore):
```
Network is unreachable
```

**Causa:** Variable `IP_SERVER` no configurada o IP incorrecta.

**Solución:**

```bash
# En PC1, obtén tu IP:
hostname -I
# ej: 192.168.1.100

# En PC2:
IP_SERVER=192.168.1.100 ./2pc_escenario2/start_voctogui_pc2.sh

# Verificar conectividad:
ping 192.168.1.100
```

---

## Docker

### Error: "Cannot connect to Docker daemon"

**Síntomas:**
```
Cannot connect to Docker daemon at unix:///var/run/docker.sock
```

**Causa:** Docker no está corriendo o el usuario no tiene permisos.

**Solución:**

```bash
# Iniciar Docker
sudo systemctl start docker

# O (para Mac/Windows):
# Abre Docker Desktop

# Dar permisos al usuario actual:
sudo usermod -aG docker $USER
newgrp docker
```

---

### Error: "X11 display not found" en Docker

**Síntomas:** `launch_docker_studio.sh` falla:
```
Error: Can't open display
```

**Causa:** X11 no está disponible para Docker.

**Solución:**

```bash
# Permitir conexiones X11 locales (ANTES de ./launch_docker_studio.sh):
xhost +local:$(id -un)

# Luego:
./launch_docker_studio.sh
```

**Nota:** En algunos sistemas, necesitas también:
```bash
export DISPLAY=:0
xhost +local:
```

---

### Error: "Health check failed" en docker-compose

**Síntomas:**
```
Container is unhealthy
```

**Causa:** Un servicio no pasa el health check (típicamente voctocore no escucha en 9999).

**Solución:**

```bash
# Ver logs del servicio fallido:
docker compose logs voctocore

# Ver el estado detallado:
docker compose ps

# Esperar más tiempo (algunos sistemas son lentos):
docker compose up -d

# Esperar 30 segundos y verificar:
sleep 30
docker compose ps

# Si sigue fallando, rehacer:
docker compose down
docker compose up -d --force-recreate
```

---

### Error: "bind: address already in use" en docker-compose

**Síntomas:**
```
Error response from daemon: driver failed programming external connectivity
```

**Causa:** Un puerto ya está en uso por otro proceso o contenedor anterior.

**Solución:**

```bash
# Listar contenedores activos:
docker ps -a

# Detener contenedores anteriores:
docker compose down

# Matar procesos que usen los puertos:
sudo lsof -i :9999
sudo lsof -i :8080
sudo lsof -i :5672

# Luego reintentar:
./launch_docker_studio.sh
```

---

## voctocore

### voctocore inicia pero no acepta conexiones

**Síntomas:** `voctocore.py` se ejecuta pero `voctogui` no puede conectar, o error "Connection refused" inmediato.

**Causa:** El pipeline GStreamer no inicializó correctamente.

**Solución:**

```bash
# Ejecutar voctocore con debug:
GST_DEBUG=2 ./voctocore/voctocore.py 2>&1 | head -100

# Buscar errores de pipeline (missing elements, bad links)

# Verificar archivo de configuración:
cat voctocore/default-config.ini

# Si hay errors de "missing element", instalar plugins (ver GStreamer section arriba)
```

---

### voctocore corre lentamente o pixela

**Síntomas:** Poca fluidez, lag en cambios de fuente.

**Causa:** 
- PC insuficientemente potente
- Plugins GStreamer no optimizados (CPU-bound en vez de GPU-accelerated)
- Demasiadas fuentes/overlays simultáneamente

**Solución:**

```bash
# Reducir complejidad:
# 1. Deshabilitar overlays innecesarios
# 2. Reducir número de previews activos (en config)
# 3. Cambiar a format más simple (RGB24 vs UYVY)

# Monitorizar CPU/RAM:
top  # o htop

# En Docker, asignar más recursos:
# (Editar docker-compose.yml)
#   resources:
#     limits:
#       cpus: '2'
#       memory: 4G
```

---

### Error: "Pad link failure" en voctocore

**Síntomas:**
```
Pad link failure between elements in pipeline
```

**Causa:** Incompatibilidad de formatos entre elementos consecutivos.

**Solución:**

```bash
# Verificar formatos en default-config.ini:
cat voctocore/default-config.ini | grep -A5 "capabilities"

# Asegurar que:
# - Video caps: UYVY 1920x1080 @ 25fps
# - Audio caps: 48000 Hz, S16LE, 2 canales (estéreo)

# Ejecutar con debug:
GST_DEBUG=4 ./voctocore/voctocore.py 2>&1 | grep -i "pad\|caps\|link"
```

---

## voctogui

### voctogui no muestra previews

**Síntomas:** Interface abre pero las 6 camaritas están negras/grises.

**Causa:** 
- voctocore no está corriendo
- Puertos 14000-14005 no activos
- Problema de red entre voctocore y voctogui

**Solución:**

```bash
# Verificar que voctocore corre:
ps aux | grep voctocore

# Verificar puertos:
netstat -tln | grep 1400
# Debería ver: 14000, 14001, 14002, ..., 14005

# Reconectar GUI:
# (Cerrar y reabrir voctogui)

# En Docker, verificar red:
docker network ls
docker inspect voctomix_net | grep "Containers" -A 50
```

---

### Overlays no aparecen en pantalla

**Síntomas:** El botón de overlay se marca pero el PNG no se ve en la mezcla.

**Causa:**
- Archivo PNG no existe o ruta incorrecta
- Overlay deshabilitado en config
- Formato PNG incorrecto (no RGBA, transparencia corrupta)

**Solución:**

```bash
# Verificar que la imagen existe:
ls -la images/overlay.png

# Si no existe, crear uno:
# (Usar GIMP o ImageMagick)
convert -size 1920x1080 xc:transparent overlay.png

# Verificar formato:
file images/overlay.png
# Debería ser: PNG image data, 1920 x 1080, 8-bit/color RGBA, non-interlaced

# Recargar config en voctocore:
# (Reiniciar voctocore + voctogui)
```

---

### Rotulación dinámica (lower-thirds) no funciona

**Síntomas:** Escribo texto en el formulario pero no aparece en el stream.

**Causa:**
- Elemento `textoverlay` no en pipeline
- Fuente incorrecta (revisar que sea mono-espacio)
- Configuración de tamaño/color incorrecta

**Solución:**

```bash
# Verificar que el pipeline incluye textoverlay:
grep -r "textoverlay" voctocore/lib/

# Verificar default-config.ini:
grep "text\|overlay" voctocore/default-config.ini

# Si faltan, añadir manualmente

# Probar con texto simple (sin caracteres especiales):
# (En voctogui toolbar → overlay text box)

# Reiniciar:
./voctocore/voctocore.py &
./voctogui/voctogui.py
```

---

## Audio

### Sin audio o audio silenciado

**Síntomas:** Stream corre pero sin sonido.

**Causa:**
- Fuente de audio no conectada
- Volumen mute en mixer
- Formato de audio incompatible

**Solución:**

```bash
# Verificar que hay audio en el sistema:
pactl list sources | grep -i pulseaudio

# Comprueba que Audio Follows Video está activo:
grep -i "audiomix\|afv" voctocore/default-config.ini

# Si mute, cambiar en voctogui:
# (Toolbar → Audio sliders)

# Verificar formato de audio en entrada (48 kHz, 2 ch, S16LE):
cat voctocore/default-config.ini | grep -i "audio"
```

---

### Audio desfasado con vídeo

**Síntomas:** Sonido llega antes o después que la imagen.

**Causa:** Diferencias en buffers de audio vs video en la pipeline.

**Solución:**

```bash
# Ajustar sync en config:
grep -i "sync\|buffer" voctocore/default-config.ini

# Si no está:
# Añadir a GStreamer elements:
#   sync=true (por defecto)

# Recompilar pipeline:
./voctocore/voctocore.py
```

---

## Telemetría y RabbitMQ

### Telemetría no se exporta a JSON

**Síntomas:** `registros/gui_state.json` no se crea o está vacío.

**Causa:**
- `gui_state_exporter.py` no iniciado
- Carpeta `registros/` no existe
- Permisos de escritura insuficientes

**Solución:**

```bash
# Crear carpeta si no existe:
mkdir -p registros
chmod 777 registros

# Verificar que voctogui inicia el exporter:
grep -n "gui_state_exporter\|GuiStateExporter" voctogui/lib/*.py

# Ejecutar manualmente:
python3 -c "from voctogui.lib.gui_state_exporter import GuiStateExporter; \
            exporter = GuiStateExporter(gui=None); exporter.run()" &
```

---

### RabbitMQ no accesible desde telemetry

**Síntomas:** Contenedor `telemetry` o servicio RabbitMQ no comunica.

**Causa:**
- RabbitMQ no está corriendo
- Puerto 5672 (AMQP) no abierto
- Credenciales incorrectas

**Solución:**

```bash
# En Docker, verificar RabbitMQ corre:
docker compose ps | grep rabbit

# Ver logs:
docker compose logs rabbitmq

# Verificar puerto:
docker compose exec voctocore nc -zv rabbitmq 5672

# Acceder al web UI:
# http://localhost:15672 (guest/guest por defecto)

# Si no funciona, reiniciar:
docker compose down
docker compose up -d rabbitmq
sleep 10
docker compose up -d
```

---

### Telemetry HTTP POST falla

**Síntomas:** Errores en logs de telemetry service:
```
Connection refused port 8080
```

**Causa:** Servicio de telemetría no escucha en 8080.

**Solución:**

```bash
# Verificar que telemetry corre:
docker compose ps | grep telemetry

# Ver logs:
docker compose logs telemetry

# Verificar puerto:
docker compose exec telemetry curl -v http://localhost:8080/health

# Si falla, revisar script telemetry_service.py:
cat example-scripts/ffmpeg/telemetry_service.py | grep -A5 "8080\|port"

# Reiniciar servicio:
docker compose restart telemetry
```

---

## Tests

### Tests fallan con "fake-gi not available"

**Síntomas:**
```
ImportError: No module named 'gi' (or GI_REPOSITORY_PATH not set)
```

**Causa:** Helper de fake-gi no está en PYTHONPATH.

**Solución:**

```bash
cd voctocore

# Opción 1: Ejecutar con script provided
./test.sh

# Opción 2: Manual
source tests/helper/fake-gi.sh
python3 -m unittest discover -s tests -p 'test_*.py'

# Opción 3: Una prueba específica
python3 -m unittest tests.commands.test_set_video_a
```

---

### Un test específico falla

**Síntomas:** `test_composites.py` falla pero otros pasan.

**Causa:** Estado incorrecto, dependencia, o bug en ese módulo.

**Solución:**

```bash
cd voctocore

# Ejecutar test con verbose:
python3 -m unittest tests.videomix.test_composites -v

# Ver traceback completo:
python3 -m unittest tests.videomix.test_composites 2>&1 | tail -50

# Ejecutar test en aislamiento (sin estado previo):
python3 -m unittest tests.videomix.test_composites.TestComposites.test_fullscreen -v
```

---

## Kubernetes

### Pod no inicia en Kubernetes

**Síntomas:** `kubectl get pods` muestra status `CrashLoopBackOff` o `Pending`.

**Causa:**
- Imagen Docker no disponible
- Recursos insuficientes
- Volumen no montado

**Solución:**

```bash
# Ver logs del pod:
kubectl logs <pod-name>

# Ver descripción detallada:
kubectl describe pod <pod-name>

# Verificar imagen:
kubectl get pod <pod-name> -o yaml | grep image

# Si imagen falta, build y push:
docker build -t voctomix:latest .
docker tag voctomix:latest localhost:5000/voctomix:latest  # si usas registry local

# En minikube, cargar imagen localmente:
minikube image build -t voctomix:latest .
```

---

### Port-forward no funciona en Kubernetes

**Síntomas:** `kubectl port-forward` no expone puertos.

**Causa:** Pod no está running o puerto incorrecto.

**Solución:**

```bash
# Verificar que el pod corre:
kubectl get pods -w

# Obtener nombre exacto del pod:
POD=$(kubectl get pods -l app=voctocore -o jsonpath="{.items[0].metadata.name}")

# Port-forward (bash):
kubectl port-forward $POD 9999:9999 8080:8080 5672:5672 &

# Verificar conexión:
nc -zv localhost 9999
```

---

## Notas para Claude Code

Este fichero es **vivo y completamente editable**. Actualízalo cuando:

- Encuentres un nuevo problema y su solución
- Un problema anterior quede obsoleto (eliminarlo)
- Cambien versiones de dependencias y las soluciones cambien
- El usuario reporte un problema recurrente

**Estilo:**
- Problema conciso + síntomas exactos + causa probable + soluciones ordenadas (simple a compleja)
- Incluir comandos exactos (copy-paste ready)
- Notas de debug con flags (GST_DEBUG, verbose, etc.)
- Links a ficheros específicos cuando sea relevante

**Actualización automática:** Si durante una sesión de trabajo detecto un problema conocido y su solución, lo añadiré aquí automáticamente.
