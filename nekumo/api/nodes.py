# coding=utf-8
import mimetypes
import os
import shutil

from hachoir.metadata import extractMetadata
from hachoir.parser import createParser

from nekumo.api.base import API, Response
from nekumo.api.decorators import method
from nekumo.core.exceptions import InvalidNode
from nekumo.utils.nodes import clear_end_path
from nekumo.utils.filesystem import copytree

__author__ = 'nekmo'
DIRECTORY_MIMETYPE = 'inode/directory'

mimetypes.init()


class Node(API):
    default_element_key = 'node'
    default_list_key = 'nodes'
    type = 'node'

    def _copy(self, dest, override=False):
        path = self.get_path()
        name = self.get_name()
        dest = self.get_path(dest, relative=False)
        if os.path.exists(dest) and os.path.isdir(dest) and not override:
            # Si existe el destino, es un directorio y no está parametrado para sobrecribir, entonces tomamos el
            # nombre del origen y lo concatenamos al destino.
            dest = os.path.join(dest, name)
        return path, dest

    @staticmethod
    def is_capable(stanza):
        return os.path.exists(stanza.get_path())

    def get_name(self):
        return clear_end_path(self.node).split('/')[-1]

    @method
    def move(self, dest, override=False):
        # TODO: renombrar override como "overwrite".
        path = self.get_path()
        dest = self.get_path(dest, False)
        # name = self.get_name()
        # TODO overwrite: http://stackoverflow.com/questions/31813504/move-and-replace-if-same-file-name-already-existed
        # -in-python
        shutil.move(path, dest)

    @method
    def info(self):
        path = self.get_path()
        return Response(self, name=self.get_name(), mtime=os.path.getmtime(path), size=os.path.getsize(path),
                        type=self.type, node=self.node, mimetype=self.get_mimetype())

    def get_mimetype(self):
        if self.type == 'dir':
            return DIRECTORY_MIMETYPE
        else:
            return mimetypes.guess_type(self.node)[0]


    def get_default_new_stanza(self, status=None, end=None):
        if self.method not in ['rm']:
            info = self.info()
        else:
            # Cuando es una petición de borrado, no debe entregarse la información del archivo.
            info = Response(self, node=self.node)
        info.update({'status': status or self.status, 'end': end or self.end})
        return info

    @method
    def extended_info(self):
        return []


class Dir(Node):
    deep = 0
    type = 'dir'

    @staticmethod
    def is_capable(stanza):
        return os.path.isdir(stanza.get_path())

    @method
    def count(self):
        walker = os.walk(self.get_path())
        dirs_count = 0
        files_count = 0
        cont = True
        while cont is not None:
            cont, dirs, files = next(walker, (None, (), ()))
            dirs_count += len(dirs)
            files_count += len(files)
        return Response(dirs=dirs_count, files=files_count)

    @method
    def ls(self, deep=0):
        # Cambiar nombre a list
        self.deep = deep
        try:
            nodes = os.listdir(self.get_path())
        except PermissionError:
            return self.info()
        nodes = filter(lambda x: x is not None, map(lambda x: self._get_node(x), nodes))
        return nodes

    @method
    def copy(self, dest, override=False):
        copytree(*self._copy(dest, override))

    @method
    def rm(self):
        # Cambiar por Remove
        shutil.rmtree(self.get_path())

    def _get_node(self, node_path):
        node = Node(self.nekumo, self.get_relative_path(node_path))
        try:
            stanza_class = self.get_best_class(node)
        except InvalidNode:
            return
        except PermissionError:
            # TODO: Será necesario devolver un error dentro de un propio listado.
            return
        result = stanza_class(self.nekumo, self.get_relative_path(node_path),
                              method='ls' if stanza_class is Dir and self.deep else 'info')
        if stanza_class is Dir:
            result.deep = (self.deep - 1) if self.deep else 0
        return result


class File(Node):
    type = 'file'

    @staticmethod
    def is_capable(stanza):
        return os.path.isfile(stanza.get_path())

    @method
    def copy(self, dest, override):
        shutil.copyfile(*self._copy(dest))

    @method
    def rm(self):
        os.remove(self.get_path())

    @method
    def extended_info(self):
        parser = createParser(self.get_path())
        if parser is None:
            return []
        try:
            metadata = extractMetadata(parser)
        except Exception as err:
            metadata = None
        if metadata is None:
            return []
        info = map(lambda x: {'description': x.description, 'values': [val.text for val in x.values]},
                   filter(lambda y: y.values, metadata._Metadata__data.values()))
        return Response(self, info=info)



class Image(File):
    @staticmethod
    def is_capable(stanza):
        # TODO: hacer esto más eficiente
        return os.path.isfile(stanza.get_path()) and \
               (mimetypes.guess_type(stanza.get_path())[0] or '').startswith('image/')