from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import ProductoForm
from .models import Categoria, Producto

def index(request):
    context = {
        'total_productos': Producto.objects.count(),
        'total_categorias': Categoria.objects.count(),
        'ultimos': Producto.objects.select_related('categoria').order_by('-fecha_ingreso', '-id')[:4],
    }
    return render(request, 'inventario/index.html', context)


def catalogo(request):
    productos = Producto.objects.select_related('categoria')
    q = request.GET.get('q', '').strip()
    categoria_id = request.GET.get('categoria', '').strip()

    if q:
        productos = productos.filter(nombre__icontains=q)
    if categoria_id.isdigit():
        productos = productos.filter(categoria_id=int(categoria_id))

    context = {
        'productos': productos,
        'categorias': Categoria.objects.all(),
        'q': q,
        'categoria_sel': int(categoria_id) if categoria_id.isdigit() else None,
    }
    return render(request, 'inventario/catalogo.html', context)

class PanelMixin(LoginRequiredMixin, PermissionRequiredMixin):
    """Exige login y el permiso indicado en `permission_required`.

    Anónimo -> redirige al login. Autenticado sin permiso -> 403.
    """
    login_url = reverse_lazy('login')


class PanelView(PanelMixin, ListView):
    permission_required = 'inventario.view_producto'
    model = Producto
    template_name = 'inventario/admin_panel.html'
    context_object_name = 'productos'

    def get_queryset(self):
        qs = Producto.objects.select_related('categoria')
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(Q(nombre__icontains=q) | Q(sku__icontains=q))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q'] = self.request.GET.get('q', '').strip()
        return ctx


class ProductoDetailView(PanelMixin, DetailView):
    permission_required = 'inventario.view_producto'
    model = Producto
    template_name = 'inventario/producto_detalle.html'
    context_object_name = 'producto'


class ProductoCreateView(PanelMixin, CreateView):
    permission_required = 'inventario.add_producto'
    model = Producto
    form_class = ProductoForm
    template_name = 'inventario/producto_form.html'
    success_url = reverse_lazy('admin_panel')
    extra_context = {'titulo': 'Nuevo producto', 'boton': 'Guardar producto'}

    def form_valid(self, form):
        messages.success(self.request, 'Producto creado correctamente.')
        return super().form_valid(form)


class ProductoUpdateView(PanelMixin, UpdateView):
    permission_required = 'inventario.change_producto'
    model = Producto
    form_class = ProductoForm
    template_name = 'inventario/producto_form.html'
    success_url = reverse_lazy('admin_panel')
    extra_context = {'titulo': 'Editar producto', 'boton': 'Guardar cambios'}

    def form_valid(self, form):
        messages.success(self.request, 'Producto actualizado correctamente.')
        return super().form_valid(form)


class ProductoDeleteView(PanelMixin, DeleteView):
    permission_required = 'inventario.delete_producto'
    model = Producto
    template_name = 'inventario/producto_confirmar_eliminar.html'
    success_url = reverse_lazy('admin_panel')
    context_object_name = 'producto'

    def form_valid(self, form):
        messages.success(self.request, 'Producto eliminado correctamente.')
        return super().form_valid(form)
