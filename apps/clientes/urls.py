from django.urls import path
from . import views

app_name = 'clientes'

urlpatterns = [
    path('ajax/guardar-institucion/', views.guardar_institucion_ajax, name='guardar_institucion_ajax'),
    path('ajax/guardar-contacto/', views.guardar_contacto_ajax, name='guardar_contacto_ajax'),
]