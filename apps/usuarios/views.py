from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from .forms import RegistroVendedorForm
from .models import UsuarioPersonalizado
from .forms import EditarUsuarioForm 
from django.core.paginator import Paginator


# VISTA DE INICIO DE SESIÓN
def login_view(request):
    # Si el usuario ya inició sesión, redirigir al dashboard modular
    if request.user.is_authenticated:
        return redirect('visitas:dashboard')

    if request.method == 'POST':
        usuario = request.POST.get('username')
        contrasena = request.POST.get('password')
        
        user = authenticate(request, username=usuario, password=contrasena)
        
        if user is not None:
            login(request, user)
            return redirect('visitas:dashboard') 
        else:
            messages.error(request, 'Usuario o contraseña incorrectos. Inténtalo de nuevo.')

    # Django buscará automáticamente en apps/usuarios/templates/usuarios/login.html
    return render(request, 'usuarios/login.html')


# VISTA DE CIERRE DE SESIÓN
def logout_view(request):
    logout(request)
    return redirect('usuarios:login')


# VISTA DE METAS (PROYECTADA)
@login_required(login_url='usuarios:login')
def metas_view(request):
    # Django buscará automáticamente en apps/usuarios/templates/usuarios/metas.html
    return render(request, 'usuarios/metas.html')


#guardia de seguridad
def es_gerente_check(user):
    return user.is_authenticated and getattr(user, 'es_gerente', False)

#FUNCION GESTION USUARIOS
@user_passes_test(es_gerente_check, login_url='visitas:dashboard')
def gestion_equipo_view(request):
    usuarios_list = UsuarioPersonalizado.objects.all().select_related('jefe').order_by('-date_joined')
    
    # --- CONFIGURACIÓN DE PAGINACIÓN ---
    paginator = Paginator(usuarios_list, 10) # Muestra 10 usuarios por página
    page_number = request.GET.get('page')
    usuarios = paginator.get_page(page_number)
    
    if request.method == 'POST':
        form = RegistroVendedorForm(request.POST, request.FILES)
        if form.is_valid():
            nuevo_usuario = form.save(commit=False)
            nuevo_usuario.set_password(form.cleaned_data['password'])
            nuevo_usuario.save()
            messages.success(request, f"¡Usuario {nuevo_usuario.username} creado con éxito!")
            return redirect('usuarios:gestion_equipo')
    else:
        form = RegistroVendedorForm()

    return render(request, 'usuarios/gestion_equipo.html', {
        'usuarios': usuarios, # Ahora 'usuarios' contiene solo los 10 de la página actual
        'form': form
    })

#FUNCION CAMBAIR ESTADO
@login_required(login_url='usuarios:login')
def toggle_estado_usuario(request, usuario_id):
    if request.method == 'POST':
        # 1. Por seguridad, verificamos que el usuario que hace esto sea Admin
        if not request.user.is_superuser and 'Administrador' not in request.user.rol:
            messages.error(request, "No tienes permisos para desactivar usuarios.")
            return redirect('usuarios:gestion_equipo')

        # 2. Buscamos al usuario que queremos modificar
        usuario_target = get_object_or_404(UsuarioPersonalizado, id=usuario_id)
        
        # 3. Evitamos que el admin se desactive a sí mismo por error
        if usuario_target == request.user:
            messages.warning(request, "No puedes desactivar tu propia cuenta activa.")
        else:
            # Invertimos el estado (Si era True pasa a False, y viceversa)
            usuario_target.is_active = not usuario_target.is_active
            usuario_target.save()
            
            estado_texto = "activado" if usuario_target.is_active else "desactivado"
            messages.success(request, f"El acceso para {usuario_target.username} ha sido {estado_texto}.")
            
    return redirect('usuarios:gestion_equipo')

#EDITAR USUARIO
@login_required(login_url='usuarios:login')
def editar_usuario(request, usuario_id):
    # Verificamos permisos de Administrador
    if not request.user.is_superuser and 'Administrador' not in request.user.rol:
        messages.error(request, "No tienes permisos para editar usuarios.")
        return redirect('usuarios:gestion_equipo')

    # Buscamos al usuario en la base de datos
    usuario = get_object_or_404(UsuarioPersonalizado, id=usuario_id)

    if request.method == 'POST':
        # Pasamos instance=usuario para que Django sepa que estamos actualizando, no creando
        form = EditarUsuarioForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, f"Los datos de {usuario.username} se actualizaron correctamente.")
            return redirect('usuarios:gestion_equipo')
    else:
        # Si es GET, cargamos el formulario con los datos actuales del usuario
        form = EditarUsuarioForm(instance=usuario)

    return render(request, 'usuarios/editar_usuario.html', {'form': form, 'usuario_edit': usuario})