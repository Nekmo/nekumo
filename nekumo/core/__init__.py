import os
import gevent
from nekumo.servers.web import WebServer
from nekumo.utils.modules import get_module

__author__ = 'nekmo'


class Nekumo(object):
    def __init__(self, directory, debug=False):
        self.greenleets = []
        self.debug = debug
        self.directory = directory

    def loop(self):
        gevent.joinall(self.greenleets)

    def debug_server(self, server_name):
        server = get_module('nekumo.servers.%s.Server' % server_name)
        server = server(self, debug=self.debug)
        server.run()

    def start(self):
        nekumo_debug_server = os.environ.get('NEKUMO_DEBUG_SERVER')
        if nekumo_debug_server is not None:
            self.debug_server(nekumo_debug_server)
        else:
            greenleet = gevent.spawn(WebServer(self, debug=self.debug).run)
            self.greenleets.append(greenleet)
        return self

    def close(self):
        pass
