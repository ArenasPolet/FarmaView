from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    #  ruta específica para el login
    path('login/', views.login_view, name='login'),
    # ruta de tu pantalla principal
    
    path('metas/', views.metas_view, name='metas'),
    path('logout/', views.logout_view, name='logout'),
    path('equipo/', views.gestion_equipo_view, name='gestion_equipo'),
    path('toggle-estado/<int:usuario_id>/', views.toggle_estado_usuario, name='toggle_estado'),
    path('editar/<int:usuario_id>/', views.editar_usuario, name='editar_usuario'),
    
]