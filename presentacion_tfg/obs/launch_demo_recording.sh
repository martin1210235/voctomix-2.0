#!/usr/bin/env bash
#
# Opens the three windows needed to record the demo video with OBS:
#   1. voctogui        (the control GUI)
#   2. PROGRAM :15000  (ffplay, what the audience sees)
#   3. TELEMETRY       (a terminal streaming the telemetry JSON events)
#
# OBS window-capture grabs each window on its own, so their position on the
# desktop does not matter: arrange them inside OBS, not here. Just keep them
# mapped (do not minimise them).
#
# Usage:
#   ./launch_demo_recording.sh          # Docker mode (default)
#   MODE=native ./launch_demo_recording.sh   # native single-PC mode
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MODE="${MODE:-docker}"

# Use sudo only if the daemon is not reachable as the current user.
if docker info >/dev/null 2>&1; then
    DOCKER="docker compose"
else
    DOCKER="sudo docker compose"
fi

cd "$ROOT"

# --- helper: launch a terminal with a big monospace font -------------------
open_terminal() {
    local title="$1" cmd="$2"
    if command -v xterm >/dev/null 2>&1; then
        xterm -T "$title" -fa "Monospace" -fs 16 -bg black -fg "#00ff66" \
              -geometry 100x28 -e bash -lc "$cmd; exec bash" &
    elif command -v gnome-terminal >/dev/null 2>&1; then
        gnome-terminal --title="$title" -- bash -lc "$cmd; exec bash" &
        echo "  (gnome-terminal: sube la letra con Ctrl + '+' varias veces)"
    elif command -v konsole >/dev/null 2>&1; then
        konsole -p tabtitle="$title" -e bash -lc "$cmd; exec bash" &
    else
        x-terminal-emulator -e bash -lc "$cmd; exec bash" &
    fi
}

echo "== 1/4  Levantando el stack =="
if [ "$MODE" = "docker" ]; then
    $DOCKER up -d
    LOGS_CMD="cd '$ROOT' && $DOCKER logs -f --tail 20 telemetry"
else
    ./start_studio_single_pc.sh &
    LOGS_CMD="cd '$ROOT' && tail -f registros/gui_state.json"
fi

echo "== 2/4  Esperando a la señal de programa (:15000) =="
until bash -c 'exec 3<>/dev/tcp/127.0.0.1/15000' 2>/dev/null; do sleep 1; done
echo "  :15000 listo."

echo "== 3/4  Abriendo PROGRAM (ffplay) y TELEMETRY (logs) =="
ffplay -hide_banner -window_title "PROGRAM" -x 704 -y 540 \
       tcp://127.0.0.1:15000 >/dev/null 2>&1 &
open_terminal "TELEMETRY" "$LOGS_CMD"

echo "== 4/4  Abriendo voctogui =="
( cd voctogui && python3 voctogui.py >/dev/null 2>&1 & )

cat <<'EOF'

────────────────────────────────────────────────────────────
 Ventanas abiertas: voctogui · PROGRAM · TELEMETRY
 Ahora en OBS:
   1. Importa la escena  presentacion_tfg/obs/  (ver README.md)
      o crea 3 fuentes "Captura de ventana" y colócalas así
      (Ctrl+E en cada una, lienzo 1920x1080):

        Fuente     Pos X   Pos Y   Caja (Ajustar a interior)
        GUI          0       0        1216 x 1080
        PROGRAM    1216      0         704 x 540
        TELEMETRY  1216     540        704 x 540

   2. Iniciar grabación y seguir GUION_VIDEO.md (segundo a segundo).
 No minimices ninguna de las tres ventanas mientras grabas.
────────────────────────────────────────────────────────────
EOF
