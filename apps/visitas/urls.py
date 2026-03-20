from django.urls import path
from . import views

app_name = 'visitas'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('nueva-visita/', views.nueva_visita_view, name='nueva_visita'),
    path('agendar/', views.agendar_visita, name='agendar_visita'),
    
    # AÑADE ESTA LÍNEA:
    path('historial/', views.historial_view, name='historial'),
    path('mi-agenda/', views.mi_agenda_view, name='mi_agenda'),
    path('cobertura/', views.cobertura_view, name='cobertura'),
    path('estado/<int:visita_id>/<str:nuevo_estado>/', views.cambiar_estado_visita, name='cambiar_estado'),
    path('cargar-contactos-ajax/', views.cargar_contactos_ajax, name='cargar_contactos_ajax'),
    
]