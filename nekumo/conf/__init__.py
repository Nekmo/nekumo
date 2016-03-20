import json
import os

import copy

__author__ = 'nekmo'


class Field(object):
    def __call__(self, value):
        return self.parse(value)

    def parse(self, value):
        raise NotImplementedError


class IntegerField(Field):
    def parse(self, value):
        return int(value)


class BooleanField(Field):
    def parse(self, value):
        return bool(value)


class BaseParser(object):
    _key = None  # Si el padre es un diccionario, el key del mismo
    _parent = None  # El elemento padre
    parser = None
    config = None

    def save(self):
        self.config.save()


class ListParser(list, BaseParser):
    def __init__(self, parser=None, data=None, config=None):
        """
        :param parser: Con qué parseador se debe parsear cada elemento
        :param data: Datos con los que poblar los elementos
        :param config: Config raíz para poder usar método save()
        :return:
        """
        super().__init__()
        # TODO: debería validarse cada elemento de data
        self.extend(data or [])


class DictParser(dict, BaseParser):
    schema = None
    default = None

    def __init__(self, parser=None, data=None, config=None):
        self.config = config
        super().__init__()
        if data:
            self.update(data)
        self.default = self.default

    def __getattr__(self, item):
        if item in self:
            return self[item]
        elif item in (self.default or {}) and item in self.schema:
            return self.parse_schema_element(item, copy.deepcopy(self.default[item]))
        return self.__getattribute__(item)

    def parse_schema(self, data):
        new_data = {}
        for key, value in data.items():
            new_data[key] = self.parse_schema_element(key, value)
        return new_data

    def parse_schema_element(self, key, value):
        parser = self.parser or self.schema[key]
        if isinstance(parser, Field):
            return parser(value)
        else:
            element = parser(data=value, config=self.config)
            element._key = key
            element._parent = self
            return element

    def update(self, E=None, **F):
        new_data = self.parse_schema(E)
        return super(DictParser, self).update(new_data, **F)


class Config(DictParser):
    is_loaded = False
    default = None

    def __init__(self, config_file, default=None):
        super().__init__()
        self.config_file = config_file
        self.default = default or self.default or {}

    def __setitem__(self, key, value):
        self.load()
        return super(Config, self).__setitem__(key, value)

    def __getitem__(self, item):
        self.load()
        return super(Config, self).__getitem__(item)

    def __delitem__(self, key):
        self.load()
        return super(Config, self).__delitem__(key)

    def __getattr__(self, item):
        if item in ['is_loaded']:
            return self.__getattribute__(item)
        self.load()
        if item in self:
            return self[item]
        return self.__getattribute__(item)

    def load(self):
        if self.is_loaded:
            return
        self.is_loaded = True
        self.clear()
        if os.path.exists(self.config_file):
            self.update(json.load(open(self.config_file, 'r')))
        else:
            default = copy.deepcopy(self.default)
            self.save(default)
            self.update(default)
        return self

    def save(self, data=None):
        config_dir = os.path.dirname(self.config_file)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        json.dump(data or self, open(self.config_file, 'w'))
