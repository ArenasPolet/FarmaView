from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class Institucion(models.Model):
    TIPO_OPCIONES = (
        ('Hospital', 'Hospital'),
        ('Clinica', 'Clínica'),
        ('Farmacia', 'Farmacia'),
        ('Centro Medico', 'Centro Médico'),
        ('Otro', 'Otro'),
    )

    nombre = models.CharField(max_length=200)
    razon_social = models.CharField(max_length=255, blank=True, null=True)
    # ESTOS SON LOS CAMPOS QUE FALTABAN:
    rut = models.CharField(max_length=20, blank=True, null=True)
    comuna = models.CharField(max_length=100, blank=True, null=True)
    # -----------------------------------
    direccion = models.CharField(max_length=255, blank=True, null=True)
    tipo = models.CharField(max_length=50, choices=TIPO_OPCIONES, default='Hospital')

    #   CAMPO REPRESNETANTE:
    representante = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='instituciones_asignadas'
    )
    
    def __str__(self):
        return self.nombre

# (Asegúrate de que tu modelo Contacto siga aquí abajo sin cambios)


# modelo Contacto
class Contacto(models.Model):
    ROLES = (
        ('Médico', 'Médico'),
        ('Administrativo', 'Administrativo'),
        ('Enfermería', 'Enfermería'),
        ('Otro', 'Otro'),
    )
    nombre = models.CharField(max_length=200)
    rol = models.CharField(max_length=50, choices=ROLES, default='Médico')
    especialidad = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    horario_preferido = models.CharField(max_length=200, blank=True, null=True)
    notas = models.TextField(blank=True, null=True)
    decisor_compra = models.BooleanField(default=False)
    institucion = models.ForeignKey(Institucion, on_delete=models.CASCADE, related_name='contactos')

    def __str__(self):
        return f"{self.nombre} ({self.rol})"


