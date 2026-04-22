#!/usr/bin/env python3
import os
import logging
import subprocess

from gi.repository import Gtk, GObject
import lib.connection as Connection

from lib.config import Config
from vocto.composite_commands import CompositeCommand
from lib.toolbar.buttons import Buttons
from lib.uibuilder import UiBuilder


class MixToolbarController(object):
    """Manages Accelerators and Clicks on the Preview Composition Toolbar-Buttons"""

    def __init__(self, win, uibuilder, output_controller, preview_controller, overlay_controller=None):
        self.initialized = False
        self.output_controller = output_controller
        self.preview_controller = preview_controller
        self.overlay_controller = overlay_controller
        self.log = logging.getLogger('PreviewToolbarController')

        accelerators = Gtk.AccelGroup()
        win.add_accel_group(accelerators)

        self.mix = Buttons(Config['toolbar.mix'])

        self.toolbar = uibuilder.find_widget_recursive(
            win, 'toolbar_mix')

        self.mix.create(self.toolbar, accelerators,
                        self.on_btn_clicked, radio=False)

    def on_btn_clicked(self, btn):
        id = btn.get_name()

        # When AUTO-OFF is active, hide the overlay and deactivate dynamic text buttons on CUT or TRANS
        if self.overlay_controller and self.overlay_controller.isAutoOff() and id in ['cut', 'trans']:
            Connection.send('show_overlay', str(False))
            oc = self.overlay_controller
            if hasattr(oc, 'dynamic_btn') and oc.dynamic_btn.get_active():
                oc.dynamic_btn.set_active(False)
            if hasattr(oc, 'dynamic_btn_2') and oc.dynamic_btn_2.get_active():
                oc.dynamic_btn_2.set_active(False)

        command = self.preview_controller.command()
        self.preview_controller.set_command(self.output_controller.command())

        if id == 'cut':
            self.log.info('Sending new composite: %s', command)

            # Intro source is detected on either channel A (fullscreen) or B (PIP/SBS).
            # ffmpeg is restarted from the beginning and a delay is added before the cut.
            if str(command.A) == 'intro' or str(command.B) == 'intro':
                ruta_script = os.path.abspath(os.path.join(
                    os.path.dirname(__file__),
                    '../../../example-scripts/ffmpeg/launch_intro.sh'
                ))
                _cmd = str(command)
                # Audio always follows channel A: intro in A sends audio to intro;
                # intro in B (PIP/SBS) sends audio to the main source (A).
                _audio_src = str(command.A)
                _vol = Connection.cam_volumes.get(_audio_src)

                already_running = subprocess.run(
                    ['pgrep', '-f', 'tcp://.*:10005'],
                    capture_output=True
                ).returncode == 0
                subprocess.Popen(['/bin/bash', ruta_script])
                # If a process was already running, launch_intro.sh kills it and
                # voctocore sleeps 1 s before accepting a new connection (~1300 ms total).
                # If nothing was running, only ffmpeg startup time is needed (~500 ms).
                delay_ms = 1300 if already_running else 500

                def _do_cut_intro():
                    Connection.send('cut', _cmd)
                    Connection.send('set_audio', _audio_src)
                    if _vol is not None:
                        Connection.send('set_audio_volume', '{} {:.4f}'.format(_audio_src, _vol))
                    return False
                GObject.timeout_add(delay_ms, _do_cut_intro)
                return

            Connection.send('cut', str(command))
            Connection.send('set_audio', str(command.A))
            pref_vol = Connection.cam_volumes.get(str(command.A))
            if pref_vol is not None:
                Connection.send('set_audio_volume', '{} {:.4f}'.format(str(command.A), pref_vol))

        elif id == 'trans':
            self.log.info(
                'Sending new composite (using transition): %s', command)
            Connection.send('transition', str(command))
            Connection.send('set_audio', str(command.A))
            pref_vol = Connection.cam_volumes.get(str(command.A))
            if pref_vol is not None:
                Connection.send('set_audio_volume', '{} {:.4f}'.format(str(command.A), pref_vol))
