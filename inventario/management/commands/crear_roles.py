from django.contrib.auth.models import Group, Permission, User
from django.core.management.base import BaseCommand

from inventario.models import Categoria, Producto

PASSWORDS = {
    'admin_tech': 'Admin2026!',
    'asistente_tech': 'Asistente2026!',
}


class Command(BaseCommand):
    help = 'Crea los grupos Administrador y Asistente (y opcionalmente usuarios y datos de prueba).'

    def add_arguments(self, parser):
        parser.add_argument('--usuarios', action='store_true', help='Crea admin_tech y asistente_tech.')
        parser.add_argument('--datos', action='store_true', help='Carga categorías y productos de ejemplo.')

    def handle(self, *args, **opts):
        modelos = ['categoria', 'producto']
        admin_perms = Permission.objects.filter(
            content_type__app_label='inventario',
            codename__regex=r'^(add|change|delete|view)_(%s)$' % '|'.join(modelos),
        )
        asistente_perms = admin_perms.filter(codename__startswith='view_')

        g_admin, _ = Group.objects.get_or_create(name='Administrador')
        g_admin.permissions.set(admin_perms)
        g_asis, _ = Group.objects.get_or_create(name='Asistente')
        g_asis.permissions.set(asistente_perms)
        self.stdout.write(self.style.SUCCESS('Grupos Administrador y Asistente listos.'))

        if opts['usuarios']:
            for username, grupo in (('admin_tech', g_admin), ('asistente_tech', g_asis)):
                user, _ = User.objects.get_or_create(username=username, defaults={'is_staff': True})
                user.is_staff = True
                user.set_password(PASSWORDS[username])
                user.save()
                user.groups.set([grupo])
            self.stdout.write(self.style.SUCCESS('Usuarios admin_tech y asistente_tech listos.'))

        if opts['datos']:
            datos = {
                'Notebooks': [('Notebook Lenovo IdeaPad 15"', 'NB-LEN-001', 459990, 12),
                              ('Notebook HP 14" Ryzen 5', 'NB-HP-002', 389990, 8)],
                'Monitores': [('Monitor Samsung 24" Full HD', 'MN-SAM-001', 129990, 20),
                              ('Monitor LG UltraWide 29"', 'MN-LG-002', 219990, 5)],
                'Periféricos': [('Teclado mecánico Logitech', 'PF-LOG-001', 49990, 30),
                                ('Mouse inalámbrico HP', 'PF-HP-002', 12990, 0)],
                'Redes': [('Router TP-Link AX1800', 'RD-TPL-001', 59990, 15)],
            }
            for nombre_cat, items in datos.items():
                cat, _ = Categoria.objects.get_or_create(
                    nombre=nombre_cat, defaults={'descripcion': f'Productos de {nombre_cat.lower()}.'})
                for nombre, sku, precio, stock in items:
                    Producto.objects.get_or_create(
                        sku=sku,
                        defaults={'nombre': nombre, 'categoria': cat, 'precio': precio, 'stock': stock})
            self.stdout.write(self.style.SUCCESS('Datos de ejemplo cargados.'))
