from django.urls import path
from . import views

app_name = 'ventas'

urlpatterns = [
    path('mis-metas/', views.metas_view, name='metas'),
    path('nueva-orden/', views.nueva_orden_view, name='nueva_orden'),
    path('orden/<int:pedido_id>/', views.detalle_orden_view, name='detalle_orden'),
    path('analitica/', views.analitica_view, name='analitica'),
    path('metas/cargar/', views.cargar_datos_excel, name='cargar_metas'),
    path('detalle-institucion/<int:institucion_id>/<int:mes>/<int:anio>/', views.detalle_institucion_view, name='detalle_institucion'),
    path('exportar/pedidos/', views.exportar_pedidos_excel, name='exportar_pedidos_excel'),
    path('exportar/metas/', views.exportar_metas_excel, name='exportar_metas_excel'),

]