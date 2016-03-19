import os

from fabric.context_managers import lcd
from fabric.operations import local

__dir__ = os.path.abspath(os.path.dirname(__file__))
web_path = os.path.join(__dir__, 'nekumo', 'servers', 'web')


def grunt():
    with lcd(web_path):
        # Comprobar que no haya dependencias pendientes
        local('npm install')
        local('grunt')


def build():
    grunt()


def _pypi(repo):
    build()
    with lcd(__dir__):
        local('python setup.py register -r "{}"'.format(repo))
        local('python setup.py sdist upload -r "{}"'.format(repo))


def pypi():
    _pypi('pypi')


def pypitest():
    _pypi('pypitest')
