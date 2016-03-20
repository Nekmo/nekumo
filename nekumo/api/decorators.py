from nekumo.core.exceptions import SecurityError
from nekumo.utils.decorators import optional_args

__author__ = 'nekmo'


def has_perms(*perms):
    def perms_decorator(func):
        def func_wrapper(self, *args, **kwargs):
            if not self.request.user.has_perms(*perms):
                raise SecurityError('Security Error')
            return func(self, *args, **kwargs)
        return func_wrapper
    return perms_decorator


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
