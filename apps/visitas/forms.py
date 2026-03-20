from django import forms
from django.db.models import Q
from django.contrib.auth import get_user_model
from .models import Visita, Institucion

Usuario = get_user_model()

class VisitaForm(forms.ModelForm):
    class Meta:
        model = Visita
        # Agregamos 'contacto' a la lista
        fields = ['institucion', 'contacto', 'fecha_hora', 'productos', 'notas']
        
        widgets = {
            # Usamos RadioSelect para Institución y Contacto para poder estilizarlos en el HTML
            'institucion': forms.RadioSelect(attrs={'class': 'form-check-input fs-5'}),
            'contacto': forms.RadioSelect(attrs={'class': 'form-check-input fs-5'}),
            'productos': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input fs-5'}),
            
            # Fecha y hora con diseño moderno
            'fecha_hora': forms.DateTimeInput(attrs={'class': 'form-control border-0 bg-transparent fw-bold text-dark', 'type': 'datetime-local'}),
            'notas': forms.Textarea(attrs={'class': 'form-control border-0', 'rows': 4, 'placeholder': 'Escriba o dicte detalles sobre la visita...', 'style': 'resize: none;'}),
        }

        def __init__(self, *args, **kwargs):
            # 1. Extraemos el usuario que nos enviará la vista
            user = kwargs.pop('user', None)
            super(VisitaForm, self).__init__(*args, **kwargs)

            # 2. Aplicamos el filtro de jerarquía a las instituciones
            if user:
                if user.is_superuser:
                    # Admin ve todo
                    self.fields['institucion'].queryset = Institucion.objects.all()
                elif getattr(user, 'es_gerente', False) or user.groups.filter(name='Gerente').exists():
                    # Gerente ve su territorio y el de su equipo
                    vendedores_permitidos = Usuario.objects.filter(Q(id=user.id) | Q(jefe=user))
                    self.fields['institucion'].queryset = Institucion.objects.filter(representante__in=vendedores_permitidos).distinct()
                else:
                    # Vendedor solo ve las suyas
                    self.fields['institucion'].queryset = Institucion.objects.filter(representante=user)