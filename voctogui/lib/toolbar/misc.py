#!/usr/bin/env python3
import logging
from gi.repository import Gdk, Gtk

from lib.config import Config
import lib.connection as Connection


class MiscToolbarController(object):
    """Manages Accelerators and Clicks Misc buttons"""

    def __init__(self, win, uibuilder):
        self.win = win
        self.log = logging.getLogger('MiscToolbarController')
        self.toolbar = uibuilder.find_widget_recursive(win, 'toolbar_main')

        # Accelerators
        accelerators = Gtk.AccelGroup()
        win.add_accel_group(accelerators)

        closebtn = uibuilder.find_widget_recursive(self.toolbar, 'close')
        closebtn.set_visible(Config.getboolean('misc', 'close'))
        closebtn.connect('clicked', self.on_closebtn_clicked)

        fullscreenbtn = uibuilder.find_widget_recursive(self.toolbar, 'fullscreen')
        if fullscreenbtn:
            fullscreenbtn.set_visible(Config.getShowFullScreenButton())
            fullscreenbtn.connect('clicked', self.on_fullscreenbtn_clicked)
            key, mod = Gtk.accelerator_parse('F11')
            fullscreenbtn.add_accelerator('clicked', accelerators,
                                   key, mod, Gtk.AccelFlags.VISIBLE)
            self.fullscreen_button = fullscreenbtn
            self.__is_fullscreen = False
            self.within_state_event = False
            win.connect("window-state-event", self.on_window_state_event)


        #cutbtn = uibuilder.find_widget_recursive(toolbar, 'cut')
        #cutbtn.set_visible(Config.getboolean('misc', 'cut'))
        #cutbtn.connect('clicked', self.on_cutbtn_clicked)

        key, mod = Gtk.accelerator_parse('t')
        #cutbtn.add_accelerator('clicked', accelerators,
        #                       key, mod, Gtk.AccelFlags.VISIBLE)
        tooltip = Gtk.accelerator_get_label(key, mod)
        #cutbtn.set_tooltip_text(tooltip)

    def on_closebtn_clicked(self, btn):
        self.log.info('close-button clicked')
        Gtk.main_quit()

    def on_cutbtn_clicked(self, btn):
        self.log.info('cut-button clicked')
        Connection.send('message', 'cut')

    def on_fullscreenbtn_clicked(self, btn):
        if not self.within_state_event:
            self.log.info('fullscreen-button clicked')
            if self.__is_fullscreen:
                self.win.unfullscreen()
            else:
                self.win.fullscreen()

    def on_window_state_event(self, widget, ev):
        self.within_state_event = True
        self.__is_fullscreen = bool(ev.new_window_state & Gdk.WindowState.FULLSCREEN)
        if hasattr(self, 'fullscreen_button'):
            self.fullscreen_button.set_active(self.__is_fullscreen)
        self.within_state_event = False
