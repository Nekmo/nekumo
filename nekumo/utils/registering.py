__author__ = 'nekmo'


class Registering(type):
    def __init__(cls, name, bases, attrs):
        cls.methods = set()
        cls.methods_by_name = {}
        for base in bases:
            cls.methods.union(base.methods)
            cls.methods_by_name.update(base.methods_by_name)
        for name, attr in attrs.items():
            if getattr(attr, '__name__', None) != 'api_method':
                continue
            cls.methods.add(attr)
            cls.methods_by_name[name] = attr
        super().__init__(name, bases, attrs)


class RegisteringBase(metaclass=Registering):
    methods = set()
    methods_by_name = {}


# @method
def method(func):
    def api_method(name):
        return func(name)
    return api_method
