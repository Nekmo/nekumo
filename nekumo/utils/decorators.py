import functools
import inspect


def optional_args(func):
    """Allow to use decorator either with arguments or not.
    """

    def is_func_arg(*args, **kw):
        return len(args) == 1 and len(kw) == 0 and (
            inspect.isfunction(args[0]) or isinstance(args[0], type))

    if isinstance(func, type):
        def class_wrapper(*args, **kw):
            if is_func_arg(*args, **kw):
                return func()(*args, **kw)  # create class before usage
            return func(*args, **kw)

        class_wrapper.__name__ = func.__name__
        class_wrapper.__module__ = func.__module__
        return class_wrapper

    @functools.wraps(func)
    def func_wrapper(*args, **kw):
        if is_func_arg(*args, **kw):
            return func(*args, **kw)

        def functor(user_func):
            return func(user_func, *args, **kw)

        return functor

    return func_wrapper
