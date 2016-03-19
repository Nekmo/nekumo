import os
import logging
import socket
import sys

from nekumo.utils.filesystem import copytree, copy_template


__author__ = 'nekmo'
__dir__ = os.path.abspath(os.path.dirname(__file__))

nekumo_src_dir = os.path.dirname(os.path.dirname(__file__))
conf_src_dir = os.path.join(nekumo_src_dir, 'conf')
execution_directory = os.path.abspath('.')
nekumo_config_directory = os.path.join(execution_directory, '.nekumo')

DEFAULT_ADDRESS = '0.0.0.0'
DEFAULT_PORT = '7070'


def address_port(value):
    value = value.split(':')
    if len(value) > 2:
        raise ValueError('Please, use only one separator (":").')
    elif len(value) == 1:
        value = [DEFAULT_ADDRESS] + value
    if not value[1].isdigit():
        raise ValueError('The port must be a number')
    value[1] = int(value[1])
    if not value[1] < 2**16 and value[1] > 0:
        raise ValueError('The port must be in the range 1-65536')
    try:
        socket.inet_aton(value[0])
    except OSError as e:
        raise ValueError('Invalid IP address: %s. Examples of valid IPs: 0.0.0.0, 127.0.0.1.' % e)
    return value


class Management(object):
    default_command = 'start'
    no_configuration_required = ['createconfig']

    def __init__(self, settings=None, description=None, default_level=logging.INFO):
        self.parser = self.argument_parser(settings, description, default_level)

    def argument_parser(self, settings=None, description=None, default_level=logging.INFO):
        import argparse
        # if settings is None:
        #     settings = os.environ.get('NEKBOT_SETTINGS_MODULE', 'settings')
        # if description is None:
        #     description = __file__.__doc__
        # if len(sys.argv) < 2:
        #     # No se ha especificado un comando. Se pone el por defecto.
        #     sys.argv.insert(1, self.default_command)
        parser = argparse.ArgumentParser(prog='nekumo', description=description)
        # Niveles de logging
        parser.add_argument('--quiet', help='set logging to ERROR',
                            action='store_const', dest='loglevel',
                            const=logging.ERROR, default=logging.INFO)
        parser.add_argument('--debug', help='set logging to DEBUG',
                            action='store_const', dest='loglevel',
                            const=logging.DEBUG, default=logging.INFO)
        parser.add_argument('--verbose', help='set logging to COMM',
                            action='store_const', dest='loglevel',
                            const=5, default=logging.INFO)
        parser.add_argument('-c', '--config-dir', help='Nekumo config directory.',
                            default=nekumo_config_directory)
        parser.add_argument('-d', '--directory', help='Directory to serve.',
                            default=execution_directory)
        parser.add_argument('address_port', help='Port or Address:Port', type=address_port, nargs='?',
                            default='{0}:{1}'.format(DEFAULT_ADDRESS, DEFAULT_PORT))
        # parser.sub = parser.add_subparsers()
        # Subcommand Create config directory
        # createconfig = parser.sub.add_parser('createconfig', help='Only create config directory.')
        # createconfig.set_defaults(which='createconfig')
        # # Subcommand Create plugin
        # parser_createplugin = parser.sub.add_parser('createplugin', help='Create a new plugin for distribute.')
        # parser_createplugin.set_defaults(which='createplugin')
        # parser_createplugin.add_argument('dest')
        # Subcommand start
        # parser_start = parser.sub.add_parser('start', help='Start Nekumo.')
        # parser_start.set_defaults(which='start')
        return parser

    def execute(self, parser=None):
        if parser is None:
            parser = self.parser
        args = parser.parse_args()
        # command = args.which
        command = 'start'
        if not command in self.no_configuration_required:
            # settings.configure(args.settings)
            pass
        logging.basicConfig(level=args.loglevel)
        if not hasattr(self, 'command_' + command):
            raise ValueError('Comand %s is invalid.' % command)
        getattr(self, 'command_' + command)(args)

    def command_createbot(self, args):
        if args.dest:
            dest = args.dest
        else:
            dest = args.name
        if not args.dest and os.path.exists(dest):
            sys.stderr.write("Sorry, directory %s exists. I can't create directory.\n" % dest)
            sys.exit(1)
        elif not os.path.exists(dest):
            os.mkdir(dest)
        try:
            copytree(os.path.join(conf_src_dir, 'project_template'), dest)
        except Exception as e:
            sys.stderr.write('Unknown error: %s\n' % e)
        print('Project created as %s' % dest)

    def command_createplugin(self, args):
        from nekumo.conf import settings
        dest = args.dest
        name = os.path.split(dest)[1]
        replace = {
            'plugin_template': name,
            'plugin_author_name': settings.PLUGIN_AUTHOR_NAME,
            'plugin_author_email': settings.PLUGIN_AUTHOR_EMAIL,
            'plugin_author_website': settings.PLUGIN_AUTHOR_WEBSITE,
        }
        if os.path.exists(dest):
            sys.stderr.write("Sorry, directory %s exists. I can't create directory.\n" % dest)
            exit(1)
        else:
            os.mkdir(dest)
        if settings.HOOK_BEFORE_CREATE_PLUGIN:
            execute_hook(settings.HOOK_BEFORE_CREATE_PLUGIN, dest, name, settings)
        copy_template(os.path.join(conf_src_dir, 'plugin_template'), dest, replace)
        print('Plugin created as %s in %s' % (name, dest))
        if settings.HOOK_AFTER_CREATE_PLUGIN:
            execute_hook(settings.HOOK_AFTER_CREATE_PLUGIN, dest, name, settings)

    def command_start(self, args):
        from nekumo.core import Nekumo
        config = os.path.join(args.directory, '.nekumo')
        nekumo = Nekumo(args.directory, args.address_port, config, debug=logging.DEBUG == args.loglevel)
        nekumo = nekumo.start()
        try:
            nekumo.loop()
        except (KeyboardInterrupt, SystemExit):
            nekumo.close()


def register_management(manager):
    # TODO
    global Management
    class ManagementMixed(manager, Management):
        pass

    Management = ManagementMixed