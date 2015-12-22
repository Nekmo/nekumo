__author__ = 'nekmo'

def get_int(value, min=None, max=None):
    if min is not None and value < min:
        return min
    elif max is not None and value > max:
        return max
    return value