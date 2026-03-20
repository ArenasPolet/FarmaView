# apps/productos/urls.py
from django.urls import path
from . import views

app_name = 'productos'

urlpatterns = [
    path('catalogo/', views.catalogo_view, name='catalogo'),
    path('cargar-catalogo/', views.cargar_catalogo_view, name='cargar_catalogo'),
    
]