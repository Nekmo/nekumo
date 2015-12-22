import os
from flask import Flask, request
from gevent.pywsgi import WSGIServer
import werkzeug.serving
from werkzeug.debug import DebuggedApplication
from geventwebsocket.handler import WebSocketHandler

__author__ = 'nekmo'

NEKUMO_ROOT = '/.nekumo'
WEBSOCKET_PATH = os.path.join(NEKUMO_ROOT, 'ws')
ANGULAR_MODULES = ['ngWebSocket', 'ngMaterial', 'ngMdIcons', 'mdColors', 'mdDialogMessage']


def get_app_flask(name=None, debug=False, flask_class=Flask):
    if name is None:
        name = __name__
    print(name)
    app = flask_class(name)
    app.debug = debug
    return app


class NekumoHandler(WebSocketHandler, werkzeug.serving.WSGIRequestHandler):
    log_request = werkzeug.serving.WSGIRequestHandler.log_request
    log_error = werkzeug.serving.WSGIRequestHandler.log_error
    log_message = werkzeug.serving.WSGIRequestHandler.log_message


class DebuggedWSApplication(DebuggedApplication):
    def __call__(self, environ, start_response):
        if environ.get('wsgi.websocket'):
            return self.app(environ, start_response)
        return super().__call__(environ, start_response)


class WebServer(object):
    # Aquellos parámetros que usted puede sobrescribir sin miedo
    default_globals = {
        'nekumo_root': NEKUMO_ROOT,
        'angular_modules': ANGULAR_MODULES,
        'websocket_path': WEBSOCKET_PATH,
    }
    # Usted no debería cambiar nada de aquí. Son parámetros que serán establecidos
    # más adelante.
    app = None

    def __init__(self, nekumo, port=8000, debug=True):
        # debug = False
        self.nekumo = nekumo
        self.port = port
        self.debug = debug
        self.app = self.get_app_flask(debug=debug)
        self.app.nekumo = self.nekumo
        self.app.web_server = self
        self.set_up_flask()

    def set_up_flask(self):
        self.update_globals(self.default_globals)
        self.app.register_blueprint(web_bp)

    def update_globals(self, new_globals, app=None):
        if app is None:
            app = self.app
        app.jinja_env.globals.update(new_globals)

    @staticmethod
    def get_app_flask(name=None, debug=False, flask_class=Flask):
        if name is None:
            name = __name__
        app = flask_class(name)
        app.debug = debug
        return app

    def _run(self):
        app = DebuggedWSApplication(self.app, True) if self.app.debug else self.app
        # self.app.logger.info('app starting up....')
        self.server = WSGIServer(
            ('', self.port),
            app,
            # handler_class=NekumoHandler
            handler_class=WebSocketHandler
        )
        self.server.serve_forever()

    def run(self):
        werkzeug.serving.run_with_reloader(self._run) if self.debug else self._run()


Server = WebServer
from nekumo.servers.web.views import web_bp
