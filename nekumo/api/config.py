from nekumo.api.base import API
from nekumo.api.decorators import method
from nekumo.utils.network import get_public_address


class QuickStart(API):
    type = 'api'

    @staticmethod
    def is_capable(stanza):
        return stanza.node == '.nekumo/quick-start' or stanza.node == '/.nekumo/quick-start'

    @method
    def read(self):
        server = self.nekumo.servers[self.nekumo.main_server]
        admin = self.nekumo.config.users['admin']
        # Admin availability
        if not admin.get('login_networks') and admin.get('password'):
            # Sólo se accede mediante login al admin
            admin_availability = 'login'
        elif admin.get('login_networks') and not admin.get('password'):
            # Sólo se puede acceder al admin por la red desde la que se accede
            admin_availability = {
                frozenset({"127.0.0.1"}): "this_device",
                frozenset({"10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"}): "home_network",
            }.get(frozenset(admin['login_networks']), None)
        else:
            # No se puede acceder como usuario admin
            admin_availability = 'none'
        anonymous_perms = self.nekumo.config.users['anonymous'].perms
        anonymous_perms = {frozenset('read'): 'read',
                           frozenset('write'): 'write',
                           frozenset({'read', 'write'}): 'read_write',
                           frozenset(): 'none'}.get(frozenset(anonymous_perms), None)
        address = get_public_address()
        return {
            'port': server.config['port'],
            'address': address,
            'admin_availability': admin_availability,
            'anonymous_perms': anonymous_perms,
        }

    @method
    def write(self, data):
        server = self.nekumo.servers[self.nekumo.main_server]
        admin = self.nekumo.config.users['admin']
        anonymous = self.nekumo.config.users['anonymous']
        # Disponibilidad del usuario Admin
        if data.get('admin_availability'):
            admin_availability = data['admin_availability']
            admin['login_networks'] = []
            del admin['password']
            if admin_availability == 'login':
                admin.set_password(data['admin_availability'])
            elif admin_availability != 'none':
                admin['login_networks'] = {
                    "this_device": ("127.0.0.1",),
                    "home_network": ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"),
                }[admin_availability]
        # Permisos para anónimos
        if data.get('anonymous_perms'):
            anonymous_perms = data['anonymous_perms']
            anonymous['perms'] = {
                'read': ['read'],
                'write': ['write'],
                'read_write': ['read', 'write'],
                'none': [],
            }[anonymous_perms]
        # Puerto del servidor
        server['port'] = data['port']
        self.nekumo.config.save()
        server.save()