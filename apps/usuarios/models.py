from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class UsuarioPersonalizado(AbstractUser):
    rol = models.CharField(max_length=50, default='Representante Comercial')
    empresa = models.CharField(max_length=100, default='Farmacéutica de Chile')
    foto_perfil = models.ImageField(upload_to='perfiles/', null=True, blank=True)
    
    # =========================================================
    # ESTRUCTURA JERÁRQUICA COMERCIAL
    # =========================================================
    jefe = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='equipo',
        help_text="Selecciona al Gerente o Jefe directo de este vendedor."
    )
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.rol}"

    # --- NUEVA PROPIEDAD DE JERARQUÍA ---
    @property
    def es_gerente(self):
        # Si el rol contiene "Admin", "Gerente" o es Superusuario de Django
        roles_jefatura = ['Administrador', 'Gerente', 'Jefe de Ventas']
        return any(palabra in self.rol for palabra in roles_jefatura) or self.is_staff or self.is_superuser

