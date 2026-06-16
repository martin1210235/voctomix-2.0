#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import subprocess
import socket
import os

class IntroLauncher(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Intro Launcher")
        self.set_default_size(200, 80)
        self.set_keep_above(True)
        self.set_border_width(10)

        button = Gtk.Button(label="▶ LAUNCH INTRO")
        button.connect("clicked", self.on_button_clicked)
        self.add(button)

    def on_button_clicked(self, widget):
        print("Launching intro source...")
        # Switch voctocore to the 'intro' source
        try:
            host = os.environ.get("VOCTOCORE_HOST", "127.0.0.1")
            port = int(os.environ.get("VOCTOCORE_PORT", "9999"))
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, port))
            s.sendall(b'set_video_a intro\n')
            s.close()
        except Exception:
            pass

        script_path = os.path.join(os.path.dirname(__file__), "launch_intro.sh")
        subprocess.Popen(["/bin/bash", script_path])

win = IntroLauncher()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
