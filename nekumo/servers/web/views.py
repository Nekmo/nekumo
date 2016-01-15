import os

from flask import Blueprint, render_template, send_from_directory, request, redirect, send_file, current_app
import gevent
from geventwebsocket.exceptions import WebSocketError
from werkzeug.exceptions import NotFound

from nekumo.api import Node
from nekumo.api.serializers import JsonSerializer
from nekumo.core.exceptions import InvalidNode, NekumoException, SerializerError
from nekumo.servers.web import NEKUMO_ROOT, WEBSOCKET_PATH, ANGULAR_MODULES

__author__ = 'nekmo'

web_bp = Blueprint('core', __name__, template_folder='templates')

STATIC_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
Serializer = JsonSerializer


@web_bp.route('/<path:path>')
@web_bp.route('/')
def index(path='/'):
    nekumo = current_app.nekumo
    modules = ANGULAR_MODULES.copy()
    modules += ['angularMoment', 'ui-notification', 'md.data.table']
    try:
        # Obtengo el nodo para saber si es un archivo o un directorio
        node = Node(nekumo, method='info', node=path).get_own_best_class()
    except InvalidNode:
        raise NotFound
    if node.type == 'dir' and not path.endswith('/'):
        return redirect(path + '/')
    elif node.type == 'file':
        return send_file(node(nekumo, path).get_path())
    return render_template('web/node.html', angular_modules=modules)


@web_bp.route('%s/static/<path:path>' % NEKUMO_ROOT)
def send_js(path):
    return send_from_directory(STATIC_DIRECTORY, path)


# API con identificadores únicos para seguir las peticiones (como Jabber).
@web_bp.route(WEBSOCKET_PATH)
def serve_api():
    if request.environ.get('wsgi.websocket'):
        ws = request.environ['wsgi.websocket']
        while True:
            try:
                message = ws.receive()
            except WebSocketError:
                return ''
            if message is None:
                continue
            try:
                stanza = Serializer.raw_to_best_stanza(current_app.nekumo, message)
            except SerializerError as e:
                ws.send(Serializer.serialize(e.serialize()))
                continue
            except NekumoException as e:
                # Se ha podido obtener el Stanza pero no era válido. Lo obtengo aunque no sea
                # válido, porque puede tener asociado el ID de la petición.
                data = Serializer.get_base_stanza(current_app.nekumo, message)
                ws.send(Serializer.serialize(e.serialize(data.id)))
                continue
            result = gevent.spawn(stanza.execute)
            # Enviar el resultado cuando haya terminado
            result.link(lambda x: ws.send(x.value))