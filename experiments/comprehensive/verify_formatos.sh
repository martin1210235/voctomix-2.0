#!/usr/bin/env bash
# Verificación visual de formato para Docker y Local: por cada formato, levanta el
# escenario, hace ffprobe de la salida del mix (:11000) y guarda un frame real (cuya
# resolución de imagen ES la prueba). Deja la evidencia en paper/pruebas/verificacion_formatos/.
#
# EJECUTAR SOLO con la máquina libre (NO mientras corre otra matriz: usa puertos/CPU).
#
# Uso:
#   verify_formatos.sh docker      # los 4 formatos en Docker
#   verify_formatos.sh local       # los 4 formatos en Local (nativo)
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../.."
ROOT="$(pwd)"
SCEN="${1:?docker|local}"
EVID="$ROOT/paper/pruebas/verificacion_formatos"; mkdir -p "$EVID"

probe_and_frame() {  # $1=scenario $2=fmt $3=W $4=H $5=F
    local sc="$1" fmt="$2" W="$3" H="$4" F="$5"
    echo "  ffprobe del mix (:11000)..."
    local info
    info=$(timeout 25 ffprobe -v error -select_streams v:0 \
        -show_entries stream=width,height,r_frame_rate,avg_frame_rate \
        -of default=noprint_wrappers=1 tcp://127.0.0.1:11000 2>/dev/null)
    echo "$info"
    { echo "=== $(date '+%Y-%m-%d %H:%M:%S') | $sc | pedido: $fmt ($W x $H @ ${F}fps) ==="
      echo "$info"; echo; } >> "$EVID/ffprobe_${sc}_${fmt}.txt"
    timeout 20 ffmpeg -y -nostdin -loglevel error -i tcp://127.0.0.1:11000 \
        -vf 'select=gte(t\,1)' -frames:v 1 "$EVID/frame_${sc}_${fmt}.png" 2>/dev/null
    echo "$info" | grep -q "width=$W" && echo "$info" | grep -q "height=$H" \
        && echo "  ANCHO/ALTO OK ($W x $H)" || echo "  ⚠ NO coincide (esperado $W x $H)"
}

for fmt in 1080p25 1080p50 2160p25 2160p50; do
    case "$fmt" in
        1080p25) W=1920;H=1080;F=25;; 1080p50) W=1920;H=1080;F=50;;
        2160p25) W=3840;H=2160;F=25;; 2160p50) W=3840;H=2160;F=50;;
    esac
    echo "########## $SCEN · $fmt ##########"
    bash experiments/comprehensive/set_format.sh "$fmt" >/dev/null

    if [ "$SCEN" = "docker" ]; then
        docker compose -f docker-compose.yml -f docker-compose.experiment.yml up -d >/dev/null 2>&1
        sleep 45
        ( sleep 6; python3 -c "import socket,time;s=socket.create_connection(('127.0.0.1',9999),timeout=5);time.sleep(.5);s.sendall(b'set_video_a cam1\n');time.sleep(1);s.close()" 2>/dev/null )
        sleep 4
        probe_and_frame docker "$fmt" "$W" "$H" "$F"
        docker compose -f docker-compose.yml -f docker-compose.experiment.yml down >/dev/null 2>&1
    else
        bash experiments/comprehensive/local_scenario.sh down >/dev/null 2>&1
        bash experiments/comprehensive/local_scenario.sh base_up >/dev/null 2>&1
        for n in 1 2 3 4; do bash experiments/comprehensive/local_scenario.sh cam_up "$n" experiment >/dev/null 2>&1; done
        sleep 35
        python3 -c "import socket,time;s=socket.create_connection(('127.0.0.1',9999),timeout=5);time.sleep(.5);s.sendall(b'set_video_a cam1\n');time.sleep(1);s.close()" 2>/dev/null
        sleep 4
        probe_and_frame local "$fmt" "$W" "$H" "$F"
        bash experiments/comprehensive/local_scenario.sh down >/dev/null 2>&1
    fi
done
echo "== EVIDENCIA en $EVID =="
ls -la "$EVID"
