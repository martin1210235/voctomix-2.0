#!/usr/bin/env python3
import os
import logging
import urllib.parse

from gi.repository import Gtk, Gdk
import lib.connection as Connection

from lib.config import Config

def quote(s):
    return urllib.parse.quote(str(s)) if s else ""

def dequote(s):
    return urllib.parse.unquote(str(s)) if s else ""

def str2bool(v):
    return str(v).lower() in ("yes", "true", "t", "1")

class OverlayToolbarController(object):
    """Manages Accelerators and Clicks on the Overlay Composition Toolbar-Buttons"""

    def __init__(self, win, uibuilder):
        self.initialized = False
        self.log = logging.getLogger('OverlayToolbarController')
        
        self.win = win

        self.dynamic_active = False
        self.dynamic_active_2 = False

        accelerators = Gtk.AccelGroup()
        win.add_accel_group(accelerators)

        self.logo1_btn = uibuilder.find_widget_recursive(win, 'logo1')
        if self.logo1_btn:
            self.logo1_btn.connect('toggled', self.on_logo1_toggled)
            Connection.on('logo1_visible', self.on_logo1_visible)
            Connection.send('get_logo1_visible')

        self.logo2_btn = uibuilder.find_widget_recursive(win, 'logo2')
        if self.logo2_btn:
            self.logo2_btn.connect('toggled', self.on_logo2_toggled)
            Connection.on('logo2_visible', self.on_logo2_visible)
            Connection.send('get_logo2_visible')

        box_insert = uibuilder.find_widget_recursive(win, 'box_insert')
        if box_insert:
            self.dynamic_main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
            
            self.section_label = Gtk.Label(label="DYNAMIC\nTEXT 1")
            self.section_label.set_angle(90) 
            self.section_label.set_justify(Gtk.Justification.CENTER)
            self.section_label.set_name("tfg-section-label")
            self.section_label.set_margin_left(0) 
            self.section_label.set_margin_right(2)
            
            self.dynamic_main_box.pack_start(self.section_label, False, False, 0)
            
            self.dynamic_frame = Gtk.Frame()
            self.dynamic_frame.set_name("tfg-frame")
            
            self.dynamic_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            self.dynamic_box.set_name("tfg-box")
            
            self.dynamic_label = Gtk.Label(label="TEXT 1")
            self.dynamic_label.set_name("tfg-label")
            self.dynamic_box.pack_start(self.dynamic_label, False, False, 0)
            
            self.dynamic_entry = Gtk.Entry()
            self.dynamic_entry.set_name("tfg-entry")
            self.dynamic_entry.set_width_chars(25)
            self.dynamic_entry.set_placeholder_text("Enter text here...")

            self.dynamic_entry.connect('focus-in-event', self.on_entry_focus_in)
            self.dynamic_entry.connect('focus-out-event', self.on_entry_focus_out)
            
            self.dynamic_box.pack_start(self.dynamic_entry, False, False, 0)
            
            self.dynamic_btn = Gtk.ToggleButton(label="INSERT 1")
            self.dynamic_btn.set_name("tfg-btn")
            self.dynamic_btn.connect('toggled', self.on_dynamic_send_1)
            self.dynamic_box.pack_start(self.dynamic_btn, False, False, 0)
            
            self.dynamic_frame.add(self.dynamic_box)
            self.dynamic_main_box.pack_start(self.dynamic_frame, False, False, 0)

            self.dynamic_main_box_2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
            
            self.section_label_2 = Gtk.Label(label="DYNAMIC\nTEXT 2")
            self.section_label_2.set_angle(90) 
            self.section_label_2.set_justify(Gtk.Justification.CENTER)
            self.section_label_2.set_name("tfg-section-label")
            self.section_label_2.set_margin_left(0) 
            self.section_label_2.set_margin_right(2)
            
            self.dynamic_main_box_2.pack_start(self.section_label_2, False, False, 0)
            
            self.dynamic_frame_2 = Gtk.Frame()
            self.dynamic_frame_2.set_name("tfg-frame")
            
            self.dynamic_box_2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            self.dynamic_box_2.set_name("tfg-box")
            
            self.dynamic_label_2 = Gtk.Label(label="TEXT 2")
            self.dynamic_label_2.set_name("tfg-label")
            self.dynamic_box_2.pack_start(self.dynamic_label_2, False, False, 0)
            
            self.dynamic_entry_2 = Gtk.Entry()
            self.dynamic_entry_2.set_name("tfg-entry-2")
            self.dynamic_entry_2.set_width_chars(25)
            self.dynamic_entry_2.set_placeholder_text("Enter text here...")
            
            self.dynamic_entry_2.connect('focus-in-event', self.on_entry_focus_in)
            self.dynamic_entry_2.connect('focus-out-event', self.on_entry_focus_out)
            
            self.dynamic_box_2.pack_start(self.dynamic_entry_2, False, False, 0)
            
            self.dynamic_btn_2 = Gtk.ToggleButton(label="INSERT 2")
            self.dynamic_btn_2.set_name("tfg-btn-2")
            self.dynamic_btn_2.connect('toggled', self.on_dynamic_send_2)
            self.dynamic_box_2.pack_start(self.dynamic_btn_2, False, False, 0)
            
            self.dynamic_frame_2.add(self.dynamic_box_2)
            self.dynamic_main_box_2.pack_start(self.dynamic_frame_2, False, False, 0)

            vertical_container = box_insert.get_parent()
            while vertical_container is not None:
                if isinstance(vertical_container, Gtk.Box) and vertical_container.get_orientation() == Gtk.Orientation.VERTICAL:
                    break
                vertical_container = vertical_container.get_parent()

            if vertical_container:
                self.text_boxes_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
                self.text_boxes_container.pack_start(self.dynamic_main_box, False, False, 0)
                self.text_boxes_container.pack_start(self.dynamic_main_box_2, False, False, 0)
                vertical_container.pack_start(self.text_boxes_container, False, False, 2)
                self.text_boxes_container.show_all()

            # Intercept key events at window level to prevent Voctomix shortcuts
            # from consuming keystrokes typed into the text entries
            self.win.connect('key-press-event', self.on_window_key_press)
            self.win.connect('button-press-event', self.on_window_button_press)

        if Config.hasOverlay():
            self.inserts = uibuilder.find_widget_recursive(win, 'inserts')
            self.inserts_store = uibuilder.get_check_widget('insert-store')
            
            if self.inserts:
                self.inserts.connect('changed', self.on_inserts_changed)

            self.insert = uibuilder.find_widget_recursive(win, 'insert')
            if self.insert:
                self.insert.connect('toggled', self.on_insert_toggled)

            self.update_inserts = uibuilder.find_widget_recursive(win, 'update-inserts')
            if self.update_inserts:
                self.update_inserts.connect('clicked', self.update_overlays)

            self.autooff = uibuilder.find_widget_recursive(win, 'insert-auto-off')
            if self.autooff:
                self.autooff.set_visible(Config.getOverlayUserAutoOff())
                self.autooff.set_active(Config.getOverlayAutoOff())

            self.overlay_description = uibuilder.find_widget_recursive(win, 'overlay-description')
            self.overlays = []

            Connection.on('overlays', self.on_overlays)
            Connection.on('overlays_title', self.on_overlays_title)
            Connection.on('overlay', self.on_overlay)
            Connection.on('overlay_visible', self.on_overlay_visible)
            
            self.update_overlays()
            
            if box_insert:
                box_insert.show()
        else:
            if box_insert:
                box_insert.hide()


    def on_entry_focus_in(self, widget, event):
        """Temporarily disable window accelerators while a text entry has focus."""
        try:
            if hasattr(self.win, "list_accel_groups"):
                self.win_accel_groups = self.win.list_accel_groups()
            else:
                self.win_accel_groups = []
        except Exception:
            self.win_accel_groups = []
            
        for ag in self.win_accel_groups:
            self.win.remove_accel_group(ag)
        return False 

    def on_entry_focus_out(self, widget, event):
        """Restore window accelerators when a text entry loses focus."""
        try:
            for ag in getattr(self, "win_accel_groups", []):
                self.win.add_accel_group(ag)
        except Exception:
            pass
        return False

    def on_window_button_press(self, widget, event):
        """Remove focus from the text entry when clicking elsewhere in the window."""
        if (hasattr(self, 'dynamic_entry') and self.dynamic_entry.is_focus()) or \
           (hasattr(self, 'dynamic_entry_2') and self.dynamic_entry_2.is_focus()):
            self.win.set_focus(None)
        return False 

    def on_window_key_press(self, widget, event):
        """Handle key events for focused text entries before Voctomix accelerators consume them."""
        focused_entry = None
        focused_btn = None

        if hasattr(self, 'dynamic_entry') and self.dynamic_entry.is_focus():
            focused_entry = self.dynamic_entry
            focused_btn = self.dynamic_btn
        elif hasattr(self, 'dynamic_entry_2') and self.dynamic_entry_2.is_focus():
            focused_entry = self.dynamic_entry_2
            focused_btn = self.dynamic_btn_2

        if focused_entry:
            # Enter
            if event.keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
                focused_btn.set_active(not focused_btn.get_active())
                return True
            
            # Escape
            if event.keyval == Gdk.KEY_Escape:
                self.win.set_focus(None)
                return True

            if event.keyval == Gdk.KEY_space:
                if focused_entry.get_selection_bounds():
                    focused_entry.delete_selection()
                pos = focused_entry.get_position()
                text = focused_entry.get_text()
                focused_entry.set_text(text[:pos] + " " + text[pos:])
                focused_entry.set_position(pos + 1)
                return True

            if event.keyval == Gdk.KEY_BackSpace:
                if focused_entry.get_selection_bounds():
                    focused_entry.delete_selection()
                else:
                    pos = focused_entry.get_position()
                    if pos > 0:
                        focused_entry.delete_text(pos - 1, pos)
                return True

            if event.keyval == Gdk.KEY_Delete:
                if focused_entry.get_selection_bounds():
                    focused_entry.delete_selection()
                else:
                    pos = focused_entry.get_position()
                    text_len = len(focused_entry.get_text())
                    if pos < text_len:
                        focused_entry.delete_text(pos, pos + 1)
                return True

        return False 

    def on_dynamic_send_1(self, widget):
        btn_ctx = self.dynamic_btn.get_style_context()
        ent_ctx = self.dynamic_entry.get_style_context()
        
        if self.dynamic_btn.get_active():
            text = self.dynamic_entry.get_text()
            Connection.send('set_text', quote(text))
            btn_ctx.add_class("overlay-active")
            ent_ctx.add_class("overlay-active")
        else:
            Connection.send('set_text', quote(""))
            btn_ctx.remove_class("overlay-active")
            ent_ctx.remove_class("overlay-active")

    def on_dynamic_send_2(self, widget):
        btn_ctx = self.dynamic_btn_2.get_style_context()
        ent_ctx = self.dynamic_entry_2.get_style_context()
        
        if self.dynamic_btn_2.get_active():
            text = self.dynamic_entry_2.get_text()
            Connection.send('set_text2', quote(text))
            btn_ctx.add_class("overlay-active")
            ent_ctx.add_class("overlay-active")
        else:
            Connection.send('set_text2', quote(""))
            btn_ctx.remove_class("overlay-active")
            ent_ctx.remove_class("overlay-active")


    def on_logo1_toggled(self, btn):
        if not self.initialized:
            return
        is_active = self.logo1_btn.get_active()
        Connection.send('show_logo1', str(is_active))

    def on_logo1_visible(self, visible):
        is_visible = str2bool(visible)
        if self.logo1_btn:
            self.logo1_btn.set_active(is_visible)

    def on_logo2_toggled(self, btn):
        if not self.initialized:
            return
        is_active = self.logo2_btn.get_active()
        Connection.send('show_logo2', str(is_active))

    def on_logo2_visible(self, visible):
        is_visible = str2bool(visible)
        if self.logo2_btn:
            self.logo2_btn.set_active(is_visible)

    def on_insert_toggled(self, btn):
        if not self.initialized:
            return
        Connection.send('show_overlay', str(self.insert.get_active()))

    def on_inserts_changed(self, combobox):
        if not self.initialized:
            return
        if self.inserts.get_active_iter():
            selected_overlay = self.inserts_store[self.inserts.get_active_iter()][0]
            if self.isAutoOff():
                Connection.send('show_overlay', str(False))
                # Also clear dynamic text overlays when switching
                if hasattr(self, 'dynamic_btn') and self.dynamic_btn.get_active():
                    self.dynamic_btn.set_active(False)
                if hasattr(self, 'dynamic_btn_2') and self.dynamic_btn_2.get_active():
                    self.dynamic_btn_2.set_active(False)
            Connection.send('set_overlay', quote(str(selected_overlay)))

    def on_overlay_visible(self, visible):
        is_visible = str2bool(visible)
        if hasattr(self, 'insert') and self.insert:
            self.insert.set_active(is_visible)
            
        if hasattr(self, 'inserts') and self.inserts:
            context = self.inserts.get_style_context()
            if is_visible:
                context.add_class("overlay-active")
            else:
                context.remove_class("overlay-active")

    def on_overlay(self, *args):
        overlay = args[0] if len(args) > 0 else ""
        overlay = dequote(overlay)
        overlays = [o for o, t in self.overlays]
        if overlay in overlays:
            self.inserts.set_active(overlays.index(overlay))
        else:
            if self.overlays:
                self.inserts.set_active(0)
        
        if hasattr(self, 'insert') and self.insert and hasattr(self, 'inserts') and self.inserts:
            self.insert.set_sensitive(not self.inserts.get_active_iter() is None)

    def on_overlays(self, overlays=None):
        if overlays is None:
            return
        
        overlays = [dequote(o).split('|') for o in overlays.split(",")]
        overlays = [o if len(o) == 2 else (o[0], o[0]) for o in overlays]
        
        if hasattr(self, 'inserts_store') and self.inserts_store is not None:
            self.inserts_store.clear()
            if overlays:
                for o in overlays:
                    self.inserts_store.append(o)
                
        if hasattr(self, 'inserts') and self.inserts:
            self.inserts.set_sensitive(len(overlays) > 1 if overlays else False)
            
        self.overlays = overlays
        self.initialized = True
        
        Connection.send('get_overlay_visible')
        Connection.send('get_overlay')

    def on_overlays_title(self, *args):
        if not hasattr(self, 'overlay_description') or not self.overlay_description:
            return
            
        title_str = args[0] if len(args) > 0 else ""
        title = [dequote(t) for t in title_str.split(",")]
        
        if title and title[0]:
            if len(title) == 4:
                start, end, id, text = title
                self.overlay_description.set_text(
                    "{start} - {end} : #{id}  '{text}'".format(
                        start=start.split(" ")[1],
                        end=end.split(" ")[1],
                        id=id, text=text))
            else:
                self.overlay_description.set_text(title[0])
            self.overlay_description.show()
        else:
            self.overlay_description.hide()

    def update_overlays(self, btn=None):
        Connection.send('get_overlays')
        Connection.send('get_overlays_title')

    def isAutoOff(self):
        if Config.hasOverlay() and hasattr(self, 'autooff') and self.autooff:
            return self.autooff.get_active()
        return False
