import os
import shutil
import tempfile

from fabric.context_managers import lcd, prefix
from fabric.operations import local

__dir__ = os.path.abspath(os.path.dirname(__file__))
web_path = os.path.join(__dir__, 'nekumo', 'servers', 'web')
virtualenv_dir = os.path.join(tempfile.tempdir or '/tmp', 'venv')


def grunt():
    with lcd(web_path):
        # Comprobar que no haya dependencias pendientes
        local('npm install')
        local('grunt')


def build():
    grunt()


def _start_virtual_build(params=''):
    """Para depuración. Crea un virtualenv e instala Nekumo para pruebas.
    """
    if os.path.lexists(virtualenv_dir):
        shutil.rmtree(virtualenv_dir)
    local('virtualenv {}'.format(virtualenv_dir))
    with prefix('source "{}/bin/activate"'.format(virtualenv_dir)):
        local('python {}/setup.py {}'.format(__dir__, params))


def start_virtual_build():
    _start_virtual_build('install')


def start_virtual_build_develop():
    _start_virtual_build('develop')


def _pypi(repo):
    build()
    with lcd(__dir__):
        local('python setup.py register -r "{}"'.format(repo))
        local('python setup.py sdist upload -r "{}"'.format(repo))


def pypi():
    _pypi('pypi')


def pypitest():
    _pypi('pypitest')
