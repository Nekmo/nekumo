import datetime
import mimetypes
import threading
from operator import itemgetter
from time import sleep, time
from uuid import uuid4

import gevent
from flask import send_file, Response, abort

from nekumo.api import Video
from nekumo.plugins.chromecast.encoder import Encoder
from nekumo.utils.network import get_local_address

mimetypes.init()
CHROMECASTS_LIST_EXPIRATION = datetime.timedelta(seconds=60 * 60)
MAX_STREAMS = 8
streams = {}


def get_address(nekumo, path):
    port = nekumo.servers['web'].config['port']
    address = get_local_address()
    return 'http://{}:{}{}'.format(address, port, path)


class Chromecasts(list):
    last_update = None

    def __init__(self):
        super(Chromecasts, self).__init__()
        self.get_chromecasts()

    def update_chromecasts_list(self):
        import pychromecast
        self[:] = pychromecast.get_chromecasts()
        self.last_update = datetime.datetime.now()
        return self

    def get_chromecasts(self):
        if not self.last_update or self.last_update + CHROMECASTS_LIST_EXPIRATION > datetime.datetime.now():
            threading.Thread(target=self.update_chromecasts_list).start()
        return self

    def openers_format(self):
        return map(lambda x: {'name': x.device.friendly_name, 'id': x.uuid.hex, 'icon': 'cast',
                              'opener': 'chromecast', 'function': lambda node: self.play(x, node) },
                   self.get_chromecasts())

    def play(self, device, node):
        # Quito la app que ya estuviese abierta para evitar conflictos
        device.quit_app()
        encoder = Encoder(node.get_path(), extras={'hard_subs': True})
        file = encoder.encode()
        id = uuid4().hex
        mc = device.media_controller
        if file.endswith('.mkv'):
            # Chromecast soporta archivos Mkv si se renombran a mp4
            id += '.mp4'
        else:
            # Le pongo al archivo id la extensión del archivo resultante
            id += '.' + file.split('.')[-1]
        streams[id] = {'file': file, 'encoder': encoder, 'mc': mc, 'last_read': None, 'popen': encoder.popen,
                       'id': id}
        url = get_address(node.nekumo, '/.nekumo/plugins/chromecast/' + id)
        mimetype = mimetypes.guess_type(id)
        mc.play_media(url, mimetype[0], node.get_name())


chromecasts = Chromecasts()
Video.openers.append(chromecasts.openers_format)


class ChromeCastPlugin(object):
    def __init__(self):
        pass

    @classmethod
    def clean_streams(cls):
        """Para evitar ataques, intentar borrar los medios más antiguos
        """
        # Sólo tengo en cuenta aquellos streams que estén encodeando
        encoding_streams = list(filter(lambda x: x['popen'], streams.values()))
        if len(encoding_streams) >= MAX_STREAMS:
            stream = sorted(encoding_streams, key=itemgetter('last_read'))[0]
            cls.clean_stream(stream)

    @staticmethod
    def clean_stream(stream):
        stream['encoder'].clean()
        del streams[stream['id']]

    @classmethod
    def clean_all_streams(cls):
        for stream in streams.values():
            cls.clean_stream(stream)

    def play(self, filename):
        if filename not in streams:
            abort(404)
        stream = streams[filename]
        if not stream['popen']:
            stream['last_read'] = time()
            # No se está haciendo encodeo, así que se envía tal cual
            return send_file(stream['file'])
        self.clean_streams()

        def stream_yield():
            file = open(stream['file'], 'rb')
            while True:
                stream['last_read'] = time()
                data = file.read(1024 * 8)
                if not data and stream['popen'].poll():
                    return
                elif not data:
                    # Está tardando en encodear. Esperar un poco y reintentar
                    sleep(0.2)
                    continue
                yield data
        response = Response(stream_yield())
        response.headers['Content-Type'] = mimetypes.guess_type(filename)
        return response

    def start(self):
        from nekumo.servers.web.views import web_bp
        web_bp.add_url_rule('/.nekumo/plugins/chromecast/<filename>', 'chromecast', self.play)

    def stop(self):
        self.clean_all_streams()

Plugin = ChromeCastPlugin
