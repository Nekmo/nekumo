import os
import shutil
import re
from .strings import replaces, multiple_search

__author__ = 'nekmo'


class RestartRename(Exception):
    pass


def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


def replace_inside_file(name, **kwargs):
    data = open(name, 'rb').read()
    with open(name, 'wb') as f:
        for key, value in kwargs.items():
            data = re.sub(re.escape(key), value, data)
        f.write(data)


def all_nodes(directory, file_handler=None, dir_handler=None, file_result=False, dir_result=False):
    results = {}
    for root, dirs, files in os.walk(directory):
        if file_handler is not None:
            for name in files:
                filepath = os.path.join(root, name)
                result = file_handler(filepath)
                if file_result:
                    results[filepath] = result
        if dir_handler is not None:
            for name in dirs:
                dirpath = os.path.join(root, name)
                result = dir_handler(dirpath)
                if dir_result:
                    results[dirpath] = result
    return results


def all_files(directory, handler, file_result=False):
    return all_nodes(directory, handler, file_result=file_result)


def all_directories(directory, handler, dir_result=False):
    return all_nodes(directory, dir_handler=handler, dir_result=dir_result)


def rename(node, new_name):
    dirname, name = os.path.split(node)
    shutil.move(node, os.path.join(dirname, new_name))


def copy_template(src, dst, to_replace=None):
    if not to_replace:
        to_replace = {}

    def rename_directory(directory):
        filename = os.path.split(directory)[1]
        if not multiple_search(to_replace.keys(), filename):
            return
        rename(directory, replaces(filename, **to_replace))
        raise RestartRename
    copytree(src, dst)
    all_files(dst, lambda x: replace_inside_file(x, **to_replace))
    all_files(dst, lambda x: rename(x, replaces(os.path.split(x)[1], **to_replace)))
    while True:
        try:
            all_directories(dst, rename_directory)
        except RestartRename:
            pass
        else:
            break