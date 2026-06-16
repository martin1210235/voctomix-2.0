#!/usr/bin/env python3
import logging

from configparser import NoOptionError
from enum import Enum, unique
import gi
gi.require_version('GstController', '1.0')
from gi.repository import Gst
from lib.config import Config
from lib.clock import Clock
from lib.transitions import Composites, Transitions
from lib.scene import Scene

from lib.overlay import Overlay

from vocto.composite_commands import CompositeCommand

class VideoMix(object):
    log = logging.getLogger('VideoMix')

    def __init__(self):
        # read capabilites and sources from confg file
        self.caps = Config.get('mix', 'videocaps')
        self.sources = Config.getlist('mix', 'sources')
        self.log.info('Configuring Mixer for %u Sources', len(self.sources))

        # load composites from config
        self.log.info("Reading transitions configuration...")
        self.composites = Composites.configure(
            Config.items('composites'), self.getVideoSize())

        # load transitions from configuration
        self.transitions = Transitions.configure(Config.items(
            'transitions'), self.composites, fps=self.getFramesPerSecond())
        self.scene = None
        self.overlay = None
        self.logo1 = None
        self.logo2 = None
        self.launched = False

    def launch(self):

        # build GStreamer mixing pipeline descriptor
        pipeline = """
            compositor name=mix !
            {caps} !
        """.format(caps=self.caps)
        
        # 1. Dynamic overlay (lower thirds)
        if Config.hasOverlay():
            width, height = self.getVideoSize()
            pipeline += """
                queue max-size-time=3000000000 name=queue-overlay !
                gdkpixbufoverlay name=overlay overlay-width={width} overlay-height={height}
            """.format(width=width, height=height)
            
            if Config.getOverlayFile():
                pipeline += " location={overlay} alpha=1.0 ".format(
                    overlay=Config.getOverlayFilePath(Config.getOverlayFile())
                )
            else:
                self.log.info("No initial overlay source configured.")
            pipeline += " ! "

        # 2. Logo overlay 1 (initially hidden: alpha=0.0)
        if Config.hasLogo1():
            width, height = self.getVideoSize()
            pipeline += """
                queue max-size-time=3000000000 name=queue-logo1 !
                gdkpixbufoverlay name=logo1 overlay-width={width} overlay-height={height}
            """.format(width=width, height=height)
            
            if Config.getLogo1File():
                pipeline += " location={logo_path} alpha=0.0 ".format(
                    logo_path=Config.getLogo1File()
                )
            else:
                self.log.info("No initial logo1 file configured.")
            pipeline += " ! "

        # 3. Logo overlay 2 (initially hidden: alpha=0.0)
        if Config.hasLogo2():
            width, height = self.getVideoSize()
            pipeline += """
                queue max-size-time=3000000000 name=queue-logo2 !
                gdkpixbufoverlay name=logo2 overlay-width={width} overlay-height={height}
            """.format(width=width, height=height)
            
            if Config.getLogo2File():
                pipeline += " location={logo_path} alpha=0.0 ".format(
                    logo_path=Config.getLogo2File()
                )
            else:
                self.log.info("No initial logo2 file configured.")
            pipeline += " ! "

        # Dynamic text overlay 1 (bottom-left, upper position)
        pipeline += """
            textoverlay name=rotulo_dinamico text="" valignment=bottom halignment=left xpad=240 ypad=93 font-desc="Sans Bold 16" shaded-background=false draw-outline=true !
        """
        # Dynamic text overlay 2 (bottom-left, lower position)
        pipeline += """
            textoverlay name=rotulo_dinamico_2 text="" valignment=bottom halignment=left xpad=240 ypad=23 font-desc="Sans Bold 11" shaded-background=false draw-outline=true !
        """

        pipeline += """
            identity name=sig !
            queue !
            tee name=tee

            intervideosrc channel=video_background !
            {caps} !
            mix.

            tee. ! queue ! intervideosink channel=video_mix_out
        """.format(
            caps=self.caps
        )

        if Config.getboolean('previews', 'enabled'):
            pipeline += """
                tee. ! queue ! intervideosink channel=video_mix_preview
            """

        if Config.getboolean('stream-blanker', 'enabled'):
            pipeline += """
                tee. ! queue ! intervideosink channel=video_mix_stream-blanker
            """

        for idx, name in enumerate(self.sources):
            pipeline += """
                intervideosrc channel=video_{name}_mixer !
                {caps} !
                videobox name=video_{idx}_cropper !
                mix.
            """.format(
                name=name,
                caps=self.caps,
                idx=idx
            )

        # create pipeline
        self.log.debug('Creating Mixing-Pipeline:\n%s', pipeline)
        self.mixingPipeline = Gst.parse_launch(pipeline)
        self.mixingPipeline.use_clock(Clock)

        self.log.debug('Binding Error & End-of-Stream-Signal '
                       'on Mixing-Pipeline')
        self.mixingPipeline.bus.add_signal_watch()
        self.mixingPipeline.bus.connect("message::eos", self.on_eos)
        self.mixingPipeline.bus.connect("message::error", self.on_error)

        self.log.debug('Binding Handoff-Handler for '
                       'Synchronus mixer manipulation')
        sig = self.mixingPipeline.get_by_name('sig')
        sig.connect('handoff', self.on_handoff)

        self.log.debug('Initializing Mixer-State')
        # initialize pipeline bindings for all sources
        self.scene = Scene(self.sources, self.mixingPipeline, self.transitions.fps)
        self.compositeMode = None
        self.sourceA = None
        self.sourceB = None
        self.setCompositeEx(Composites.targets(self.composites)[0].name, self.sources[0], self.sources[1] )

        if Config.hasOverlay():
            self.overlay = Overlay(
                self.mixingPipeline, 'overlay', Config.getOverlayFile(), Config.getOverlayBlendTime())

        if Config.hasLogo1():
            self.logo1 = Overlay(
                self.mixingPipeline, 'logo1', Config.getLogo1File(), Config.getLogo1BlendTime())
            self.logo1.isVisible = False

        if Config.hasLogo2():
            self.logo2 = Overlay(
                self.mixingPipeline, 'logo2', Config.getLogo2File(), Config.getLogo2BlendTime())
            self.logo2.isVisible = False

        bgMixerpad = (self.mixingPipeline.get_by_name('mix')
                      .get_static_pad('sink_0'))
        bgMixerpad.set_property('zorder', 0)

        self.log.debug('Launching Mixing-Pipeline')
        self.mixingPipeline.set_state(Gst.State.PLAYING)
        self.launched = True

    def getVideoSize(self):
        caps = Gst.Caps.from_string(self.caps)
        struct = caps.get_structure(0)
        _, width = struct.get_int('width')
        _, height = struct.get_int('height')
        return width, height

    def getFramesPerSecond(self):
        caps = Gst.Caps.from_string(self.caps)
        struct = caps.get_structure(0)
        _, num, denom = struct.get_fraction('framerate')
        return float(num) / float(denom)

    def getPlayTime(self):
        return self.mixingPipeline.get_pipeline_clock().get_time() - \
            self.mixingPipeline.get_base_time()

    def on_handoff(self, object, buffer):
        if self.launched:
            if self.scene and self.scene.dirty:
                playTime = self.getPlayTime()
                self.log.debug('Applying new Mixer-State at %d ms', playTime / Gst.MSECOND)
                self.scene.push(playTime)

    def on_eos(self, bus, message):
        self.log.debug('Received End-of-Stream-Signal on Mixing-Pipeline')

    def on_error(self, bus, message):
        self.log.debug('Received Error-Signal on Mixing-Pipeline')
        (error, debug) = message.parse_error()
        self.log.debug('Error-Details: #%u: %s', error.code, debug)

    def setCompositeEx(self, newCompositeName=None, newA=None, newB=None, useTransitions = False):
        assert not newCompositeName or type(newCompositeName) == str
        assert not newA or type(newA) == str
        assert not newB or type(newB) == str

        if not self.compositeMode:
            curCompositeName = None
        else:
            curCompositeName = self.compositeMode
            curA = self.sourceA
            curB = self.sourceB

        if curCompositeName and not (newCompositeName and newA and newB):
            if not newCompositeName:
                newCompositeName = curCompositeName
            if not newA:
                newA = curA if newB != curA else curB
            if not newB:
                newB = curA if newA == curB else curB
        
        assert newA != newB
        curComposite = self.composites[curCompositeName] if curCompositeName else None
        newComposite = self.composites[newCompositeName]

        if newComposite and newA in self.sources and newB in self.sources:
            transition = None
            targetA, targetB = newA, newB
            if useTransitions:
                if curComposite:
                    swap = False
                    if (curA, curB) == (newA, newB):
                        transition, swap = self.transitions.solve(curComposite, newComposite, False)
                    elif (curA, curB) == (newB, newA):
                        transition, swap = self.transitions.solve(curComposite, newComposite, True)
                        if not swap:
                            targetA, targetB = newB, newA
            if transition:
                self.scene.commit(targetA, transition.Az(1,2))
                self.scene.commit(targetB, transition.Bz(2,1))
            else:
                self.scene.set(targetA, newComposite.Az(1))
                self.scene.set(targetB, newComposite.Bz(2))

        self.compositeMode = newComposite.name
        self.sourceA = newA
        self.sourceB = newB

    def setComposite(self, command, useTransitions=False):
        assert type(command) == str
        command = CompositeCommand.from_str(command)
        self.setCompositeEx(command.composite, command.A, command.B, useTransitions)

    def getVideoSources(self):
        return [self.sourceA, self.sourceB]

    def setVideoSourceA(self, source):
        self.setCompositeEx(None,source,None, useTransitions=False)

    def getVideoSourceA(self):
        return self.sourceA

    def setVideoSourceB(self, source):
        self.setCompositeEx(None,None,source, useTransitions=False)

    def getVideoSourceB(self):
        return self.sourceB

    def setCompositeMode(self, mode):
        self.setCompositeEx(mode,None,None, useTransitions=False)

    def getCompositeMode(self):
        return self.compositeMode

    def getComposite(self):
        return str(CompositeCommand(self.compositeMode, self.sourceA, self.sourceB))

    def setOverlay(self, location):
        if self.overlay:
            self.overlay.set(location)

    def showOverlay(self, visible):
        if self.overlay:
            self.overlay.show(visible, self.getPlayTime())

    def getOverlay(self):
        if self.overlay:
            return self.overlay.get()
        return None

    def getOverlayVisible(self):
        if self.overlay:
            return self.overlay.visible()
        return False

    def showLogo1(self, visible):
        if self.logo1:
            self.logo1.show(visible, self.getPlayTime())

    def getLogo1Visible(self):
        if self.logo1:
            return self.logo1.visible()
        return False

    def showLogo2(self, visible):
        if self.logo2:
            self.logo2.show(visible, self.getPlayTime())

    def getLogo2Visible(self):
        if self.logo2:
            return self.logo2.visible()
        return False

    def set_dynamic_text(self, texto):
        if self.launched:
            self.log.info(f"Applying dynamic text 1: {texto}")
            elemento_texto = self.mixingPipeline.get_by_name('rotulo_dinamico')
            if elemento_texto:
                elemento_texto.set_property('text', str(texto))

    def set_dynamic_text_2(self, texto):
        if self.launched:
            self.log.info(f"Applying dynamic text 2: {texto}")
            elemento_texto = self.mixingPipeline.get_by_name('rotulo_dinamico_2')
            if elemento_texto:
                elemento_texto.set_property('text', str(texto))
