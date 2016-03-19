import os
from nekumo.core import Nekumo

from nekumo.core.exceptions import InvalidStanza, InvalidNode, NekumoException, SecurityError, ProgrammingError
from nekumo.utils.nodes import clear_start_path
from nekumo.utils.registering import RegisteringBase
from nekumo.api.decorators import method as method_decorator

__author__ = 'nekmo'


class API(RegisteringBase):
    default_list_key = 'items'
    default_element_key = 'item'
    default_dict_key = 'data'

    nekumo = None
    node = ''
    method = ''
    params = None
    status = 'success' # error, success, info, warning
    id = None
    end = True

    def __init__(self, nekumo, node='', method='', status='success', id=None, end=True, **params):
        if not isinstance(nekumo, Nekumo):
            raise AttributeError('Nekumo argument is not a Nekumo instance.')
        for param in set(locals()) - {'self'}:
            setattr(self, param, locals()[param])

    @method_decorator
    def exists(self):
        return Response(self, exists=os.path.exists(self.get_path())).set_update_stanza(False)

    def raise_invalid(self):
        if not self.is_valid():
            raise InvalidStanza('Stanza is invalid. Check fields.')

    def is_valid(self):
        return self.node is not None and self.method is not None

    def execute(self):
        if not self.method:
            raise InvalidStanza('Method is required.')
        params = self.params or {}
        method = getattr(self, self.method, None)
        if method is None:
            raise InvalidStanza('Invalid method \'{}\''.format(self.method), self.id)
        try:
            response = method(**params)
        except NekumoException as e:
            response = e
        return self.prepare_response(response)

    def prepare_response(self, response):
        if hasattr(self, 'reply'):
            response = self.reply(response)
        if hasattr(self, 'serialize'):
            response = self.serialize(response)
        return response

    def set_status(self, status):
        self.status = status

    def set_end(self, end):
        self.end = end

    def get_default_new_stanza(self, status=None, end=None):
        return {
            'id': self.id,
            'status': status or self.status,
            'end': end or self.end,
        }

    def reply(self, data, status=None, end=None):
        new_stanza = self.get_default_new_stanza(status, end)
        if isinstance(data, Response):
            new_stanza.update(data)
        elif isinstance(data, dict):
            new_stanza[self.default_dict_key] = data
        elif isinstance(data, (list, tuple, set, frozenset, filter, map)):
            new_stanza[self.default_list_key] = data
        elif data == None:
            pass
        else:
            new_stanza[self.default_element_key] = data
        return new_stanza

    def get_root(self):
        if self.nekumo is None:
            raise AttributeError('Nekumo instance is required in API.')
        return self.nekumo.directory

    def get_path(self, node=None, relative=True):
        if node is None:
            node = self.node
        elif node is not None and relative:
            node = os.path.join(self.node, clear_start_path(node))
        elif node is not None and not relative:
            pass
        else:
            raise ProgrammingError
        node = clear_start_path(node)
        path = os.path.join(self.get_root(), node)
        if not path.startswith(self.get_root()):
            raise SecurityError
        return path

    def get_relative_path(self, node):
        return clear_start_path(os.path.join(self.node, clear_start_path(node)))

    @staticmethod
    def is_capable(node):
        return False

    @classmethod
    def get_best_class(cls, stanza):
        # Selección dinámica del objeto de API a usar en función del nodo.
        from nekumo.api import stanza_classes
        for stanza_class in stanza_classes:
            # TODO: para cachear, en stanza debería haber un atrribute _cache con aquellos
            # valores obtenidos, como mimetype, etc.
            if stanza_class.is_capable(stanza):
                return stanza_class
        if stanza.method == 'exists':
            # Esta es la única excepción para devolver la stanza base: comprobar si el
            # propio nodo existe.
            return API
        raise InvalidNode('%s' % stanza.node)

    def get_own_best_class(self):
        return self.get_best_class(self)


class Response(dict):
    _update_stanza = True

    def __init__(self, stanza=None, **kwargs):
        super().__init__(**kwargs)
        if stanza is not None:
            self['id'] = stanza.id
            self['status'] = stanza.status
            self['method'] = stanza.method

    def set_update_stanza(self, update_stanza=True):
        self._update_stanza = update_stanza
        return self
