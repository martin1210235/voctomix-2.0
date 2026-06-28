#!/usr/bin/python3
import logging
import os
from gi.repository import Gst, GstNet

__all__ = ['Clock', 'NetTimeProvider']
port = int(os.environ.get("VOCTOCORE_CLOCK_PORT", "9998"))

log = logging.getLogger('Clock')

log.debug("Obtaining System-Clock")
Clock = Gst.SystemClock.obtain()
log.info("Using System-Clock for all pipelines.")

log.info("Starting NetTimeProvider on Port %u", port)
NetTimeProvider = GstNet.NetTimeProvider.new(Clock, '::', port)
