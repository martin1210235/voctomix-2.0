#!/usr/bin/env bash
# Live viewer(s) of the running mix, pinned on top so they stay visible during a
# whole test. Uses gst xvimagesink (X11, no OpenGL -> works over AnyDesk/remote)
# and Wnck to raise + pin. Call AFTER the stack is up.
#
#   show_gui.sh          -> only the mix monitor (~1.6% CPU). Use for PERFORMANCE
#                           (1.1/1.2) so the CPU/RAM measured stays clean.
#   show_gui.sh gui      -> mix monitor + full voctogui mixer (~6.5% CPU extra).
#                           Use for LATENCY (2.x) and RESILIENCE (3.1), where the
#                           measurement is timing (CPU cost is irrelevant).
set -u
export DISPLAY="${DISPLAY:-:0}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WITH_GUI="${1:-}"

# --- mix monitor (always) ---
pkill -f "gst-launch.*port=11000" 2>/dev/null
sleep 0.5
nohup gst-launch-1.0 tcpclientsrc host=127.0.0.1 port=11000 \
    ! queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 \
    ! matroskademux ! videoconvert ! queue \
    ! xvimagesink force-aspect-ratio=true sync=false \
    >/tmp/gstmix.log 2>&1 &
sleep 4

# --- optional full voctogui ---
if [ "$WITH_GUI" = "gui" ] || [ "$WITH_GUI" = "--gui" ]; then
    pkill -f "python3 voctogui.py" 2>/dev/null
    sleep 0.5
    ( cd "$ROOT/voctogui" && nohup python3 voctogui.py >/tmp/voctogui.log 2>&1 & )
    sleep 9
fi

python3 - "$WITH_GUI" <<'PY'
import gi, sys, time
gi.require_version('Wnck', '3.0'); gi.require_version('Gtk', '3.0')
from gi.repository import Wnck, Gtk
Gtk.init([])
with_gui = sys.argv[1] in ("gui", "--gui")
scr = Wnck.Screen.get_default(); scr.force_update()
M = (Wnck.WindowMoveResizeMask.X | Wnck.WindowMoveResizeMask.Y |
     Wnck.WindowMoveResizeMask.WIDTH | Wnck.WindowMoveResizeMask.HEIGHT)
mon = gui = None
for w in scr.get_windows():
    n = w.get_name() or ""
    if "gst-launch" in n or "@!0,0" in n:
        mon = w
    elif n == "Voctomix GUI":
        gui = w
# Monitor: pequeño arriba-derecha si hay voctogui, grande si va solo.
if mon:
    try:
        mon.unmaximize()
        if with_gui and gui:
            mon.set_geometry(Wnck.WindowGravity.STATIC, M, 1180, 70, 700, 400)
        else:
            mon.set_geometry(Wnck.WindowGravity.STATIC, M, 40, 70, 980, 560)
        mon.make_above(); mon.activate(int(time.time()))
    except Exception as e:
        print("aviso monitor:", e)
# voctogui: grande, encima, frontal.
if with_gui and gui:
    try:
        gui.unmaximize()
        gui.set_geometry(Wnck.WindowGravity.STATIC, M, 30, 60, 1120, 900)
        gui.make_above(); gui.activate(int(time.time()) + 1)
    except Exception as e:
        print("aviso voctogui:", e)
for _ in range(25):
    Gtk.main_iteration_do(False); time.sleep(0.02)
print(f"[show_gui] monitor={'OK' if mon else 'NO'}"
      + (f" voctogui={'OK' if gui else 'NO'}" if with_gui else ""))
PY
