from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('catalogo/', views.catalogo, name='catalogo'),

    path('acceso/', LoginView.as_view(
        template_name='inventario/login.html',
        redirect_authenticated_user=True,
    ), name='login'),
    path('salir/', LogoutView.as_view(), name='logout'),

    path('panel/', views.PanelView.as_view(), name='admin_panel'),
    path('panel/producto/nuevo/', views.ProductoCreateView.as_view(), name='producto_crear'),
    path('panel/producto/<int:pk>/', views.ProductoDetailView.as_view(), name='producto_detalle'),
    path('panel/producto/<int:pk>/editar/', views.ProductoUpdateView.as_view(), name='producto_editar'),
    path('panel/producto/<int:pk>/eliminar/', views.ProductoDeleteView.as_view(), name='producto_eliminar'),
]
