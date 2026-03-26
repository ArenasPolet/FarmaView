from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
# IMPORTACIONES MODULARES:
from apps.clientes.models import Institucion, Contacto
from apps.productos.models import Producto


#  MODELO VISITA
class Visita(models.Model):
    ESTADOS = (
        ('Pendiente', 'Pendiente'),
        ('Realizada', 'Realizada'),
        ('Cancelada', 'Cancelada'),
    )
    # Conecta con el Usuario (App Usuarios)
    representante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='visitas')
   # Conecta con Clientes (App Clientes)
    institucion = models.ForeignKey(Institucion, on_delete=models.CASCADE, related_name='visitas_programadas')
    contacto = models.ForeignKey(Contacto, on_delete=models.SET_NULL, null=True, blank=True, related_name='visitas')
    razon_social = models.CharField(max_length=255, blank=True, null=True)
    fecha_hora = models.DateTimeField(verbose_name="Fecha y Hora de la visita")
    productos = models.ManyToManyField(Producto, blank=True, related_name='visitas')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Pendiente')
    notas = models.TextField(blank=True, null=True)
    tipo_gestion = models.CharField(max_length=50, blank=True, null=True, verbose_name="Tipo de Gestión")
    
    def __str__(self):
        return f"{self.institucion.nombre} {self.fecha_hora.strftime('%d/%m/%Y %H:%M')}"

class RegistroVisita(models.Model):
    # Conecta con el Usuario
    representante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='registros_visitas')
    # Conecta con Clientes
    institucion = models.ForeignKey(Institucion, on_delete=models.CASCADE, related_name='registros_visitas')
    contacto = models.ForeignKey(Contacto, on_delete=models.SET_NULL, null=True, blank=True, related_name='registros_visitas')
    
    # auto_now_add=True guarda la fecha y hora exacta de creación automáticamente
    fecha_hora = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora Realizada") 
    
    productos = models.ManyToManyField(Producto, blank=True, related_name='registros_visitas')
    notas = models.TextField(blank=True, null=True)
    tipo_gestion = models.CharField(max_length=50, blank=True, null=True, verbose_name="Tipo de Gestión")
    # --- CAMPOS GPS ---
    latitud = models.CharField(max_length=50, null=True, blank=True)
    longitud = models.CharField(max_length=50, null=True, blank=True)
    class Meta:
        verbose_name = "Registro de Visita"
        verbose_name_plural = "Registros de Visitas"

    def __str__(self):
        return f"Registro en {self.institucion.nombre} - {self.fecha_hora.strftime('%d/%m/%Y %H:%M')}"
    


