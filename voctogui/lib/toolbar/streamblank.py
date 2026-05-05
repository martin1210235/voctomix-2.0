#!/usr/bin/env python3
import logging
import json
import os

from gi.repository import Gtk
import lib.connection as Connection

from lib.config import Config


class StreamblankToolbarController(object):
    """Manages Accelerators and Clicks on the Composition Toolbar-Buttons"""

    def __init__(self, win, uibuilder, warning_overlay):
        self.log = logging.getLogger('StreamblankToolbarController')
        self.toolbar = uibuilder.find_widget_recursive(win, 'toolbar_mode')

        self.warning_overlay = warning_overlay

        livebtn = uibuilder.find_widget_recursive(self.toolbar, 'stream_live')
        blankbtn = uibuilder.find_widget_recursive(self.toolbar, 'stream_blank')

        blankbtn_pos = self.toolbar.get_item_index(blankbtn)

        if not Config.getboolean('stream-blanker', 'enabled'):
            self.log.info('disabling stream-blanker features '
                          'because the server does not support them: %s',
                          Config.getboolean('stream-blanker', 'enabled'))

            self.toolbar.remove(livebtn)
            self.toolbar.remove(blankbtn)
            return

        blank_sources = Config.getlist('stream-blanker', 'sources')

        self.current_status = None
        self.current_video = 'cam1'  # last source with active audio
        self.is_blanked = False

        livebtn.connect('toggled', self.on_btn_toggled)
        livebtn.set_can_focus(False)
        self.livebtn = livebtn
        self.blank_btns = {}

        accel_f_key = 11

        for idx, name in enumerate(blank_sources):
            if idx == 0:
                new_btn = blankbtn
            else:
                new_btn = Gtk.RadioToolButton(group=livebtn)
                self.toolbar.insert(new_btn, blankbtn_pos)

            new_btn.set_name(name)
            new_btn.set_can_focus(False)
            new_btn.set_label(name.upper())
            new_btn.connect('toggled', self.on_btn_toggled)
            new_btn.set_tooltip_text("Stop streaming by %s" % name)

            self.blank_btns[name] = new_btn
            accel_f_key = accel_f_key - 1

        Connection.on('stream_status', self.on_stream_status)
        Connection.send('get_stream_status')

        # AFV: track which source currently has audio
        Connection.on('audio_status', self.on_audio_status)
        Connection.send('get_audio')

        Connection.on('video_status', self.on_video_status)
        Connection.send('get_video')

    def on_audio_status(self, *parts):
        """Track the active audio source and enforce silence while blanked.

        In LIVE mode: updates current_video with the loudest source.
        In PAUSE/NOSTREAM mode: if a source gains volume (e.g. due to a CUT),
        mutes it immediately so that CUT changes video without changing audio."""
        try:
            volumes = json.loads("".join(parts))
            active_source, active_vol = max(
                volumes.items(), key=lambda kv: float(kv[1])
            )
            if float(active_vol) > 0.0:
                self.current_video = active_source
                if self.is_blanked:
                    # Mute immediately: stream is still in PAUSE/NOSTREAM
                    Connection.send('set_audio_volume',
                                    '{} 0.0'.format(active_source))
        except Exception:
            pass

    def on_video_status(self, source_a, source_b):
        # video_status is not used for audio tracking: it also fires when
        # the operator changes the preview without performing a CUT.
        pass

    def on_btn_toggled(self, btn):
        if btn.get_active():
            btn_name = btn.get_name()

            if self.current_status == btn_name:
                self.log.info('stream-status already active: %s', btn_name)
                return

            self.log.info('stream-status activated: %s', btn_name)

            if btn_name == 'live':
                self.is_blanked = False
                Connection.is_blanked = False
                Connection.send('set_stream_live')
                # AFV: restore audio to the last active source when returning to LIVE
                Connection.send('set_audio', self.current_video)
                pref_vol = Connection.cam_volumes.get(self.current_video, 1.0)
                Connection.send('set_audio_volume', '{} {:.4f}'.format(self.current_video, pref_vol))

            else:
                self.is_blanked = True
                Connection.is_blanked = True
                Connection.send('set_stream_blank', btn_name)
                # AFV: mute the active source when entering PAUSE/NOSTREAM
                Connection.send('set_audio_volume',
                                '{} 0.0'.format(self.current_video))

    def on_stream_status(self, status, source=None):
        self.log.info('on_stream_status callback w/ status %s and source %s',
                      status, source)

        self.is_blanked = (status != 'live')
        Connection.is_blanked = self.is_blanked
        self.current_status = source if source is not None else status
        if status == 'live':
            btn = self.livebtn
            self.warning_overlay.disable()
        else:
            btn = self.blank_btns[source]
            self.warning_overlay.enable(btn.get_name())
        if not btn.get_active():
            btn.set_active(True)
