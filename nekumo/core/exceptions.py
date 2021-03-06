__author__ = 'nekmo'


class NekumoException(Exception):
    message = ''
    status = 'error'

    def __init__(self, message='', id_=None):
        self.message = message
        self.id_ = id_

    def get_message(self):
        msg = self.__class__ if not self.message else self.message
        return 'Error: %s' % msg

    def serialize(self, id_=None):
        response = {
            'status': self.status,
            'message': self.get_message(),
        }
        id_ = id_ or self.id_
        if id_ is not None:
            response['id'] = id_
        return response

class InvalidNode(NekumoException):
    pass


class SerializerError(NekumoException):
    pass


class InvalidJson(SerializerError):
    pass


class InvalidStanza(NekumoException):
    pass


class SerializeError(NekumoException):
    pass


class SecurityError(NekumoException):
    pass


class ProgrammingError(NekumoException):
    pass


class NekumoKeyError(NekumoException):
    pass


class BadRequestError(NekumoException):
    pass


class NekumoConnectionError(NekumoException):
    pass
