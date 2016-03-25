import datetime
import mimetypes
import threading
from time import sleep
from uuid import uuid4

import gevent
from flask import send_file, Response

from nekumo.api import Video
from nekumo.plugins.chromecast.encoder import Encoder
from nekumo.utils.network import get_local_address

mimetypes.init()
CHROMECASTS_LIST_EXPIRATION = datetime.timedelta(seconds=60 * 60)
encoders = {}


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
        encoder = Encoder(node.get_path())
        file = encoder.encode()
        id = uuid4().hex
        if file.endswith('.mkv'):
            # Chromecast soporta archivos Mkv si se renombran a mp4
            id += '.mp4'
        else:
            # Le pongo al archivo id la extensión del archivo resultante
            id += '.' + file.split('.')[-1]
        encoders[id] = file
        url = get_address(node.nekumo, '/.nekumo/plugins/chromecast/' + id)
        mimetype = mimetypes.guess_type(id)
        mc = device.media_controller
        sleep(5)
        mc.play_media(url, mimetype[0], node.get_name())


chromecasts = Chromecasts()
Video.openers.append(chromecasts.openers_format)


class ChromeCastPlugin(object):
    def __init__(self):
        pass

    def play(self, filename):
        def stream():
            file = open(encoders[filename], 'rb')
            while True:
                data = file.read(1024 * 8)
                if not data:
                    return
                yield data
        response = Response(stream())
        response.headers['Content-Type'] = mimetypes.guess_type(filename)
        return response

    def start(self):
        from nekumo.servers.web.views import web_bp
        web_bp.add_url_rule('/.nekumo/plugins/chromecast/<filename>', 'chromecast', self.play)

Plugin = ChromeCastPlugin
