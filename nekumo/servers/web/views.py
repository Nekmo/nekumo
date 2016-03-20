import os

import gevent
from flask import Blueprint, render_template, send_from_directory, request, redirect, send_file, current_app
from werkzeug.exceptions import NotFound

from geventwebsocket.exceptions import WebSocketError
from nekumo.api import Node
from nekumo.api.serializers import JsonSerializer
from nekumo.core.exceptions import InvalidNode, NekumoException, SerializerError
from nekumo.servers.web import NEKUMO_ROOT, WEBSOCKET_PATH, ANGULAR_MODULES, get_user, has_perms, WebRequest

__author__ = 'nekmo'

web_bp = Blueprint('core', __name__, template_folder='templates')

STATIC_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
Serializer = JsonSerializer


def execute(stanza):
    def call():
        try:
            return stanza.execute()
        except NekumoException as e:
            return Serializer.serialize(e.serialize())
    return call


@web_bp.route('/<path:path>')
@web_bp.route('/')
def index(path='/'):
    has_perms('read')
    nekumo = current_app.nekumo
    modules = ANGULAR_MODULES.copy()
    modules += ['angularMoment', 'ui-notification', 'md.data.table']
    user = get_user()
    try:
        # Obtengo el nodo para saber si es un archivo o un directorio
        node = Node(nekumo, method='info', node=path).get_own_best_class()
    except InvalidNode:
        raise NotFound
    if node.type == 'dir' and not path.endswith('/'):
        return redirect(path + '/')
    elif node.type == 'file' and not 'preview' in request.args:
        return send_file(node(nekumo, path).get_path())
    elif node.type == 'api':
        # TODO: Provisional
        import json
        return json.dumps(node(nekumo, path).read())
    return render_template('web/node.html', angular_modules=modules, debug=current_app.config['DEBUG'],
                           is_admin=user.has_perm('admin'),
                           show_quickstart=current_app.nekumo.config.get('show_quickstart', False))


@web_bp.route('%s/static/<path:path>' % NEKUMO_ROOT)
def send_js(path):
    return send_from_directory(STATIC_DIRECTORY, path)


# API con identificadores únicos para seguir las peticiones (como XMPP).
@web_bp.route(WEBSOCKET_PATH)
def serve_api():
    if request.environ.get('wsgi.websocket'):
        ws = request.environ['wsgi.websocket']
        nekumo_request = WebRequest()
        while True:
            try:
                message = ws.receive()
            except WebSocketError:
                return ''
            if message is None:
                continue
            try:
                stanza = Serializer.raw_to_best_stanza(current_app.nekumo, message, nekumo_request)
            except SerializerError as e:
                ws.send(Serializer.serialize(e.serialize()))
                continue
            except NekumoException as e:
                # Se ha podido obtener el Stanza pero no era válido. Lo obtengo aunque no sea
                # válido, porque puede tener asociado el ID de la petición.
                data = Serializer.get_base_stanza(current_app.nekumo, message)
                ws.send(Serializer.serialize(e.serialize(data.id)))
                continue
            result = gevent.spawn(execute(stanza))
            # Enviar el resultado cuando haya terminado
            result.link(lambda x: ws.send(x.value))
