import os
import glob
import logging
from configparser import SafeConfigParser, DuplicateSectionError
from lib.args import Args

__all__ = ['Config']

Config = None


class VocConfigParser(SafeConfigParser):
    def __init__(self):
        super().__init__()
        self.default_insert = None
        self.log = logging.getLogger('ConfigParser')

    def getlist(self, section, option):
        if not self.has_option(section, option):
            return []
        option_val = self.get(section, option).strip()
        if len(option_val) == 0:
            return []

        unfiltered = [x.strip() for x in option_val.split(',')]
        return list(filter(None, unfiltered))

    def add_section_if_missing(self, section):
        try:
            self.add_section(section)
        except DuplicateSectionError:
            pass

    def hasOverlay(self):
        """Return True if the [overlay] section is present in the config."""
        return self.has_section('overlay')

    def getOverlayFile(self):
        """Return the default overlay filename if configured."""
        if self.has_option('overlay', 'file'):
            return self.getOverlayNameFromFilePath(self.get('overlay', 'file'))
        return None

    def getOverlaysPath(self):
        """Return the absolute path to the overlay images directory."""
        if self.has_option('overlay', 'path'):
            return os.path.abspath(self.get('overlay', 'path'))
        return os.getcwd()

    def getOverlayFilePath(self, overlay):
        """Convert an overlay name to an absolute PNG file path."""
        if not overlay:
            return None
        filename, name = overlay.split("|") if "|" in overlay else (overlay, None)
        filename = filename + ".png" if filename and (len(filename) < 4 or filename[-4:].lower() != ".png") else filename
        return os.path.join(self.getOverlaysPath(), filename)

    def getOverlayNameFromFilePath(self, filepath):
        """Extract the overlay name from its absolute file path."""
        if not filepath:
            return None
        filepath, name = filepath.split("|") if '|' in filepath else (filepath, None)
        filename = filepath.replace(self.getOverlaysPath() + os.sep, "")
        filename = filename[:-4] if filename and len(filename) > 4 and filename[-4:].lower() == ".png" else filename
        return "|".join((filename, name)) if name else filename

    def getOverlayFiles(self):
        """Return a sorted list of available overlay PNG files.

        Priority: explicit order from the .ini [overlay] files option,
        then alphabetical scan of the overlay directory.
        """
        inserts = []
        folder_path = self.getOverlaysPath()

        # Explicit order from the .ini takes highest priority
        if self.has_option('overlay', 'files'):
            manual_inserts = [self.getOverlayNameFromFilePath(o) for o in self.getlist('overlay', 'files')]
            for o in manual_inserts:
                if o not in inserts:
                    inserts.append(o)

        # Fall back to alphabetical directory scan
        if os.path.isdir(folder_path):
            png_files = sorted(glob.glob(os.path.join(folder_path, '*.png')))
            for f in png_files:
                name = self.getOverlayNameFromFilePath(f)
                if name not in inserts:
                    inserts.append(name)
        else:
            self.log.error(f"Overlay path '{folder_path}' is not a valid directory.")

        # Append the default file if not already included
        if self.getOverlayFile():
            name = self.getOverlayNameFromFilePath(self.getOverlayFile())
            if name not in inserts and name is not None:
                inserts.append(name)

        # Filter out entries whose image files do not exist on disk
        valid = []
        for i in inserts:
            filename = self.getOverlayFilePath(i.split('|')[0])
            if filename is not None and os.path.isfile(filename):
                valid.append(i)
            else:
                self.log.error("Could not find overlay image file '%s'." % filename)

        if valid:
            self.default_insert = valid[0]
            self.log.info('found %d insert(s): %s', len(valid), ",".join([i for i in valid]))
        else:
            self.default_insert = None
            self.log.warning('Could not find any available overlays in configuration.')

        return valid

    def getOverlayBlendTime(self):
        if self.has_option('overlay', 'blend-time'):
            return int(self.get('overlay', 'blend-time'))
        elif self.has_option('overlay', 'blend'):
            return int(self.get('overlay', 'blend'))
        return 300

    def getOverlayAutoOff(self):
        return self.getboolean('overlay', 'auto-off', fallback=True)

    def getOverlayUserAutoOff(self):
        return self.getboolean('overlay', 'user-auto-off', fallback=True)

    def getOverlaysTitle(self):
        return None

    def hasLogo1(self):
        return self.has_section('logo1')

    def getLogo1File(self):
        if self.has_option('logo1', 'file'):
            return self.get('logo1', 'file')
        return None

    def getLogo1BlendTime(self):
        if self.has_option('logo1', 'blend-time'):
            return int(self.get('logo1', 'blend-time'))
        return 300

    def hasLogo2(self):
        return self.has_section('logo2')

    def getLogo2File(self):
        if self.has_option('logo2', 'file'):
            return self.get('logo2', 'file')
        return None

    def getLogo2BlendTime(self):
        if self.has_option('logo2', 'blend-time'):
            return int(self.get('logo2', 'blend-time'))
        return 300


def load():
    global Config
    files = [
        os.path.join(os.path.dirname(os.path.realpath(__file__)),
                     '../default-config.ini'),
        os.path.join(os.path.dirname(os.path.realpath(__file__)),
                     '../config.ini'),
        '/etc/voctomix/voctocore.ini',
        '/etc/voctomix.ini',  # deprecated
        '/etc/voctocore.ini',
        os.path.expanduser('~/.voctomix.ini'),  # deprecated
        os.path.expanduser('~/.voctocore.ini'),
    ]

    if Args.ini_file is not None:
        files.append(Args.ini_file)

    Config = VocConfigParser()
    readfiles = Config.read(files)

    log = logging.getLogger('ConfigParser')
    log.debug('considered config-files: \n%s',
              "\n".join([
                  "\t\t" + os.path.normpath(file)
                  for file in files
              ]))
    log.debug('successfully parsed config-files: \n%s',
              "\n".join([
                  "\t\t" + os.path.normpath(file)
                  for file in readfiles
              ]))

    if Args.ini_file is not None and Args.ini_file not in readfiles:
        raise RuntimeError('explicitly requested config-file "{}" '
                           'could not be read'.format(Args.ini_file))
