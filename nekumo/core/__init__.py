import os
import gevent

from nekumo.conf.nekumo_config import NekumoConfig
from nekumo.utils.modules import get_module

__author__ = 'nekmo'



class Nekumo(object):
    main_server = 'web'

    def __init__(self, directory, address_port, config_dir, debug=False):
        self.servers = {}
        self.plugins = {}
        self.greenleets = []
        self.debug = debug
        self.directory = directory
        # TODO: utilizar el config_dir para crear el directorio de configuración y cargarlo
        self.config_dir = config_dir
        self.config = self.get_config(os.path.join(self.config_dir, 'config.json'))
        self.address_port = address_port

    def get_config(self, config_file):
        return NekumoConfig(config_file)

    def init_plugins(self):
        for plugin_name in self.config.plugins:
            module = get_module('nekumo.plugins.{}.Plugin'.format(plugin_name))
            self.plugins[plugin_name] = module()

    def start_plugins(self):
        for plugin in self.plugins.values():
            plugin.start()

    def stop_plugins(self):
        for plugin in self.plugins.values():
            plugin.stop()

    def loop(self):
        gevent.joinall(self.greenleets)

    def debug_server(self, server_name):
        server = get_module('nekumo.servers.%s.Server' % server_name)
        server = server(self, debug=self.debug)
        self.servers[server_name] = server
        server.run()

    def start(self):
        self.init_plugins()
        nekumo_debug_server = os.environ.get('NEKUMO_DEBUG_SERVER')
        if nekumo_debug_server is not None:
            self.start_plugins()
            self.debug_server(nekumo_debug_server)
        else:
            from nekumo.servers.web import WebServer
            server = WebServer(self, debug=self.debug)
            self.servers['web'] = server
            greenleet = gevent.spawn(server.run)
            self.greenleets.append(greenleet)
            self.start_plugins()
        return self

    def close(self):
        self.stop_plugins()
