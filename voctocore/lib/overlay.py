#!/usr/bin/env python3
from gi.repository import Gst, GstController
import logging
import gi
gi.require_version('GstController', '1.0')


class Overlay:
    log = logging.getLogger('Overlay')

    def __init__(self, pipeline, element_name='overlay', location=None, blend_time=300):
        self.overlay = pipeline.get_by_name(element_name)
        self.location = location

        # Initial state is hidden (False) so the GUI button starts unchecked
        self.isVisible = False
        self.blend_time = blend_time

        if not self.overlay:
            self.log.error(f"GStreamer element not found: {element_name}")
            return

        self.alpha = GstController.InterpolationControlSource()
        self.alpha.set_property('mode', GstController.InterpolationMode.LINEAR)
        cb = GstController.DirectControlBinding.new_absolute(self.overlay, 'alpha', self.alpha)
        self.overlay.add_control_binding(cb)

        # Start fully transparent
        self.alpha.set(0, 0.0)

    def set(self, location):
        '''Update the image file path.'''
        self.location = location if location else ""
        if self.isVisible and self.overlay:
            self.overlay.set_property('location', self.location)

    def show(self, visible, playtime):
        '''Control visibility with a smooth alpha fade transition.'''
        if not self.overlay:
            return

        assert self.alpha

        if self.isVisible != visible:
            if self.blend_time > 0:
                self.alpha.set(playtime, 0.0 if visible else 1.0)
                self.alpha.set(playtime + int(Gst.SECOND / 1000.0 * self.blend_time), 1.0 if visible else 0.0)
            else:
                self.alpha.set(playtime, 1.0 if visible else 0.0)

            self.isVisible = visible

            if visible:
                self.overlay.set_property('location', self.location)

    def get(self):
        '''Return the current image file path.'''
        return self.location

    def visible(self):
        '''Return whether the overlay layer is currently visible.'''
        return self.isVisible
