from django.contrib import admin
from .models import Pedido, DetallePedido, MetaMensual

# Esto permite ver los productos del carrito dentro de la misma pantalla del pedido

class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0
    readonly_fields = ('subtotal',)

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ['id', 'institucion', 'contacto','representante', 'fecha_creacion', 'estado', 'total_final']
    list_filter = ['estado', 'fecha_creacion']
    search_fields = ['institucion__nombre', 'contacto__nombre']
    inlines = [DetallePedidoInline] # Agrega el carrito abajo


@admin.register(MetaMensual)
class MetaMensualAdmin(admin.ModelAdmin):
    # Las columnas que verás en la tabla general
    list_display = ('representante', 'mes', 'anio', 'monto_meta_formateado')
    
    # Filtros laterales para buscar rápidamente por año, mes o vendedor
    list_filter = ('anio', 'mes', 'representante')
    
    # Barra de búsqueda por si tienes muchos vendedores
    search_fields = ('representante__username', 'representante__first_name', 'representante__last_name')

    # Una pequeña función para que el monto se vea con separador de miles en la tabla
    def monto_meta_formateado(self, obj):
        return f"${obj.monto_meta:,}".replace(',', '.')
    monto_meta_formateado.short_description = 'Monto de la Meta'

@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'producto', 'cantidad', 'precio_unitario_historico', 'subtotal')
    search_fields = ('pedido__institucion__nombre', 'producto__nombre')