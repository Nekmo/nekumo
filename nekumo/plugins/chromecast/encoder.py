import logging
import shutil
import tempfile
import warnings
import copy
from uuid import uuid4

from subprocess import check_output, Popen
import xml.etree.ElementTree as ET

import os

TEMPDIR = tempfile.tempdir or '/tmp'
REPLACES = ['[', ']', '-']

if hasattr(shutil, 'which'):
    # Sólo está soportado en Python +3.3
    if not shutil.which('ffmpeg'):
        warnings.warn('Ffmpeg is not installed, and is required for encoder.', UserWarning)
    if not shutil.which('mediainfo'):
        warnings.warn('Mediainfo is not installed, and is required for encoder.', UserWarning)


def escape_name(name):
    for replace in REPLACES:
        name = name.replace(replace, '\\' + replace)
    return name

class Encoder(object):
    popen = None
    output_encode = None
    validation = {
        'video': {
            'bit_depths': ['8 bits'],
            'codecs': ['h264', 'vp8'],
        }
    }

    def __init__(self, input_file, extras=None):
        self._mediainfo = None
        self.input_file = input_file
        self.extras = extras or {}

    def mediainfo(self):
        if self._mediainfo:
            return self._mediainfo
        files = ET.fromstring(check_output(['mediainfo', '--Output=XML', self.input_file])).findall('File')
        if not len(files):
            self._mediainfo = None
        else:
            if len(files) > 1:
                logging.warning('More than a file in encoder for {}'.format(self.input_file))
            self._mediainfo = files[0]
        return self._mediainfo

    def get_video_info(self):
        info = self.mediainfo()
        if not info:
            return
        videos = info.findall('track[@type=\'Video\']')
        if len(videos):
            return videos[0]
        return

    def get_subtitles(self):
        info = self.mediainfo()
        return info.findall('track[@type=\'Text\']')

    def incompatibilities(self):
        incompatibilities = set()
        # if self.input_file.endswith('.mkv'):
        #     incompatibilities.add(['extension'])
        video = self.get_video_info()
        extras = self.get_extras()
        if video and video.find('Bit_depth').text not in self.validation['video']['bit_depths']:
            # Es un vídeo de 10 bits o superior
            incompatibilities.add('video')
        if video and video.find('Title').text not in self.validation['video']['codecs']:
            # El codec no es válido
            incompatibilities.add('video')
        if 'hard_subs' in extras:
            incompatibilities.add('video')
        return incompatibilities

    def get_extras(self):
        extras = copy.deepcopy(self.extras)
        if extras.get('hard_subs') and not len(self.get_subtitles()):
            extras.pop('hard_subs')
        return extras

    def args_extras(self, extras=None):
        extras = extras or self.get_extras()
        args_extras = []
        if 'hard_subs' in extras:
            args_extras.extend(['-vf',  'subtitles={}'.format(escape_name(self.input_file))])
        return args_extras

    def clean(self):
        if self.popen:
            self.popen.kill()
        if self.output_encode:
            os.remove(self.output_encode)

    def encode(self):
        incompatibilities = self.incompatibilities()
        if not incompatibilities:
            # No es necesario encodear
            return self.input_file
        args = ['ffmpeg', '-i', self.input_file, '-y', '-movflags', 'faststart', '-flags', 'global_header',
                '-f', 'matroska']
        # Vídeo
        args.extend(['-c:v', 'libx264' if 'video' in incompatibilities else 'copy'])
        # Audio
        args.extend(['-c:a', 'libfdk_aac' if 'audio' in incompatibilities else 'copy'])
        # Extras
        args.extend(self.args_extras())
        # Output
        output = os.path.join(TEMPDIR, uuid4().hex + '.mkv')
        args.extend([output])
        self.popen = Popen(args)
        self.output_encode = output
        return output
