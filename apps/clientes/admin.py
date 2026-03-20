from django.contrib import admin
from .models import Contacto, Institucion

# Registramos tus tres tablas
admin.site.register(Institucion)
admin.site.register(Contacto)