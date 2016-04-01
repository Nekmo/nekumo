import unittest
from nekumo.core.pubsub import PubSubNode, Listener, Event


class TestPubSub(unittest.TestCase):
    def test_get_subnode_key_error(self):
        """Acceder a un nodo no existente sin create debe fallar.
        """
        root = PubSubNode()
        with self.assertRaises(KeyError):
            root.get_subnode('/foo/bar/spam')

    def test_get_subnode_create(self):
        """Acceder a un nodo no existente con create debe crear
        la ruta completa.
        """
        path = '/foo/bar/spam'
        root = PubSubNode()
        root.get_subnode(path, True)
        try:
            node = root.get_subnode(path)
        except KeyError:
            self.fail('get_node() has not created subnode!')
        self.assertEqual(node.path, path)

    def test_fire_event(self):
        """Hacer fire de un evento a una ruta con un listener en dicha ruta, debe
        ejecutarlo.
        """
        root = PubSubNode()
        path = '/foo/bar/spam'
        root.register(path, Listener(lambda x: x))
        self.assertEqual(len(root.fire(path, Event())), 1)

    def test_fire_nonexistent(self):
        """Se ejecuta un nodo que no existe.
        """
        root = PubSubNode()
        root.register('/foo/bar', Listener(lambda x: x))
        self.assertEqual(len(root.fire('/foo/bar/spam', Event())), 0)

    def test_no_fire(self):
        """No debe ejecutarse el listener de un nodo padre cuando
        el que se está ejecutando es el de un hijo.
        """
        root = PubSubNode()
        root.register('/foo/bar/spam', Listener(lambda x: x))
        root.register('/foo/bar', Listener(lambda x: x))
        self.assertEqual(len(root.fire('/foo/bar/spam', Event())), 1)

    def test_fire_recursive(self):
        """Si se está ejecutando un evento para un nodo hijo, el de un nodo
        padre debe ejecutarse si éste tiene el parámetro recursive.
        """
        root = PubSubNode()
        root.register('/foo/bar', Listener(lambda x: x, recursive=True))
        self.assertEqual(len(root.fire('/foo/bar/spam', Event())), 1)

    def subscribe_root(self):
        """Suscribirse a root con un espacio vacío o el mismo separados debe ser válido, y
        no deben crearse subnodos.
        """
        root = PubSubNode()
        root.register('', Listener(lambda x: x))
        root.register('/', Listener(lambda x: x))
        self.assertEqual(len(root.listeners), 2)
        self.assertEqual(len(root), 0)
        self.assertEqual(len(root.fire('/', Event())), 2)
        self.assertEqual(len(root.fire('', Event())), 2)




if __name__ == '__main__':
    unittest.main()
