__author__ = 'nekmo'


def clear_start_path(node):
    if node.startswith('/'):
        node = node[1:]
    return node


def clear_end_path(node):
    if node.endswith('/'):
        node = node[:-1]
    return node