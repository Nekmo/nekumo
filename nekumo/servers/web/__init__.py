import os
from flask import Flask, request, current_app, session, abort
from gevent.pywsgi import WSGIServer
import werkzeug.serving
import werkzeug.wrappers
import werkzeug.routing
from werkzeug.debug import DebuggedApplication

from config import WebConfig
from geventwebsocket.handler import WebSocketHandler
from nekumo.api.base import BaseRequest

__author__ = 'nekmo'

NEKUMO_ROOT = '/.nekumo'
WEBSOCKET_PATH = os.path.join(NEKUMO_ROOT, 'ws')
ANGULAR_MODULES = ['ngWebSocket', 'ngMaterial', 'ngMdIcons', 'mdColors', 'mdDialogMessage', 'ngSanitize',
                   'oc.lazyLoad']


# PATCH: Hay una función en werkzeug (wsgi_decoding_dance en _compat) que intenta reconvertir la url
# de forma incorrecta. Debe devolverse tal cual.
def _wsgi_decoding_dance(s, charset='utf-8', errors='replace'):
    return s

setattr(werkzeug.wrappers, 'wsgi_decoding_dance', _wsgi_decoding_dance)
setattr(werkzeug.routing, 'wsgi_decoding_dance', _wsgi_decoding_dance)


def get_user():
    users = current_app.nekumo.config.users
    if session.get('username') in users and session.get('security_hash') == users[session['username']].security_hash:
        return users[session['username']]
    address = request.remote_addr
    user = users.address_login(address)
    if user:
        session['username'] = user.username
        session['security_hash'] = user.security_hash
        session.permanent = True
    return user


def has_perms(*perms):
    user = get_user()
    if user is None:
        abort(401)
    if not user.has_perms(*perms):
        abort(401)
    return True


class NekumoHandler(WebSocketHandler, werkzeug.serving.WSGIRequestHandler):
    log_request = werkzeug.serving.WSGIRequestHandler.log_request
    log_error = werkzeug.serving.WSGIRequestHandler.log_error
    log_message = werkzeug.serving.WSGIRequestHandler.log_message


class WebRequest(BaseRequest):
    def __init__(self):
        super().__init__()
        self.user = get_user()


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

    def __init__(self, nekumo, address_port=('0.0.0.0', 7070), debug=True):
        # debug = False
        self.nekumo = nekumo
        self.address = address_port[0]
        self.port = address_port[1]
        self.debug = debug
        self.app = self.get_app_flask(debug=debug)
        self.app.nekumo = self.nekumo
        self.app.web_server = self
        self.set_up_flask()
        self.config = WebConfig(os.path.join(self.nekumo.config_dir, 'servers', 'web',  'config.json'))

    def set_up_flask(self):
        from nekumo.servers.web.views import web_bp
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
        import binascii
        app.secret_key = binascii.hexlify(os.urandom(24))
        return app

    def _run(self):
        app = DebuggedWSApplication(self.app, True) if self.app.debug else self.app
        # self.app.logger.info('app starting up....')
        self.server = WSGIServer(
            (self.address, self.port),
            app,
            # handler_class=NekumoHandler
            handler_class=WebSocketHandler
        )
        self.server.serve_forever()

    def run(self):
        werkzeug.serving.run_with_reloader(self._run) if self.debug else self._run()


Server = WebServer
