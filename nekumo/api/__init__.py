from nekumo.api.nodes import Dir, File, Node

__author__ = 'nekmo'


stanza_classes = [
    # Este listado se recorre para determinar el tipo de clase mejor a usar
    # con un nodo. Se usa un método estático is_capable para determinarlo.
    # Por ejemplo, tendremos clases Dir y File, con métodos distintos.
    Dir,
    File,
    Node,
]