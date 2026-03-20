from django import forms
from .models import UsuarioPersonalizado
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

# Definimos las opciones de rol globalmente para consistencia
OPCIONES_ROL = [
    ('Representante Comercial', _('Representante Comercial')),
    ('Gerente', _('Gerente')),
    ('Administrador', _('Administrador')),
]

class RegistroVendedorForm(forms.ModelForm):
    password = forms.CharField(
        label=_("Contraseña"),
        widget=forms.PasswordInput(attrs={'class': 'form-control rounded-pill', 'placeholder': '********'})
    )
    confirm_password = forms.CharField(
        label=_("Confirmar Contraseña"),
        widget=forms.PasswordInput(attrs={'class': 'form-control rounded-pill', 'placeholder': '********'})
    )
    
    rol = forms.ChoiceField(
        label=_("Rol"),
        choices=OPCIONES_ROL,
        widget=forms.Select(attrs={'class': 'form-select rounded-pill'})
    )

    class Meta:
        model = UsuarioPersonalizado
        # AGREGAMOS 'jefe' A LA LISTA DE FIELDS
        fields = ['username', 'first_name', 'last_name', 'email', 'rol', 'jefe', 'empresa', 'foto_perfil']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control rounded-pill', 'placeholder': _('Nombre de usuario')}),
            'first_name': forms.TextInput(attrs={'class': 'form-control rounded-pill', 'placeholder': _('Nombre')}),
            'last_name': forms.TextInput(attrs={'class': 'form-control rounded-pill', 'placeholder': _('Apellido')}),
            'email': forms.EmailInput(attrs={'class': 'form-control rounded-pill', 'placeholder': _('correo@ejemplo.com')}),
            'empresa': forms.TextInput(attrs={'class': 'form-control rounded-pill', 'placeholder': _('Nombre de la empresa')}),
            'foto_perfil': forms.FileInput(attrs={'class': 'form-control rounded-pill'}),
            # ESTILO PARA EL SELECT DE JEFE
            'jefe': forms.Select(attrs={'class': 'form-select rounded-pill'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # FILTRO INTELIGENTE: Solo usuarios activos que sean jefes/gerentes/admin pueden ser "Jefes"
        self.fields['jefe'].queryset = UsuarioPersonalizado.objects.filter(is_active=True).filter(
            Q(rol__icontains='Gerente') | 
            Q(rol__icontains='Administrador') | 
            Q(rol__icontains='Jefe') |
            Q(is_superuser=True)
        )
        self.fields['jefe'].label = _("Jefe Directo / Gerente")
        self.fields['jefe'].empty_label = _("Seleccione un Jefe (Opcional)")

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm_password")
        if password != confirm:
            raise forms.ValidationError(_("Las contraseñas no coinciden."))
        return cleaned_data


class EditarUsuarioForm(forms.ModelForm):
    rol = forms.ChoiceField(
        label=_("Rol"),
        choices=OPCIONES_ROL, 
        widget=forms.Select(attrs={'class': 'form-select rounded-pill'})
    )

    class Meta:
        model = UsuarioPersonalizado
        # AGREGAMOS 'jefe' TAMBIÉN AQUÍ
        fields = ['username', 'first_name', 'last_name', 'email', 'rol', 'jefe', 'empresa', 'foto_perfil']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control rounded-pill', 'placeholder': _('Nombre de usuario')}),
            'first_name': forms.TextInput(attrs={'class': 'form-control rounded-pill', 'placeholder': _('Nombre')}),
            'last_name': forms.TextInput(attrs={'class': 'form-control rounded-pill', 'placeholder': _('Apellido')}),
            'email': forms.EmailInput(attrs={'class': 'form-control rounded-pill', 'placeholder': _('correo@ejemplo.com')}),
            'empresa': forms.TextInput(attrs={'class': 'form-control rounded-pill', 'placeholder': _('Nombre de la empresa')}),
            'foto_perfil': forms.FileInput(attrs={'class': 'form-control rounded-pill'}),
            'jefe': forms.Select(attrs={'class': 'form-select rounded-pill'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # El mismo filtro para la edición
        self.fields['jefe'].queryset = UsuarioPersonalizado.objects.filter(is_active=True).filter(
            Q(rol__icontains='Gerente') | 
            Q(rol__icontains='Administrador') | 
            Q(rol__icontains='Jefe') |
            Q(is_superuser=True)
        )
        self.fields['jefe'].label = _("Jefe Directo / Gerente")
        self.fields['jefe'].empty_label = _("Seleccione un Jefe (Opcional)")