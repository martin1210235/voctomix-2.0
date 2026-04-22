#!/usr/bin/env python3
import socket
import json
import os
import time
import threading
from datetime import datetime
from copy import deepcopy
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- RABBITMQ (importación opcional: si pika no está instalado, el notario
#     sigue funcionando en modo local/HTTP sin publicar en RabbitMQ) ---
try:
    import pika
    PIKA_DISPONIBLE = True
except ImportError:
    PIKA_DISPONIBLE = False

# --- Descubrir la IP local de la máquina (Modo Híbrido: Docker / Nativo) ---
def obtener_ip_lan():
    """Detecta la IP automáticamente en nativo o usa la manual en Docker"""
    # 1. Prioridad: Si estamos en Docker y configuramos MI_IP_REAL en el compose, la usamos
    ip_docker = os.environ.get("MI_IP_REAL")
    if ip_docker:
        return ip_docker

    # 2. Si no hay variable (Escenarios nativos de 1 PC o 2 PCs), autodescubrimiento por socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # No necesita conexión real, solo ver qué interfaz usaría el sistema para salir
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        # 3. Último recurso si no hay red activa
        return "127.0.0.1"

IP_REAL_CEREBRO = obtener_ip_lan()
# ---------------------------------------------------------------------------

# --- MODO UNIVERSAL (HTTP) ---
# En Docker con red separada, sobreescribir con: VOCTOCORE_HOST=voctocore
HOST = os.environ.get("VOCTOCORE_HOST", "127.0.0.1")
PORT = 9999
HTTP_PORT = 8080  # Cambiado a HTTP
USE_NETWORK = os.environ.get("NOTARIO_USE_UDP") == "1"

STATE_SECONDS = 5
POLL_SECONDS = 1.0

# --- CONFIGURACIÓN RABBITMQ ---
RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.environ.get("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.environ.get("RABBITMQ_USER", "voctomix")
RABBITMQ_PASS = os.environ.get("RABBITMQ_PASS", "voctomix123")
# Exchange fanout: cualquier consumidor suscrito recibe todos los eventos
RABBITMQ_EXCHANGE = "voctomix_events"
USE_RABBITMQ = PIKA_DISPONIBLE and os.environ.get("RABBITMQ_HOST") is not None

BASE_DIR = "/opt/voctomix"
if not os.path.exists(BASE_DIR):
    # Fallback por si lo ejecutas fuera de Docker
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
REGISTROS_DIR = os.path.join(BASE_DIR, "registros")
GUI_STATE_PATH = os.path.join(REGISTROS_DIR, "gui_state.json")

os.makedirs(REGISTROS_DIR, exist_ok=True)

if not USE_NETWORK:
    try:
        if os.path.exists(GUI_STATE_PATH):
            os.remove(GUI_STATE_PATH)
    except Exception:
        pass

numero = 1
while os.path.exists(os.path.join(REGISTROS_DIR, f"registro{numero}.jsonl")):
    numero += 1

log_file_path = os.path.join(REGISTROS_DIR, f"registro{numero}.jsonl")

# Memoria para HTTP
estado_gui_remoto = {}

# Tiempos para cálculos de Salud del Sistema
START_TIME = time.time()
last_cpu_idle = 0
last_cpu_total = 0

estado = {
    "preview": {
        "channel_a": "none",
        "channel_b": "none"
    },
    "output": {
        "channel_a": "none",
        "channel_b": "none"
    },
    "mode": "unknown",
    "composite": {
        "name": "unknown",
        "fullscreen": True,
        "side_by_side": False,
        "pip": False,
        "lecture": False
    },
    "mirror": False,
    "insertion": {
        "overlay": False,
        "auto_off": False,
        "overlay_selected": "unknown",
        "logo1": False,
        "logo2": False,
        "text1_active": False,
        "text1_value": "",
        "text2_active": False,
        "text2_value": ""
    },
    "audio": {
        "cam1_db": None,
        "cam2_db": None,
        "cam3_db": None,
        "cam4_db": None,
        "break_db": "N/A",  # fuente solo-vídeo, sin audio en voctocore
        "intro_db": "N/A"   # fuente solo-vídeo, sin audio en voctocore
    },
    "sources": {
        "cam1": False,
        "cam2": False,
        "cam3": False,
        "cam4": False,
        "break": False,
        "intro": False
    },
    "stream_info": {
        "video_resolution": "unknown",
        "video_fps": "unknown",
        "video_codec": "rawvideo",
        "video_pix_fmt": "unknown",
        "calc_bandwidth_mbps_per_cam": 0.0,
        "audio_sample_rate": "unknown",
        "audio_channels": "unknown",
        "audio_fmt": "unknown"
    },
    "system_health": {
        "cpu_usage_percent": 0.0,
        "ram_usage_percent": 0.0,
        "ram_available_mb": 0,
        "uptime": "00:00:00",
        "session_duration": "00:00:00"
    },
    "network": {
        "core_ip": IP_REAL_CEREBRO,
        "gui_local_ip": IP_REAL_CEREBRO if not USE_NETWORK else "unknown"
    }
}

lock = threading.Lock()

# --- PUBLICADOR RABBITMQ ---
# Mantiene una conexión persistente al broker.
# Si se cae, intenta reconectar sin bloquear el resto del sistema.
_rabbit_conn = None
_rabbit_channel = None
_rabbit_lock = threading.Lock()

def _conectar_rabbit():
    """Crea (o recrea) la conexión y el channel a RabbitMQ."""
    global _rabbit_conn, _rabbit_channel
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    params = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        credentials=credentials,
        connection_attempts=3,
        retry_delay=2,
        heartbeat=60,
        blocked_connection_timeout=10
    )
    _rabbit_conn = pika.BlockingConnection(params)
    _rabbit_channel = _rabbit_conn.channel()
    # Exchange tipo fanout: todos los consumers suscritos reciben cada mensaje
    _rabbit_channel.exchange_declare(
        exchange=RABBITMQ_EXCHANGE,
        exchange_type='fanout',
        durable=True  # sobrevive reinicios del broker
    )

def publicar_en_rabbit(payload: dict):
    """
    Publica un evento de estado/cambio en el exchange de RabbitMQ.
    Si la conexión está caída, intenta reconectar una vez. Si falla,
    lo ignora y el notario sigue funcionando con JSON/HTTP normalmente.
    """
    if not USE_RABBITMQ:
        return
    global _rabbit_conn, _rabbit_channel
    body = json.dumps(payload, ensure_ascii=False)
    with _rabbit_lock:
        for intento in range(2):
            try:
                if _rabbit_conn is None or _rabbit_conn.is_closed:
                    _conectar_rabbit()
                _rabbit_channel.basic_publish(
                    exchange=RABBITMQ_EXCHANGE,
                    routing_key='',   # fanout ignora routing_key
                    body=body,
                    properties=pika.BasicProperties(
                        content_type='application/json',
                        delivery_mode=1  # no persistente (velocidad > durabilidad en live)
                    )
                )
                return  # éxito
            except Exception:
                _rabbit_conn = None   # fuerza reconexión en siguiente intento
                if intento == 0:
                    time.sleep(1)

def _iniciar_rabbit_bg():
    """Intenta conectar a RabbitMQ en background sin bloquear el arranque."""
    if not USE_RABBITMQ:
        return
    for intento in range(10):
        try:
            with _rabbit_lock:
                _conectar_rabbit()
            print(f"[RabbitMQ] ✅ Conectado a {RABBITMQ_HOST}:{RABBITMQ_PORT} "
                  f"— exchange '{RABBITMQ_EXCHANGE}'")
            return
        except Exception as e:
            print(f"[RabbitMQ] ⏳ Intento {intento+1}/10 fallido: {e}")
            time.sleep(5)
    print("[RabbitMQ] ⚠️  No se pudo conectar. Continuando sin publicar eventos AMQP.")
# -----------------------------------

def ahora_hora():
    return datetime.now().strftime("%H:%M:%S")

def ahora_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# --- FUNCIONES DE SALUD DEL SISTEMA ---
def actualizar_salud_sistema():
    global last_cpu_idle, last_cpu_total
    with lock:
        # Duración de sesión
        session_seconds = int(time.time() - START_TIME)
        estado["system_health"]["session_duration"] = time.strftime('%H:%M:%S', time.gmtime(session_seconds))

        # Uptime del PC
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
                estado["system_health"]["uptime"] = time.strftime('%H:%M:%S', time.gmtime(uptime_seconds))
        except:
            pass

        # RAM
        try:
            with open('/proc/meminfo', 'r') as f:
                lines = f.readlines()
            mem_total = 0
            mem_available = 0
            for line in lines:
                if line.startswith('MemTotal:'):
                    mem_total = int(line.split()[1])
                elif line.startswith('MemAvailable:'):
                    mem_available = int(line.split()[1])
            if mem_total > 0:
                estado["system_health"]["ram_available_mb"] = mem_available // 1024
                estado["system_health"]["ram_usage_percent"] = round(100.0 * (mem_total - mem_available) / mem_total, 1)
        except:
            pass

        # CPU
        try:
            with open('/proc/stat', 'r') as f:
                cpu_line = f.readline()
            parts = [float(column) for column in cpu_line.strip().split()[1:]]
            idle, total = parts[3], sum(parts)
            idle_delta = idle - last_cpu_idle
            total_delta = total - last_cpu_total
            last_cpu_idle, last_cpu_total = idle, total
            if total_delta > 0:
                estado["system_health"]["cpu_usage_percent"] = round(100.0 * (1.0 - idle_delta / total_delta), 1)
        except:
            pass
# --------------------------------------

# --- SERVIDOR HTTP INTEGRADO ---
class GuiStateHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        global estado_gui_remoto
        if self.path == '/gui_state':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                estado_recibido = json.loads(post_data.decode('utf-8'))
                
                with lock:
                    estado_gui_remoto = estado_recibido
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"status": "ok"}')
            except Exception:
                self.send_response(400)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass # Silenciamos los logs del servidor HTTP para no ensuciar la terminal

def escuchar_http_gui():
    server_address = ('0.0.0.0', HTTP_PORT)
    HTTPServer.allow_reuse_address = True 
    httpd = HTTPServer(server_address, GuiStateHTTPRequestHandler)
    httpd.serve_forever()
# -------------------------------

def cargar_gui_state_archivo():
    if not os.path.exists(GUI_STATE_PATH):
        return None
    try:
        with open(GUI_STATE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def es_valido_canal(valor):
    return valor not in (None, "", "unknown", "none", "desconocido", "ninguno")

def es_valido_texto(valor):
    return valor not in (None, "", "unknown", "desconocido")

def fusionar_gui_state():
    if USE_NETWORK:
        with lock:
            gui = deepcopy(estado_gui_remoto)
    else:
        gui = cargar_gui_state_archivo()

    if not gui:
        return

    with lock:
        preview = gui.get("preview", {})
        if es_valido_canal(preview.get("channel_a")):
            estado["preview"]["channel_a"] = preview.get("channel_a")
        if es_valido_canal(preview.get("channel_b")):
            estado["preview"]["channel_b"] = preview.get("channel_b")

        mode = gui.get("mode")
        if mode in ("live", "pause", "nostream"):
            estado["mode"] = mode

        composite = gui.get("composite", {})
        gui_name = composite.get("name", "unknown")
        if gui_name in ("full_screen", "side_by_side", "picture_in_picture", "lecture"):
            estado["composite"]["name"] = gui_name
            estado["composite"]["fullscreen"] = (gui_name == "full_screen")
            estado["composite"]["side_by_side"] = (gui_name == "side_by_side")
            estado["composite"]["pip"] = (gui_name == "picture_in_picture")
            estado["composite"]["lecture"] = (gui_name == "lecture")

        if isinstance(gui.get("mirror"), bool):
            estado["mirror"] = gui["mirror"]

        insertion = gui.get("insertion", {})
        if "overlay" in insertion:
            estado["insertion"]["overlay"] = bool(insertion.get("overlay", False))
        if "auto_off" in insertion:
            estado["insertion"]["auto_off"] = bool(insertion.get("auto_off", False))

        overlay_selected = insertion.get("overlay_selected")
        if es_valido_texto(overlay_selected):
            estado["insertion"]["overlay_selected"] = overlay_selected

        for key in ("logo1", "logo2", "text1_active", "text2_active"):
            if key in insertion:
                estado["insertion"][key] = bool(insertion.get(key, False))

        for key in ("text1_value", "text2_value"):
            if key in insertion:
                estado["insertion"][key] = insertion.get(key, "")

        audio = gui.get("audio", {})
        for key in ("cam1_db", "cam2_db", "cam3_db", "cam4_db", "break_db", "intro_db"):
            if key in audio:
                estado["audio"][key] = audio[key]
                
        gui_ip = gui.get("gui_ip")
        if gui_ip:
            estado["network"]["gui_local_ip"] = gui_ip

def guardar_evento(tipo="state"):
    fusionar_gui_state()
    with lock:
        payload = deepcopy(estado)
        payload["timestamp"] = ahora_timestamp()
        payload["type"] = tipo

    # Publicar en RabbitMQ (no bloqueante: si falla, continúa con JSONL)
    publicar_en_rabbit(payload)

    try:
        with open(log_file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        pass

def imprimir_estado(prefijo="STATE"):
    fusionar_gui_state()
    with lock:
        info = (
            f'"preview": {json.dumps(estado["preview"], ensure_ascii=False)}, '
            f'"output": {json.dumps(estado["output"], ensure_ascii=False)}, '
            f'"mode": {json.dumps(estado["mode"], ensure_ascii=False)}, '
            f'"composite": {json.dumps(estado["composite"], ensure_ascii=False)}, '
            f'"mirror": {json.dumps(estado["mirror"], ensure_ascii=False)}, '
            f'"insertion": {json.dumps(estado["insertion"], ensure_ascii=False)}, '
            f'"audio": {json.dumps(estado["audio"], ensure_ascii=False)}, '
            f'"sources": {json.dumps(estado["sources"], ensure_ascii=False)}, '
            f'"stream_info": {json.dumps(estado["stream_info"], ensure_ascii=False)}, '
            f'"system_health": {json.dumps(estado["system_health"], ensure_ascii=False)}, '
            f'"network": {json.dumps(estado["network"], ensure_ascii=False)}'
        )
    print(f"[{ahora_hora()}] {prefijo} -> {info}")

def set_mode(nombre):
    nombre = str(nombre).strip().lower()
    if nombre == "blank":
        estado["mode"] = "pause"
    elif nombre in ("live", "pause", "nostream"):
        estado["mode"] = nombre
    else:
        estado["mode"] = "unknown"

def actualizar_composite_desde_codigo(codigo):
    codigo = str(codigo).strip().lower()
    limpio = codigo.replace("^", "").replace("|", "")

    if limpio.startswith("fs"):
        name = "full_screen"
    elif "sbs" in limpio:
        name = "side_by_side"
    elif "pip" in limpio:
        name = "picture_in_picture"
    elif "lec" in limpio:
        name = "lecture"
    else:
        name = "unknown"

    estado["composite"]["name"] = name
    estado["composite"]["fullscreen"] = (name == "full_screen")
    estado["composite"]["side_by_side"] = (name == "side_by_side")
    estado["composite"]["pip"] = (name == "picture_in_picture")
    estado["composite"]["lecture"] = (name == "lecture")
    estado["mirror"] = ("|" in codigo)

def notificar_cambio_si_toca(estado_anterior):
    with lock:
        actual = deepcopy(estado)

    if estado_anterior != actual:
        imprimir_estado("CHANGE")
        guardar_evento("change")

def enviar_consultas_estado(sock):
    try:
        sock.sendall(b"get_video\n")
        sock.sendall(b"get_stream_status\n")
        sock.sendall(b"get_composite_mode\n")
        sock.sendall(b"get_overlay_visible\n")
        # Consultar volúmenes de todas las fuentes en una sola llamada
        sock.sendall(b"get_audio\n")
        sock.sendall(b"get_sources_status\n")
    except Exception:
        raise

def procesar_linea(linea):
    partes = linea.split(" ")
    comando = partes[0]

    with lock:
        estado_anterior = deepcopy(estado)

        if comando == "server_config":
            try:
                json_str = linea.split(" ", 1)[1]
                config = json.loads(json_str)
                mix_config = config.get("mix", {})
                
                vcaps = mix_config.get("videocaps", "")
                if vcaps:
                    for chunk in vcaps.split(","):
                        if chunk.startswith("width="):
                            w = chunk.split("=")[1]
                        elif chunk.startswith("height="):
                            h = chunk.split("=")[1]
                        elif chunk.startswith("framerate="):
                            fps_raw = chunk.split("=")[1]
                            fps = str(int(fps_raw.split("/")[0]) // int(fps_raw.split("/")[1])) if "/" in fps_raw else fps_raw
                            estado["stream_info"]["video_fps"] = fps
                        elif chunk.startswith("format="):
                            estado["stream_info"]["video_pix_fmt"] = chunk.split("=")[1]
                    if 'w' in locals() and 'h' in locals():
                        estado["stream_info"]["video_resolution"] = f"{w}x{h}"
                        
                        if 'fps' in locals():
                            mbps = round((int(w) * int(h) * int(fps) * 1.5 * 8) / 1000000.0, 2)
                            estado["stream_info"]["calc_bandwidth_mbps_per_cam"] = mbps

                acaps = mix_config.get("audiocaps", "")
                if acaps:
                    for chunk in acaps.split(","):
                        if chunk.startswith("rate="):
                            estado["stream_info"]["audio_sample_rate"] = chunk.split("=")[1]
                        elif chunk.startswith("channels="):
                            estado["stream_info"]["audio_channels"] = chunk.split("=")[1]
                        elif chunk.startswith("format="):
                            estado["stream_info"]["audio_fmt"] = chunk.split("=")[1]
            except Exception:
                pass

        elif comando == "video_status" and len(partes) >= 3:
            estado["output"]["channel_a"] = partes[1]
            estado["output"]["channel_b"] = partes[2]

        # voctocore responde "composite_mode fs" (no "composite")
        elif comando in ("composite", "composite_mode") and len(partes) >= 2:
            codigo = partes[1].split("(")[0]
            actualizar_composite_desde_codigo(codigo)

        elif comando == "stream_status" and len(partes) >= 2:
            set_mode(partes[1])

        elif comando == "overlay_status" and len(partes) >= 2:
            valor = partes[1].lower()
            estado["insertion"]["overlay"] = valor in ("true", "1", "on", "visible")

        # Respuesta: "audio_status {"cam1":0.85,"cam2":1.0,...}"
        elif comando == "audio_status" and len(partes) >= 2:
            try:
                import math
                json_str = linea.split(" ", 1)[1]
                volumenes = json.loads(json_str)
                for fuente, vol_lineal in volumenes.items():
                    clave = f"{fuente}_db"
                    if clave in estado["audio"]:
                        # Convertir volumen lineal a dB, mínimo -60 dB
                        db = round(20 * math.log10(max(float(vol_lineal), 1e-3)), 1)
                        estado["audio"][clave] = db
            except Exception:
                pass

        # Respuesta: "sources_status {"cam1":true,"cam2":false,...}"
        # true  = ffmpeg conectado → hay señal
        # false = puerto escuchando pero nadie conectado → sin señal
        elif comando == "sources_status" and len(partes) >= 2:
            try:
                json_str = linea.split(" ", 1)[1]
                conexiones = json.loads(json_str)
                for nombre, conectado in conexiones.items():
                    if nombre in estado["sources"]:
                        estado["sources"][nombre] = bool(conectado)
            except Exception:
                pass

    notificar_cambio_si_toca(estado_anterior)

def escuchar_voctomix():
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.0)
            s.connect((HOST, PORT))

            try:
                s.sendall(b"get_config\n")
            except Exception:
                pass

            enviar_consultas_estado(s)
            ultimo_poll = time.time()
            buffer = ""

            while True:
                ahora = time.time()
                if ahora - ultimo_poll >= POLL_SECONDS:
                    enviar_consultas_estado(s)
                    ultimo_poll = ahora

                try:
                    data = s.recv(4096)
                    if not data:
                        raise ConnectionError("Conexión cerrada por voctocore")

                    buffer += data.decode("utf-8", errors="replace")

                    while "\n" in buffer:
                        linea, buffer = buffer.split("\n", 1)
                        linea = linea.strip()
                        if linea:
                            procesar_linea(linea)

                except socket.timeout:
                    continue

        except Exception:
            time.sleep(1)

def state_loop():
    while True:
        time.sleep(STATE_SECONDS)
        actualizar_salud_sistema()
        imprimir_estado("STATE")
        guardar_evento("state")

print("\n" + "=" * 85)
modo_texto = "Red/Docker (HTTP)" if USE_NETWORK else "Local (Disco)"
rabbit_texto = f"sí ({RABBITMQ_HOST}:{RABBITMQ_PORT})" if USE_RABBITMQ else "no (RABBITMQ_HOST no configurado)"
print(f"🎙️  NOTARIO ACTIVADO - Modo: {modo_texto}")
print(f"🐇 RabbitMQ: {rabbit_texto}")
print(f"📁 Guardando JSON en: registro{numero}.jsonl")
print("=" * 85 + "\n")

if USE_NETWORK:
    threading.Thread(target=escuchar_http_gui, daemon=True).start()

# Conexión RabbitMQ en background: no bloquea el arranque si el broker tarda
if USE_RABBITMQ:
    threading.Thread(target=_iniciar_rabbit_bg, daemon=True).start()

threading.Thread(target=escuchar_voctomix, daemon=True).start()
threading.Thread(target=state_loop, daemon=True).start()

while True:
    time.sleep(1)
