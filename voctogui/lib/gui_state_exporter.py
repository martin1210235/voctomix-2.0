#!/usr/bin/env python3
import json
import os
import threading
import time
import socket
import urllib.request
from datetime import datetime

from gi.repository import Gtk, GLib

class GuiStateExporter:
    def __init__(self, ui, interval=1.0):
        self.ui = ui
        self.interval = interval
        self.running = False
        self.thread = None
        self._cpu_last_idle = 0.0
        self._cpu_last_total = 0.0

        self.target_ip = os.environ.get("GUI_TARGET_IP")
        self.target_port = int(os.environ.get("TELEMETRY_HTTP_PORT", "8080"))

        if not self.target_ip:
            self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
            self.sessions_dir = os.path.join(self.base_dir, "sessions")
            self.output_path = os.path.join(self.sessions_dir, "gui_state.json")
            os.makedirs(self.sessions_dir, exist_ok=True)

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    def _loop(self):
        while self.running:
            try:
                # Stop the loop if the main window has been destroyed
                if not self.ui or not hasattr(self.ui, 'win') or self.ui.win is None:
                    break 

                state = self._collect_state_threadsafe()
                if state is not None:
                    if self.target_ip:
                        url = f"http://{self.target_ip}:{self.target_port}/gui_state"
                        data = json.dumps(state, ensure_ascii=False).encode('utf-8')
                        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')
                        try:
                            with urllib.request.urlopen(req, timeout=0.5) as response:
                                pass
                        except:
                            pass 
                    else:
                        tmp_path = self.output_path + ".tmp"
                        with open(tmp_path, "w", encoding="utf-8") as f:
                            json.dump(state, f, ensure_ascii=False, indent=2)
                        os.replace(tmp_path, self.output_path)
            except Exception as e:
                # Stop silently on GTK "widget destroyed" errors
                if "destroyed" in str(e).lower():
                    break
            time.sleep(self.interval)

    def _collect_state_threadsafe(self):
        result = {"done": False, "data": None}

        def idle_collect():
            try:
                result["data"] = self._collect_state()
            except Exception:
                result["data"] = None
            result["done"] = True
            return False

        GLib.idle_add(idle_collect)

        timeout = time.time() + 2.0
        while not result["done"] and time.time() < timeout and self.running:
            time.sleep(0.02)

        return result["data"]

    def _collect_system_health(self):
        result = {
            "cpu_usage_percent": 0.0,
            "ram_usage_percent": 0.0,
            "ram_available_mb": 0,
        }
        try:
            with open('/proc/stat', 'r') as f:
                parts = [float(x) for x in f.readline().split()[1:]]
            idle, total = parts[3], sum(parts)
            delta_idle = idle - self._cpu_last_idle
            delta_total = total - self._cpu_last_total
            self._cpu_last_idle, self._cpu_last_total = idle, total
            if delta_total > 0:
                result["cpu_usage_percent"] = round(100.0 * (1.0 - delta_idle / delta_total), 1)
        except Exception:
            pass
        try:
            mem_total = mem_available = 0
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if line.startswith('MemTotal:'):
                        mem_total = int(line.split()[1])
                    elif line.startswith('MemAvailable:'):
                        mem_available = int(line.split()[1])
            if mem_total > 0:
                result["ram_available_mb"] = mem_available // 1024
                result["ram_usage_percent"] = round(100.0 * (mem_total - mem_available) / mem_total, 1)
        except Exception:
            pass
        return result

    def _get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "unknown"

    def _collect_state(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return {
            "last_update": now,
            "gui_ip": self._get_local_ip(),
            "preview": {
                "channel_a": self._get_toolbar_active_name("toolbar_preview_a"),
                "channel_b": self._get_toolbar_active_name("toolbar_preview_b"),
            },
            "mode": self._get_mode(),
            "composite": self._get_composite(),
            "mirror": self._get_mirror(),
            "insertion": {
                "overlay": self._get_toggle_state("insert"),
                "auto_off": self._get_toggle_state("insert-auto-off"),
                "overlay_selected": self._read_combo_active_text("inserts"),
                "logo1": self._get_toggle_state("logo1"),
                "logo2": self._get_toggle_state("logo2"),
                "text1_active": self._get_toggle_state_by_name("tfg-btn"),
                "text1_value": self._get_entry_text_by_name("tfg-entry"),
                "text2_active": self._get_toggle_state_by_name("tfg-btn-2"),
                "text2_value": self._get_entry_text_by_name("tfg-entry-2"),
            },
            "audio": self._collect_audio_levels(),
            "system_health": self._collect_system_health(),
        }

    def _find_widget_recursive(self, parent, wanted_id):
        if parent is None:
            return None

        try:
            if self._widget_matches_name(parent, wanted_id):
                return parent
        except Exception:
            pass

        try:
            if hasattr(parent, "get_children"):
                for child in parent.get_children():
                    found = self._find_widget_recursive(child, wanted_id)
                    if found is not None:
                        return found
        except Exception:
            pass

        return None

    def _get_widget(self, widget_id):
        if hasattr(self.ui, "builder"):
            try:
                w = self.ui.builder.get_object(widget_id)
                if w is not None:
                    return w
            except Exception:
                pass

        if hasattr(self.ui, "win"):
            return self._find_widget_recursive(self.ui.win, widget_id)

        return None

    def _iter_all_widgets(self, root):
        stack = [root]
        while stack:
            widget = stack.pop()
            yield widget
            try:
                if hasattr(widget, "get_children"):
                    children = widget.get_children()
                    for child in reversed(children):
                        stack.append(child)
            except Exception:
                pass

    def _buildable_name(self, widget):
        try:
            return Gtk.Buildable.get_name(widget)
        except Exception:
            return None

    def _gtk_name(self, widget):
        try:
            if hasattr(widget, "get_name"):
                return widget.get_name()
        except Exception:
            pass
        return None

    def _widget_matches_name(self, widget, wanted_name):
        if widget is None:
            return False

        try:
            bname = self._buildable_name(widget)
            if bname == wanted_name:
                return True
        except Exception:
            pass

        try:
            gname = self._gtk_name(widget)
            if gname == wanted_name:
                return True
        except Exception:
            pass

        return False

    def _widget_label_text(self, widget):
        if widget is None:
            return ""

        try:
            if hasattr(widget, "get_label"):
                label = widget.get_label()
                if label:
                    return str(label).strip()
        except Exception:
            pass

        try:
            child = widget.get_child()
            if child and hasattr(child, "get_text"):
                text = child.get_text()
                if text:
                    return str(text).strip()
        except Exception:
            pass

        return ""

    def _normalize_name(self, raw):
        if raw is None:
            return "unknown"

        value = str(raw).strip().lower()
        if not value:
            return "unknown"

        value = value.replace("_", " ").replace("-", " ").strip()

        mapping = {
            "cam1": "cam1",
            "cam2": "cam2",
            "cam3": "cam3",
            "cam4": "cam4",
            "slides": "cam4",  # alias kept for backward compatibility
            "grabber": "break",
            "break": "break",
            "intro": "intro",

            "fullscreen": "full_screen",
            "full screen": "full_screen",
            "fs": "full_screen",

            "side by side": "side_by_side",
            "sbs": "side_by_side",

            "pip": "picture_in_picture",
            "picture in picture": "picture_in_picture",

            "lecture": "lecture",
            "lec": "lecture",

            "mirror": "mirror",

            "live": "live",
            "pause": "pause",
            "nostream": "nostream",
            "blank": "blank",
            "blinded": "blinded",
        }

        return mapping.get(value, value)

    def _toolbutton_semantic_name(self, widget):
        if widget is None:
            return "unknown"

        candidates = []

        try:
            name_prop = widget.get_name()
            if name_prop:
                candidates.append(name_prop)
        except Exception:
            pass

        buildable = self._buildable_name(widget)
        if buildable:
            candidates.append(buildable)

        label = self._widget_label_text(widget)
        if label:
            candidates.append(label)

        bad = {
            "gtkradiobutton",
            "gtktogglebutton",
            "gtktoolbutton",
            "gtkradiotoolbutton",
            "unknown",
            "",
        }

        for candidate in candidates:
            norm = self._normalize_name(candidate)
            if norm not in bad:
                return norm

        return "unknown"

    def _get_toolbar_active_name(self, toolbar_id):
        toolbar = self._get_widget(toolbar_id)
        if toolbar is None:
            return "unknown"

        try:
            children = toolbar.get_children()
        except Exception:
            return "unknown"

        for child in children:
            try:
                if hasattr(child, "get_active") and child.get_active():
                    return self._toolbutton_semantic_name(child)
            except Exception:
                continue

        return "none"

    def _get_toggle_state(self, widget_id):
        widget = self._get_widget(widget_id)
        if widget is None:
            return False

        try:
            if hasattr(widget, "get_active"):
                return bool(widget.get_active())
        except Exception:
            pass

        return False

    def _get_toggle_state_by_name(self, wanted_name):
        if not hasattr(self.ui, "win"):
            return False

        for widget in self._iter_all_widgets(self.ui.win):
            try:
                if self._widget_matches_name(widget, wanted_name) and hasattr(widget, "get_active"):
                    return bool(widget.get_active())
            except Exception:
                continue

        return False

    def _get_entry_text_by_name(self, wanted_name):
        if not hasattr(self.ui, "win"):
            return ""

        for widget in self._iter_all_widgets(self.ui.win):
            try:
                if self._widget_matches_name(widget, wanted_name) and hasattr(widget, "get_text"):
                    return widget.get_text()
            except Exception:
                continue

        return ""

    def _read_combo_active_text(self, widget_id):
        combo = self._get_widget(widget_id)
        if combo is None:
            return "unknown"

        try:
            tree_iter = combo.get_active_iter()
            model = combo.get_model()
            if tree_iter is not None and model is not None:
                try:
                    return str(model[tree_iter][1])
                except Exception:
                    return str(model[tree_iter][0])
        except Exception:
            pass

        try:
            if hasattr(combo, "get_active_text"):
                txt = combo.get_active_text()
                if txt is not None:
                    return str(txt)
        except Exception:
            pass

        return "unknown"

    def _get_mode(self):
        toolbar = self._get_widget("toolbar_mode")
        if toolbar is None:
            return "unknown"

        try:
            children = toolbar.get_children()
        except Exception:
            return "unknown"

        for child in children:
            try:
                if hasattr(child, "get_active") and child.get_active():
                    name = self._toolbutton_semantic_name(child)
                    if name == "blank":
                        return "pause"
                    if name in ("live", "pause", "nostream"):
                        return name

                    label = self._widget_label_text(child).strip().lower()
                    if label == "live":
                        return "live"
                    if label == "pause":
                        return "pause"
            except Exception:
                continue

        return "unknown"

    def _get_composite(self):
        name = self._get_toolbar_active_name("toolbar_preview_composite")

        result = {
            "name": "unknown",
            "fullscreen": False,
            "side_by_side": False,
            "pip": False,
            "lecture": False,
        }

        if name in ("full_screen", "side_by_side", "picture_in_picture", "lecture"):
            result["name"] = name

        if result["name"] == "full_screen":
            result["fullscreen"] = True
        elif result["name"] == "side_by_side":
            result["side_by_side"] = True
        elif result["name"] == "picture_in_picture":
            result["pip"] = True
        elif result["name"] == "lecture":
            result["lecture"] = True

        return result

    def _get_mirror(self):
        mod_name = self._get_toolbar_active_name("toolbar_preview_mod")
        return mod_name == "mirror"

    def _collect_audio_levels(self):
        values = {
            "cam1_db": None,
            "cam2_db": None,
            "cam3_db": None,
            "cam4_db": None,
            "break_db": None,
            "intro_db": None,
        }

        if not hasattr(self.ui, "win"):
            return values

        preview_widgets = []
        for widget in self._iter_all_widgets(self.ui.win):
            try:
                if self._widget_matches_name(widget, "widget_preview"):
                    preview_widgets.append(widget)
            except Exception:
                continue

        for preview in preview_widgets:
            source_name = None
            audio_level_value = None

            for widget in self._iter_all_widgets(preview):
                bname = self._buildable_name(widget)

                try:
                    if bname == "label" and hasattr(widget, "get_text"):
                        source_name = self._normalize_name(widget.get_text())
                    elif bname == "audio_level" and hasattr(widget, "get_value"):
                        audio_level_value = round(float(widget.get_value()), 2)
                except Exception:
                    continue

            key_map = {
                "cam1": "cam1_db",
                "cam2": "cam2_db",
                "cam3": "cam3_db",
                "cam4": "cam4_db",
                "break": "break_db",
                "intro": "intro_db",
            }

            if source_name in key_map:
                values[key_map[source_name]] = audio_level_value

        return values
