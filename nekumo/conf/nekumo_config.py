import json
from collections import defaultdict
from ipaddress import IPv4Address, IPv4Network

import bcrypt as bcrypt

from nekumo.conf import Config, ListParser, DictParser, BooleanField

PERMS = {
    'admin': {'write', 'read'},
}


class Perms(ListParser):

    def __init__(self, parser=None, data=None, config=None):
        self._perms = set()
        super().__init__(parser=parser, data=data, config=config)

    def extend(self, iterable):
        super(Perms, self).extend(iterable)
        self._perms.update(iterable)
        for perm in iterable:
            self._perms.update(PERMS.get(perm, ()))

    def has_perm(self, perm):
        return perm in self._perms

    def has_perms(self, *perms):
        for perm in perms:
            if not self.has_perm(perm):
                return False
        return True


class User(DictParser):
    _security_hash = None
    default = {'perms': [], 'login_networks': []}
    schema = {
        'perms': Perms,
        'login_networks': ListParser,
    }

    @property
    def security_hash(self):
        """Hash de las medidas de login para, en caso de cambio, caducar las sesiones que
        utilicen el antiguo hash.
        """
        if not self._security_hash:
            self._security_hash = json.dumps([self.get('password'), self.get('login_networks')])
        return self._security_hash

    def set_password(self, password):
        self['password'] = bcrypt.hashpw(password, bcrypt.gensalt())

    @property
    def username(self):
        return self._key

    def has_perm(self, perm):
        return self['perms'].has_perm(perm)

    def has_perms(self, *perms):
        return self['perms'].has_perms(*perms)


class Users(DictParser):
    parser = User
    default_users = ['admin', 'anonymous']

    def __init__(self, parser=None, data=None, config=None):
        self._networks = defaultdict(list)
        super().__init__(parser=parser, data=data, config=config)

    def address_login(self, address):
        """Intentar logearse utilizando una dirección.
        """
        address = IPv4Address(address)
        null_network = IPv4Network('0.0.0.0')
        users = []
        for network, network_users in self._networks.items():
            if address not in network and not network == null_network:
                continue
            users.extend(network_users)
        if not users:
            return
        return sorted(users, key=lambda x: len(x.perms._perms))[-1]

    def parse_schema_element(self, key, value):
        element = super(Users, self).parse_schema_element(key, value)
        for network in element.login_networks:
            network = IPv4Network(network)
            self._networks[network].append(element)
        return element

    def __getitem__(self, item):
        if not item in self and item in self.default_users:
            return User()
        return super(Users, self).__getitem__(item)


class NekumoConfig(Config):
    # ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"]
    default = {
        "users": {
            "anonymous": {"perms": ["read", "write"], "login_networks": ["0.0.0.0"]},
            "admin": {"login_networks": ["127.0.0.1"], "perms": ["admin"]},
        },
        "servers": ["web"],
        "show_quickstart": True,
        "plugins": []
    }
    schema = {
        "users": Users,
        "servers": ListParser,
        "show_quickstart": BooleanField(),
        "plugins": ListParser,
    }
