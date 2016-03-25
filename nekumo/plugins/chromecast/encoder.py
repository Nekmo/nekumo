import logging
import shutil
import tempfile
import warnings
from uuid import uuid4

from subprocess import check_output, Popen
import xml.etree.ElementTree as ET

import os

TEMPDIR = tempfile.tempdir or '/tmp'


if hasattr(shutil, 'which'):
    # Sólo está soportado en Python +3.3
    if not shutil.which('ffmpeg'):
        warnings.warn('Ffmpeg is not installed, and is required for encoder.', UserWarning)
    if not shutil.which('mediainfo'):
        warnings.warn('Mediainfo is not installed, and is required for encoder.', UserWarning)


class Encoder(object):
    popen = None
    output_encode = None
    validation = {
        'video': {
            'bit_depths': ['8 bits'],
            'codecs': ['h264', 'vp8'],
        }
    }

    def __init__(self, input_file):
        self._mediainfo = None
        self.input_file = input_file

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

    def incompatibilities(self):
        incompatibilities = set()
        # if self.input_file.endswith('.mkv'):
        #     incompatibilities.add(['extension'])
        video = self.get_video_info()
        if video and video.find('Bit_depth').text not in self.validation['video']['bit_depths']:
            # Es un vídeo de 10 bits o superior
            incompatibilities.add('video')
        if video and video.find('Title').text not in self.validation['video']['codecs']:
            # El codec no es válido
            incompatibilities.add('video')
        # mediainfo --Output=XML source.mkv
        # Encodear (Cambiar ext mkv a mp4)
        # ffmpeg -i '[AU] Working!! 2 - 01 [BD][99EB9224].mkv' -c:a copy -c:v libx264 -y -movflags faststart -flags global_header -f matroska -vf subtitles=/tmp/source.mkv /tmp/video3.mp4
        return incompatibilities

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
        # Output
        output = os.path.join(TEMPDIR, uuid4().hex + '.mkv')
        args.extend([output])
        self.popen = Popen(args)
        self.output_encode = output
        return output