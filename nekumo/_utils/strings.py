# coding=utf-8
import sys
try:
    import ushlex as shlex
except ImportError:
    if sys.version_info.major < 3:
        import warnings
        warnings.warn("Ushlex is not installed. Shlex not support Unicode!", ImportWarning)
    import shlex

import re
from nekumo.utils.ints import get_int

if sys.version_info.major >= 3:
    unicode = str

__author__ = 'nekmo'


def long_message(message, newlines=1, length=140):
    if not isinstance(message, (str, unicode)):
        try:
            message = str(message)
        except (UnicodeDecodeError, UnicodeEncodeError):
            message = unicode(message)
    if len(message) > length:
        return True
    if len(message.split('\n')) - 1 > newlines:
        return True
    return False


def split_arguments(body):
    """Dividir una cadena de texto en un listado de argumentos como en un shell.
    """
    # Sustituyo todas las comillas sencillas entre palabras por car \x00 para luego
    # devolverlo a su original. Hago esto, porque seguramente sea un apóstrofe como
    # los usados en inglés.
    body = re.sub(r"([^\A ])\'([^\Z ])", "\\1\x00\\2", body)
    args = shlex.split(body)
    args = map(lambda x: x.replace('\x00', "'"), args)
    return args


def find_occurrences(key, text):
    return map(lambda x: x.start(), re.finditer(re.escape(key), text))


def multiple_search(keys, text, *args):
    return re.findall('(%s)' % '|'.join(map(re.escape, keys)), text, *args)


def limit_context(key, text, chars_context=10, limiter='[...]'):
    results = []
    for occurrence in find_occurrences(key, text):
        part_a = text[get_int(occurrence - chars_context, 0):occurrence]
        part_b = text[occurrence + len(key):get_int(occurrence + len(key) + chars_context, len(text))]
        results.append('{limiter}%s{key}%s{limiter}'.format(**locals()) % (part_a, part_b))
    return ' '.join(results)


def highlight_occurrence(text, occurrence, char='*'):
    return re.sub('(%s)' % re.escape(occurrence), r'{char}\1{char}'.format(char=char), text)


def in_str_no_case(term, text):
    return bool(re.findall(re.escape(term), text, re.IGNORECASE))


def replaces(text, **kwargs):
    for key, value in kwargs.items():
        text = text.replace(key, value)
    return text