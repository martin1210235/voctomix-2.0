#!/usr/bin/python3
import logging
import os
from gi.repository import Gst, GstNet

__all__ = ['Clock']
port = int(os.environ.get("VOCTOCORE_CLOCK_PORT", "9998"))

log = logging.getLogger('Clock')
Clock = None


def obtainClock(host):
    global log, Clock, SystemClock

    log.debug('obtaining NetClientClock from host %s', host)
    Clock = GstNet.NetClientClock.new('voctocore', host, port, 0)
    log.debug('obtained NetClientClock from host %s: %s', host, Clock)

    timeout_ns = int(os.environ.get("CLOCK_SYNC_TIMEOUT_MS", "5000")) * Gst.MSECOND
    log.debug('waiting for NetClientClock to sync (timeout %dms)', timeout_ns // Gst.MSECOND)
    synced = Clock.wait_for_sync(timeout_ns)
    if synced:
        log.info('successfully synced NetClientClock to host')
    else:
        log.debug('clock sync timed out, continuing without sync')
