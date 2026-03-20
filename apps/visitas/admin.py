from django.contrib import admin
from .models import Visita, RegistroVisita

# Configuramos la vista mejorada para RegistroVisita
class RegistroVisitaAdmin(admin.ModelAdmin):
    # Esto crea el diseño de doble columna para el campo productos
    filter_horizontal = ('productos',) 

# Configuramos la vista mejorada para Visita (agendadas)
class VisitaAdmin(admin.ModelAdmin):
    filter_horizontal = ('productos',)

# Registramos los modelos usando esta nueva configuración
admin.site.register(Visita, VisitaAdmin)
admin.site.register(RegistroVisita, RegistroVisitaAdmin)