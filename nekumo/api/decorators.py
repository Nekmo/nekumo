from nekumo.utils.decorators import optional_args

__author__ = 'nekmo'


# @method
@optional_args
def method(func, *args, **kw):
    return func(*args, **kw)


@optional_args
class method:
    def __init__(self, *args, **kw):
        self.args = args
        self.kw = kw

    def __call__(self, func):
        def api_method(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            return result

        return api_method
