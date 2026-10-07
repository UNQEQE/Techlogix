from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import Categoria, Producto


class TechLogixTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('crear_roles', '--usuarios', '--datos', verbosity=0)
        cls.producto = Producto.objects.get(sku='NB-LEN-001')

    def login(self, user, pwd):
        self.assertTrue(self.client.login(username=user, password=pwd))

    def test_publicas_anonimo(self):
        for name in ('index', 'catalogo', 'login'):
            self.assertEqual(self.client.get(reverse(name)).status_code, 200, name)

    def test_catalogo_filtros(self):
        r = self.client.get(reverse('catalogo'), {'q': 'monitor'})
        self.assertEqual(len(r.context['productos']), 2)
        cat = Categoria.objects.get(nombre='Redes')
        r = self.client.get(reverse('catalogo'), {'categoria': cat.id})
        self.assertEqual([p.sku for p in r.context['productos']], ['RD-TPL-001'])

    def test_anonimo_redirige_a_login(self):
        for name, args in [('admin_panel', []), ('producto_crear', []),
                           ('producto_editar', [self.producto.pk]),
                           ('producto_eliminar', [self.producto.pk]),
                           ('producto_detalle', [self.producto.pk])]:
            r = self.client.get(reverse(name, args=args))
            self.assertEqual(r.status_code, 302, name)
            self.assertIn(reverse('login'), r.url)

    def test_asistente_lee_pero_no_modifica(self):
        self.login('asistente_tech', 'Asistente2026!')
        self.assertEqual(self.client.get(reverse('admin_panel')).status_code, 200)
        self.assertEqual(self.client.get(reverse('producto_detalle', args=[self.producto.pk])).status_code, 200)
        self.assertEqual(self.client.get(reverse('producto_crear')).status_code, 403)
        self.assertEqual(self.client.get(reverse('producto_editar', args=[self.producto.pk])).status_code, 403)
        self.assertEqual(self.client.post(reverse('producto_eliminar', args=[self.producto.pk])).status_code, 403)
        self.assertTrue(Producto.objects.filter(pk=self.producto.pk).exists())

    def test_asistente_no_ve_botones_cud(self):
        self.login('asistente_tech', 'Asistente2026!')
        html = self.client.get(reverse('admin_panel')).content.decode()
        self.assertNotIn('Nuevo producto', html)
        self.assertNotIn('>Editar<', html)
        self.assertNotIn('>Eliminar<', html)

    def test_admin_crud_completo(self):
        self.login('admin_tech', 'Admin2026!')
        html = self.client.get(reverse('admin_panel')).content.decode()
        self.assertIn('Nuevo producto', html)
        self.assertIn('>Editar<', html)

        cat = Categoria.objects.first()
        r = self.client.post(reverse('producto_crear'), {
            'nombre': 'Webcam Logitech C920', 'categoria': cat.id, 'sku': 'WB-LOG-001',
            'precio': 59990, 'stock': 7, 'fecha_ingreso': '2026-10-07'})
        self.assertRedirects(r, reverse('admin_panel'))
        nuevo = Producto.objects.get(sku='WB-LOG-001')

        r = self.client.post(reverse('producto_editar', args=[nuevo.pk]), {
            'nombre': 'Webcam Logitech C920 HD', 'categoria': cat.id, 'sku': 'WB-LOG-001',
            'precio': 54990, 'stock': 9, 'fecha_ingreso': '2026-10-07'})
        self.assertRedirects(r, reverse('admin_panel'))
        nuevo.refresh_from_db()
        self.assertEqual((nuevo.nombre, nuevo.stock), ('Webcam Logitech C920 HD', 9))

        self.assertEqual(self.client.get(reverse('producto_eliminar', args=[nuevo.pk])).status_code, 200)
        r = self.client.post(reverse('producto_eliminar', args=[nuevo.pk]))
        self.assertRedirects(r, reverse('admin_panel'))
        self.assertFalse(Producto.objects.filter(pk=nuevo.pk).exists())

    def test_login_redirige_al_panel(self):
        r = self.client.post(reverse('login'), {'username': 'admin_tech', 'password': 'Admin2026!'})
        self.assertRedirects(r, reverse('admin_panel'))

    def test_django_admin_asistente_solo_lectura(self):
        self.login('asistente_tech', 'Asistente2026!')
        self.assertEqual(self.client.get('/admin/inventario/producto/').status_code, 200)
        self.assertEqual(self.client.get('/admin/inventario/producto/add/').status_code, 403)
