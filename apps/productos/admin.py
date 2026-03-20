from django.contrib import admin
from .models import Producto, Categoria

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    # Agregamos 'stock' a la lista
    list_display = ('nombre', 'precio_lista', 'stock', 'categoria', 'codigo_sku')
    # ¡Truco! Permite editar el stock directamente desde la tabla
    list_editable = ('stock',) 
    list_filter = ('categoria',)
    search_fields = ('nombre', 'codigo_sku')