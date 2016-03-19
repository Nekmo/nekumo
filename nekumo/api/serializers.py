import json
from nekumo.api.base import API
from nekumo.core.exceptions import SerializeError, InvalidJson, NekumoException

__author__ = 'nekmo'


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (map, filter)):
            return list(obj)
        if isinstance(obj, API):
            return obj.execute()
        if isinstance(obj, NekumoException):
            return obj.serialize()
        if isinstance(obj, bytes):
            return obj.decode('utf-8')
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)


class JsonSerializer(API):

    @classmethod
    def raw_to_best_stanza(cls, nekumo, data):
        data = cls.deserialize(data)
        stanza = cls.get_base_stanza(nekumo, data, False)
        stanza_class = cls.mix_api_class(cls.get_best_class(stanza))
        return stanza_class(nekumo, **data)

    @classmethod
    def mix_api_class(cls, api_class):
        class JsonMixedClass(cls, api_class):
            pass
        return JsonMixedClass

    # @classmethod
    # def get_best_class(cls, stanza):
    #     return cls.mix_api_class(super().get_best_class(stanza))

    @staticmethod
    def serialize(data):
        try:
            result = json.dumps(data, cls=Encoder)
            return result
        except ValueError:
            raise SerializeError()

    @staticmethod
    def deserialize(data):
        try:
            return json.loads(data)
        except ValueError:
            raise InvalidJson()

    @classmethod
    def get_base_stanza(cls, nekumo, data, from_raw=True):
        if from_raw:
            data = cls.deserialize(data)
        return JsonSerializer(nekumo, **data)