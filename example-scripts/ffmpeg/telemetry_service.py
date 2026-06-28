#!/usr/bin/env python3
import socket
import json
import os
import time
import threading
from datetime import datetime
from copy import deepcopy
from http.server import BaseHTTPRequestHandler, HTTPServer

# Optional RabbitMQ support: if pika is not installed the service continues
# working in local/HTTP mode without publishing to the broker.
try:
    import pika
    PIKA_AVAILABLE = True
except ImportError:
    PIKA_AVAILABLE = False


def get_lan_ip():
    """Returns the local LAN IP address.

    In Docker, reads the HOST_IP environment variable set in the compose file.
    In native mode (1PC / 2PC), auto-discovers the outgoing interface IP.
    """
    ip_docker = os.environ.get("HOST_IP")
    if ip_docker:
        return ip_docker

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


LOCAL_IP = get_lan_ip()

# In Docker with a separate network, override with: VOCTOCORE_HOST=voctocore
HOST = os.environ.get("VOCTOCORE_HOST", "127.0.0.1")
PORT = int(os.environ.get("VOCTOCORE_PORT", "9999"))
HTTP_PORT = int(os.environ.get("TELEMETRY_HTTP_PORT", "8080"))
USE_NETWORK = os.environ.get("TELEMETRY_USE_UDP") == "1"

STATE_SECONDS = 5
POLL_SECONDS = 1.0

# --- RABBITMQ CONFIGURATION ---
RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.environ.get("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.environ.get("RABBITMQ_USER", "voctomix")
RABBITMQ_PASS = os.environ.get("RABBITMQ_PASS", "voctomix123")
# Fanout exchange: every subscribed consumer receives all events
RABBITMQ_EXCHANGE = "voctomix_events"
USE_RABBITMQ = PIKA_AVAILABLE and os.environ.get("RABBITMQ_HOST") is not None

BASE_DIR = os.environ.get("VOCTOMIX_BASE_DIR", "/opt/voctomix")
if not os.path.exists(BASE_DIR):
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
SESSIONS_DIR = os.path.join(BASE_DIR, "sessions")
GUI_STATE_PATH = os.path.join(SESSIONS_DIR, "gui_state.json")

os.makedirs(SESSIONS_DIR, exist_ok=True)

if not USE_NETWORK:
    try:
        if os.path.exists(GUI_STATE_PATH):
            os.remove(GUI_STATE_PATH)
    except Exception:
        pass

# SAVE_LOGS: set to "false" in docker-compose to disable session file writing
SAVE_LOGS = os.environ.get("SAVE_LOGS", "true").strip().lower() not in ("false", "0", "no")

session_index = 1
while os.path.exists(os.path.join(SESSIONS_DIR, f"session{session_index}.jsonl")):
    session_index += 1

log_file_path = os.path.join(SESSIONS_DIR, f"session{session_index}.jsonl")

remote_gui_state = {}

START_TIME = time.time()
last_cpu_idle = 0
last_cpu_total = 0

state = {
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
        "break_db": "N/A",
        "intro_db": "N/A"
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
        "core_ip": LOCAL_IP,
        "gui_local_ip": LOCAL_IP if not USE_NETWORK else "unknown"
    }
}

lock = threading.Lock()

# --- RABBITMQ PUBLISHER ---
# Maintains a persistent connection to the broker.
# If the connection drops, it attempts to reconnect without blocking the rest of the system.
_rabbit_conn = None
_rabbit_channel = None
_rabbit_lock = threading.Lock()


def _connect_rabbit():
    """Creates (or recreates) the connection and channel to RabbitMQ."""
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
    # Fanout exchange: all subscribed consumers receive every message
    _rabbit_channel.exchange_declare(
        exchange=RABBITMQ_EXCHANGE,
        exchange_type='fanout',
        durable=True
    )


def publish_to_rabbit(payload: dict):
    """Publishes a state or change event to the RabbitMQ exchange.

    Attempts to reconnect once if the connection is down. If it fails again,
    the error is silently ignored so the telemetry service continues with JSONL/HTTP.
    """
    if not USE_RABBITMQ:
        return
    global _rabbit_conn, _rabbit_channel
    body = json.dumps(payload, ensure_ascii=False)
    with _rabbit_lock:
        for attempt in range(2):
            try:
                if _rabbit_conn is None or _rabbit_conn.is_closed:
                    _connect_rabbit()
                _rabbit_channel.basic_publish(
                    exchange=RABBITMQ_EXCHANGE,
                    routing_key='',
                    body=body,
                    properties=pika.BasicProperties(
                        content_type='application/json',
                        delivery_mode=1  # non-persistent: speed over durability in live production
                    )
                )
                return
            except Exception:
                _rabbit_conn = None
                if attempt == 0:
                    time.sleep(1)


def _start_rabbit_bg():
    """Connects to RabbitMQ in a background thread without blocking startup."""
    if not USE_RABBITMQ:
        return
    for attempt in range(10):
        try:
            with _rabbit_lock:
                _connect_rabbit()
            print(f"[RabbitMQ] Connected to {RABBITMQ_HOST}:{RABBITMQ_PORT} "
                  f"— exchange '{RABBITMQ_EXCHANGE}'")
            return
        except Exception as e:
            print(f"[RabbitMQ] Attempt {attempt+1}/10 failed: {e}")
            time.sleep(5)
    print("[RabbitMQ] Could not connect. Continuing without AMQP event publishing.")


def current_time_str():
    return datetime.now().strftime("%H:%M:%S")


def current_timestamp_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# --- SYSTEM HEALTH ---
def update_system_health():
    global last_cpu_idle, last_cpu_total
    with lock:
        session_seconds = int(time.time() - START_TIME)
        state["system_health"]["session_duration"] = time.strftime('%H:%M:%S', time.gmtime(session_seconds))

        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
                state["system_health"]["uptime"] = time.strftime('%H:%M:%S', time.gmtime(uptime_seconds))
        except Exception:
            pass

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
                state["system_health"]["ram_available_mb"] = mem_available // 1024
                state["system_health"]["ram_usage_percent"] = round(100.0 * (mem_total - mem_available) / mem_total, 1)
        except Exception:
            pass

        try:
            with open('/proc/stat', 'r') as f:
                cpu_line = f.readline()
            parts = [float(column) for column in cpu_line.strip().split()[1:]]
            idle, total = parts[3], sum(parts)
            idle_delta = idle - last_cpu_idle
            total_delta = total - last_cpu_total
            last_cpu_idle, last_cpu_total = idle, total
            if total_delta > 0:
                state["system_health"]["cpu_usage_percent"] = round(100.0 * (1.0 - idle_delta / total_delta), 1)
        except Exception:
            pass


# --- EMBEDDED HTTP SERVER ---
class GuiStateHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        global remote_gui_state
        if self.path == '/gui_state':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                received_state = json.loads(post_data.decode('utf-8'))

                with lock:
                    remote_gui_state = received_state

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
        pass


def listen_http_gui():
    server_address = ('0.0.0.0', HTTP_PORT)
    HTTPServer.allow_reuse_address = True
    httpd = HTTPServer(server_address, GuiStateHTTPRequestHandler)
    httpd.serve_forever()


def load_gui_state_file():
    if not os.path.exists(GUI_STATE_PATH):
        return None
    try:
        with open(GUI_STATE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def is_valid_channel(value):
    return value not in (None, "", "unknown", "none")


def is_valid_text(value):
    return value not in (None, "", "unknown")


def merge_gui_state():
    if USE_NETWORK:
        with lock:
            gui = deepcopy(remote_gui_state)
    else:
        gui = load_gui_state_file()

    if not gui:
        return

    with lock:
        preview = gui.get("preview", {})
        if is_valid_channel(preview.get("channel_a")):
            state["preview"]["channel_a"] = preview.get("channel_a")
        if is_valid_channel(preview.get("channel_b")):
            state["preview"]["channel_b"] = preview.get("channel_b")

        mode = gui.get("mode")
        if mode in ("live", "pause", "nostream"):
            state["mode"] = mode

        composite = gui.get("composite", {})
        gui_name = composite.get("name", "unknown")
        if gui_name in ("full_screen", "side_by_side", "picture_in_picture", "lecture"):
            state["composite"]["name"] = gui_name
            state["composite"]["fullscreen"] = (gui_name == "full_screen")
            state["composite"]["side_by_side"] = (gui_name == "side_by_side")
            state["composite"]["pip"] = (gui_name == "picture_in_picture")
            state["composite"]["lecture"] = (gui_name == "lecture")

        if isinstance(gui.get("mirror"), bool):
            state["mirror"] = gui["mirror"]

        insertion = gui.get("insertion", {})
        if "overlay" in insertion:
            state["insertion"]["overlay"] = bool(insertion.get("overlay", False))
        if "auto_off" in insertion:
            state["insertion"]["auto_off"] = bool(insertion.get("auto_off", False))

        overlay_selected = insertion.get("overlay_selected")
        if is_valid_text(overlay_selected):
            state["insertion"]["overlay_selected"] = overlay_selected

        for key in ("logo1", "logo2", "text1_active", "text2_active"):
            if key in insertion:
                state["insertion"][key] = bool(insertion.get(key, False))

        for key in ("text1_value", "text2_value"):
            if key in insertion:
                state["insertion"][key] = insertion.get(key, "")

        audio = gui.get("audio", {})
        for key in ("cam1_db", "cam2_db", "cam3_db", "cam4_db", "break_db", "intro_db"):
            if key in audio:
                state["audio"][key] = audio[key]

        gui_ip = gui.get("gui_ip")
        if gui_ip:
            state["network"]["gui_local_ip"] = gui_ip


def save_event(event_type="state"):
    merge_gui_state()
    with lock:
        payload = deepcopy(state)
        payload["timestamp"] = current_timestamp_str()
        payload["type"] = event_type

    publish_to_rabbit(payload)

    if SAVE_LOGS:
        try:
            with open(log_file_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(payload, ensure_ascii=False) + "\n")
        except Exception:
            pass


def print_state(prefix="STATE"):
    merge_gui_state()
    with lock:
        health = state["system_health"]
        sources = state["sources"]
        cam_status = " ".join(
            f"{s}{'✓' if v else '✗'}"
            for s, v in sources.items()
            if s.startswith("cam")
        )
        summary = (
            f"CPU: {health['cpu_usage_percent']:5.1f}%  "
            f"RAM: {health['ram_usage_percent']:5.1f}%  "
            f"uptime: {health['uptime']}  "
            f"session: {health['session_duration']}  "
            f"[{cam_status}]"
        )
        info = (
            f'"preview": {json.dumps(state["preview"], ensure_ascii=False)}, '
            f'"output": {json.dumps(state["output"], ensure_ascii=False)}, '
            f'"mode": {json.dumps(state["mode"], ensure_ascii=False)}, '
            f'"composite": {json.dumps(state["composite"], ensure_ascii=False)}, '
            f'"mirror": {json.dumps(state["mirror"], ensure_ascii=False)}, '
            f'"insertion": {json.dumps(state["insertion"], ensure_ascii=False)}, '
            f'"audio": {json.dumps(state["audio"], ensure_ascii=False)}, '
            f'"sources": {json.dumps(state["sources"], ensure_ascii=False)}, '
            f'"stream_info": {json.dumps(state["stream_info"], ensure_ascii=False)}, '
            f'"system_health": {json.dumps(state["system_health"], ensure_ascii=False)}, '
            f'"network": {json.dumps(state["network"], ensure_ascii=False)}'
        )
    print(f"[{current_time_str()}] {prefix}  {summary}", flush=True)
    print(f"           full → {{{info}}}", flush=True)
    print(flush=True)


def set_mode(name):
    name = str(name).strip().lower()
    if name == "blank":
        state["mode"] = "pause"
    elif name in ("live", "pause", "nostream"):
        state["mode"] = name
    else:
        state["mode"] = "unknown"


def update_composite_from_code(code):
    code = str(code).strip().lower()
    cleaned = code.replace("^", "").replace("|", "")

    if cleaned.startswith("fs"):
        name = "full_screen"
    elif "sbs" in cleaned:
        name = "side_by_side"
    elif "pip" in cleaned:
        name = "picture_in_picture"
    elif "lec" in cleaned:
        name = "lecture"
    else:
        name = "unknown"

    state["composite"]["name"] = name
    state["composite"]["fullscreen"] = (name == "full_screen")
    state["composite"]["side_by_side"] = (name == "side_by_side")
    state["composite"]["pip"] = (name == "picture_in_picture")
    state["composite"]["lecture"] = (name == "lecture")
    state["mirror"] = ("|" in code)


def notify_if_changed(previous_state):
    with lock:
        current = deepcopy(state)

    if previous_state != current:
        print_state("CHANGE")
        save_event("change")


def send_state_queries(sock):
    try:
        sock.sendall(b"get_video\n")
        sock.sendall(b"get_stream_status\n")
        sock.sendall(b"get_composite_mode\n")
        sock.sendall(b"get_overlay_visible\n")
        sock.sendall(b"get_audio\n")
        sock.sendall(b"get_sources_status\n")
    except Exception:
        raise


def process_line(line):
    parts = line.split(" ")
    command = parts[0]

    with lock:
        previous_state = deepcopy(state)

        if command == "server_config":
            try:
                json_str = line.split(" ", 1)[1]
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
                            state["stream_info"]["video_fps"] = fps
                        elif chunk.startswith("format="):
                            state["stream_info"]["video_pix_fmt"] = chunk.split("=")[1]
                    if 'w' in locals() and 'h' in locals():
                        state["stream_info"]["video_resolution"] = f"{w}x{h}"

                        if 'fps' in locals():
                            mbps = round((int(w) * int(h) * int(fps) * 1.5 * 8) / 1000000.0, 2)
                            state["stream_info"]["calc_bandwidth_mbps_per_cam"] = mbps

                acaps = mix_config.get("audiocaps", "")
                if acaps:
                    for chunk in acaps.split(","):
                        if chunk.startswith("rate="):
                            state["stream_info"]["audio_sample_rate"] = chunk.split("=")[1]
                        elif chunk.startswith("channels="):
                            state["stream_info"]["audio_channels"] = chunk.split("=")[1]
                        elif chunk.startswith("format="):
                            state["stream_info"]["audio_fmt"] = chunk.split("=")[1]
            except Exception:
                pass

        elif command == "video_status" and len(parts) >= 3:
            state["output"]["channel_a"] = parts[1]
            state["output"]["channel_b"] = parts[2]

        elif command in ("composite", "composite_mode") and len(parts) >= 2:
            code = parts[1].split("(")[0]
            update_composite_from_code(code)

        elif command == "stream_status" and len(parts) >= 2:
            set_mode(parts[1])

        elif command == "overlay_status" and len(parts) >= 2:
            value = parts[1].lower()
            state["insertion"]["overlay"] = value in ("true", "1", "on", "visible")

        elif command == "audio_status" and len(parts) >= 2:
            try:
                import math
                json_str = line.split(" ", 1)[1]
                volumes = json.loads(json_str)
                for src, linear_vol in volumes.items():
                    key = f"{src}_db"
                    if key in state["audio"]:
                        # Convert linear volume to dB; floor at -60 dB
                        db = round(20 * math.log10(max(float(linear_vol), 1e-3)), 1)
                        state["audio"][key] = db
            except Exception:
                pass

        elif command == "sources_status" and len(parts) >= 2:
            try:
                json_str = line.split(" ", 1)[1]
                connections = json.loads(json_str)
                for name, connected in connections.items():
                    if name in state["sources"]:
                        state["sources"][name] = bool(connected)
            except Exception:
                pass

    notify_if_changed(previous_state)


def listen_voctocore():
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.0)
            s.connect((HOST, PORT))

            try:
                s.sendall(b"get_config\n")
            except Exception:
                pass

            send_state_queries(s)
            last_poll = time.time()
            buffer = ""

            while True:
                now = time.time()
                if now - last_poll >= POLL_SECONDS:
                    send_state_queries(s)
                    last_poll = now

                try:
                    data = s.recv(4096)
                    if not data:
                        raise ConnectionError("Connection closed by voctocore")

                    buffer += data.decode("utf-8", errors="replace")

                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        line = line.strip()
                        if line:
                            process_line(line)

                except socket.timeout:
                    continue

        except Exception:
            time.sleep(1)


def state_loop():
    while True:
        time.sleep(STATE_SECONDS)
        update_system_health()
        print_state("STATE")
        save_event("state")


print("\n" + "=" * 85)
mode_text = "Network/Docker (HTTP)" if USE_NETWORK else "Local (disk)"
rabbit_text = f"yes ({RABBITMQ_HOST}:{RABBITMQ_PORT})" if USE_RABBITMQ else "no (RABBITMQ_HOST not set)"
print(f"TELEMETRY SERVICE ACTIVE - Mode: {mode_text}")
print(f"RabbitMQ: {rabbit_text}")
if SAVE_LOGS:
    print(f"Saving JSON to: session{session_index}.jsonl")
else:
    print("SAVE_LOGS=false — session log file disabled")
print("=" * 85 + "\n")

if USE_NETWORK:
    threading.Thread(target=listen_http_gui, daemon=True).start()

if USE_RABBITMQ:
    threading.Thread(target=_start_rabbit_bg, daemon=True).start()

threading.Thread(target=listen_voctocore, daemon=True).start()
threading.Thread(target=state_loop, daemon=True).start()

while True:
    time.sleep(1)
