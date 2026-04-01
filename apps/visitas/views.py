from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from apps.usuarios.models import UsuarioPersonalizado
from .models import Visita 
from itertools import chain
from operator import attrgetter
from .forms import VisitaForm
# Importamos modelos para llenar los selectores
from apps.clientes.models import Institucion, Contacto
from apps.productos.models import Producto
from .models import Visita, RegistroVisita
from django.utils import timezone
from datetime import datetime,timedelta
from django.utils.translation import gettext as _
from django.db.models import F, Count, Q, Sum,Case, When
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect
import calendar
from django.http import JsonResponse
from apps.ventas.models import MetaInstitucion, MetaMensual,Pedido
from django.contrib.auth import get_user_model

Usuario = get_user_model()


# Diccionario global para los nombres de los meses
NOMBRES_MESES = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio', 
    7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
}


# ==========================================
# VISTA DASHBOARD (CON JERARQUÍA)
# ==========================================
@login_required(login_url='usuarios:login')
def dashboard_view(request):
    ahora_full =timezone.localtime(timezone.now())
    hoy_real = ahora_full.date()
    
    # --- LÓGICA DEL FILTRO ---
    mes_sel = int(request.GET.get('mes', hoy_real.month))
    anio_sel = int(request.GET.get('anio', hoy_real.year))

    # 1. LÓGICA DE PERMISOS (Jerarquía)
    if request.user.is_superuser:
        vendedores_permitidos = Usuario.objects.all()
    elif getattr(request.user, 'es_gerente', False) or request.user.groups.filter(name='Gerente').exists():
        vendedores_permitidos = Usuario.objects.filter(Q(id=request.user.id) | Q(jefe=request.user))
    else:
        vendedores_permitidos = Usuario.objects.filter(id=request.user.id)
 
    # 2. Agenda (Visitas programadas para hoy del equipo permitido)
    mis_visitas = []
    if mes_sel == hoy_real.month and anio_sel == hoy_real.year:
        mis_visitas = Visita.objects.filter(
            representante__in=vendedores_permitidos, 
            fecha_hora__date=hoy_real
        ).order_by('fecha_hora')[:5]

    # 3. ATENCIÓN REQUERIDA (Visitas Pendientes Atrasadas)
    ultimas_pendientes = Visita.objects.filter(
        representante__in=vendedores_permitidos,
        estado__icontains='Pendiente',
        fecha_hora__lt=ahora_full
    ).select_related('institucion', 'representante').order_by('fecha_hora')[:5]

    # 4. METAS Y VENTAS (¡Aquí está el cambio principal a MetaInstitucion!)
    meta_monto = MetaInstitucion.objects.filter(
        representante__in=vendedores_permitidos, 
        mes=mes_sel, 
        anio=anio_sel
    ).aggregate(total=Sum('monto_meta'))['total'] or 0

    ventas_totales = Pedido.objects.filter(
        representante__in=vendedores_permitidos,
        fecha_creacion__year=anio_sel,
        fecha_creacion__month=mes_sel,
        estado__in=['Ingresado', 'Facturado']
    ).aggregate(total=Sum('total_final'))['total'] or 0

    porcentaje = int((ventas_totales / meta_monto) * 100) if meta_monto > 0 else 0

    # Obtenemos la última venta real para el footer de la tarjeta
    ultima_venta = Pedido.objects.filter(
        representante__in=vendedores_permitidos,
        estado__in=['Ingresado', 'Facturado']
    ).order_by('-fecha_creacion').first()

    # 5. Proyección 
    proyeccion = ventas_totales
    if mes_sel == hoy_real.month and anio_sel == hoy_real.year:
        dias_pasados = hoy_real.day
        dias_totales = calendar.monthrange(anio_sel, mes_sel)[1]
        if dias_pasados > 0:
            proyeccion = int((ventas_totales / dias_pasados) * dias_totales)

    # ==========================================
    #  CÁLCULO DE COBERTURA EXACTO (Agendas + Terreno)
    # ==========================================
    instituciones_equipo = Institucion.objects.filter(representante__in=vendedores_permitidos).distinct()
    meta_cobertura_dashboard = instituciones_equipo.count() * 2 
    
    # Sumamos tanto las agendas realizadas como los registros directos en terreno
    visitas_agendadas = Visita.objects.filter(
        representante__in=vendedores_permitidos,
        estado__in=['Realizada', 'Completada'],
        fecha_hora__year=anio_sel,
        fecha_hora__month=mes_sel
    ).count()

    visitas_terreno = RegistroVisita.objects.filter(
        representante__in=vendedores_permitidos,
        fecha_hora__year=anio_sel,
        fecha_hora__month=mes_sel
    ).count()

    visitas_realizadas_dashboard = visitas_agendadas + visitas_terreno
    porcentaje_cobertura_dashboard = int((visitas_realizadas_dashboard / meta_cobertura_dashboard) * 100) if meta_cobertura_dashboard > 0 else 0

    # ==========================================

    contexto = {
        'mes_sel': mes_sel,
        'anio_sel': anio_sel,
        'mes_nombre': NOMBRES_MESES.get(mes_sel),
        'nombres_meses': NOMBRES_MESES,
        'ventas_totales_mes': ventas_totales,
        'meta_mensual_ventas': meta_monto,
        'porcentaje_meta_ventas': porcentaje,
        'ancho_barra_meta_ventas': min(porcentaje, 100),
        'proyeccion_cierre': proyeccion,
        'visitas_agenda': mis_visitas,
        'ultimas_pendientes': ultimas_pendientes,
        'hoy': hoy_real,
        'meta_cobertura': meta_cobertura_dashboard,
        'visitas_realizadas': visitas_realizadas_dashboard,
        'porcentaje_cobertura': min(porcentaje_cobertura_dashboard, 100),
        'ultima_venta': ultima_venta, # Enviamos el dato al HTML
    }
    return render(request, 'visitas/dashboard.html', contexto)

# ==========================================
# VISTA COBERTURA (CON JERARQUÍA)
# ==========================================
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.decorators import login_required
# Asegúrate de tener tus modelos importados: Institucion, Visita, RegistroVisita, Usuario

# ==========================================
# VISTA COBERTURA (CON JERARQUÍA)
# ==========================================
@login_required
def cobertura_view(request):
    # 1. Sacamos la hora UTC y la convertimos OBLIGATORIAMENTE a la hora de Chile
    hoy = timezone.localtime(timezone.now())
    inicio_mes = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # 1. Definir el equipo permitido (Jerarquía)
    if request.user.is_superuser:
        vendedores_permitidos = Usuario.objects.all()
    elif getattr(request.user, 'es_gerente', False):
        vendedores_permitidos = Usuario.objects.filter(Q(id=request.user.id) | Q(jefe=request.user))
    else:
        vendedores_permitidos = Usuario.objects.filter(id=request.user.id)

    # 2. Obtener las instituciones del equipo
    instituciones_del_equipo = Institucion.objects.filter(
        representante__in=vendedores_permitidos
    ).distinct()

    # --- 3. MÉTRICAS GENERALES (FUSIONADAS) ---
    # Contamos realizadas en Visita
    v_reales = Visita.objects.filter(
        representante__in=vendedores_permitidos,
        estado='Realizada',
        fecha_hora__gte=inicio_mes
    ).count()

    # Contamos realizadas en RegistroVisita
    r_reales = RegistroVisita.objects.filter(
        representante__in=vendedores_permitidos,
        fecha_hora__gte=inicio_mes
    ).count()
    
    total_visitas_realizadas = v_reales + r_reales
    meta_total_visitas = instituciones_del_equipo.count() * 2
    pendientes_totales = max(0, meta_total_visitas - total_visitas_realizadas)
    porcentaje = int((total_visitas_realizadas / meta_total_visitas * 100)) if meta_total_visitas > 0 else 0

   # --- 4. OBTENER, CONTAR Y ORDENAR ---
    # Convertimos el queryset a una lista de Python para poder manipularla libremente
    todas_las_instituciones = list(instituciones_del_equipo)

    # Contamos las visitas para TODAS las instituciones primero
    for inst in todas_las_instituciones:
        agendadas = Visita.objects.filter(
            institucion=inst,
            representante__in=vendedores_permitidos,
            estado='Realizada',
            fecha_hora__gte=inicio_mes
        ).count()

        espontaneas = RegistroVisita.objects.filter(
            institucion=inst,
            representante__in=vendedores_permitidos,
            fecha_hora__gte=inicio_mes
        ).count()

        inst.conteo_visitas = agendadas + espontaneas

    # LA MAGIA DEL ORDENAMIENTO UX:
    # Ordenamos la lista. Primero por 'conteo_visitas' (los 0 van arriba, luego los 1, luego los 2+)
    # y en caso de empate (por ejemplo, muchos con 0), los ordena alfabéticamente por 'nombre'
    todas_las_instituciones.sort(key=lambda x: (x.conteo_visitas, x.nombre))

    # --- 5. PAGINACIÓN ---
    # El Paginator de Django es tan genial que funciona perfecto con listas de Python
    paginator = Paginator(todas_las_instituciones, 10)
    page_number = request.GET.get('page')
    lista_territorio = paginator.get_page(page_number)

    context = {
        'total_target': meta_total_visitas,
        'visited': total_visitas_realizadas,
        'remaining': pendientes_totales,
        'porcentaje': porcentaje,
        'lista_territorio': lista_territorio,
        'hoy': hoy,
    }
    
    return render(request, 'visitas/cobertura.html', context)
   

# ==========================================
# 1. NUEVA VISITA (Guarda en RegistroVisita)
# ==========================================
@login_required(login_url='usuarios:login')
def nueva_visita_view(request):
    
    # --- 1. LÓGICA DE PERMISOS (Filtro Jerárquico) ---
    if request.user.is_superuser:
        vendedores_permitidos = Usuario.objects.all()
    elif getattr(request.user, 'es_gerente', False) or request.user.groups.filter(name='Gerente').exists():
        vendedores_permitidos = Usuario.objects.filter(Q(id=request.user.id) | Q(jefe=request.user))
    else:
        vendedores_permitidos = Usuario.objects.filter(id=request.user.id)

    # --- 2. PROCESAMIENTO DEL FORMULARIO (POST) ---
    if request.method == 'POST':
        institucion_id = request.POST.get('institucion')
        contacto_id = request.POST.get('contacto')
        tipo_gestion = request.POST.get('tipo_gestion', 'Presentación')
        notas = request.POST.get('notas')
        # Atrapamos las coordenadas ocultas
        lat_recibida = request.POST.get('latitud')
        lon_recibida = request.POST.get('longitud')

        if not institucion_id:
            messages.error(request, 'Debe seleccionar una institución.')
            return redirect('visitas:nueva_visita')

        try:
            # Creamos el registro en la tabla RegistroVisita
            nuevo_registro = RegistroVisita(
                representante=request.user,
                institucion_id=institucion_id,
                contacto_id=contacto_id if contacto_id else None,
                tipo_gestion=tipo_gestion,
                notas=notas,
                latitud=lat_recibida,  
                longitud=lon_recibida
                # Recordatorio: fecha_hora se pone sola por el auto_now_add=True
            )
            nuevo_registro.save()
            
            # Capturamos los productos seleccionados
            productos_ids = request.POST.getlist('productos')
            
            if productos_ids:
                nuevo_registro.productos.set(productos_ids)
                
            messages.success(request, '¡Registro de visita guardado con éxito!')
            return redirect('visitas:dashboard') 
            
        except Exception as e:
            messages.error(request, f'Error al guardar el registro: {e}')
            return redirect('visitas:nueva_visita')

    # --- 3. CARGA DE PANTALLA (GET) CON FILTRO APLICADO ---
    
    # Filtramos las instituciones basándonos en el equipo permitido
    instituciones_filtradas = Institucion.objects.filter(representante__in=vendedores_permitidos).distinct()
    
    contexto = {
        'instituciones': instituciones_filtradas, # ¡AQUÍ ESTÁ LA MAGIA!
        # También filtramos los contactos para no cargar los de toda la empresa en memoria
        'contactos': Contacto.objects.filter(institucion__in=instituciones_filtradas), 
        'productos': Producto.objects.filter(stock__gt=0),
    }
    return render(request, 'visitas/nueva_visita.html', contexto)

# ==========================================
# 2. AGENDAR VISITA (Guarda en Visita)
# ==========================================
@login_required
def agendar_visita(request):
    """
    Vista para renderizar el formulario de agendar visita y procesarlo con filtros de jerarquía.
    """
    # --- 1. LÓGICA DE PERMISOS (Filtro Jerárquico) ---
    if request.user.is_superuser:
        vendedores_permitidos = Usuario.objects.all()
    elif getattr(request.user, 'es_gerente', False) or request.user.groups.filter(name='Gerente').exists():
        vendedores_permitidos = Usuario.objects.filter(Q(id=request.user.id) | Q(jefe=request.user))
    else:
        vendedores_permitidos = Usuario.objects.filter(id=request.user.id)

    # --- 2. PROCESAMIENTO DEL FORMULARIO (POST) ---
    if request.method == 'POST':
        institucion_id = request.POST.get('institucion')
        fecha_hora = request.POST.get('fecha_hora')
        contacto_id = request.POST.get('contacto')
        tipo_gestion = request.POST.get('tipo_gestion')
        notas = request.POST.get('notas')
        
        if not all([institucion_id, fecha_hora, tipo_gestion]):
            messages.error(request, _('Por favor, completa los campos obligatorios.'))
            return redirect('visitas:agendar_visita')

        try:
            # Guardamos en el modelo original Visita
            nueva_agenda = Visita(
                representante=request.user,  
                institucion_id=institucion_id,
                fecha_hora=fecha_hora, 
                contacto_id=contacto_id if contacto_id else None, 
                tipo_gestion=tipo_gestion,
                notas=notas,
                estado='Pendiente' 
            )
            nueva_agenda.save()

            productos_ids = request.POST.getlist('productos') 
            if productos_ids:
                nueva_agenda.productos.set(productos_ids)

            messages.success(request, _('Visita agendada correctamente.'))
            return redirect('visitas:dashboard') 

        except Exception as e:
            messages.error(request, f"{_('Error al agendar la visita:')} {e}")
            return redirect('visitas:agendar_visita')
        
    # --- 3. CARGA DE PANTALLA (GET) CON FILTRO ESTRICTO ---
    
    # Filtramos las instituciones basándonos en la jerarquía (igual que en registro)
    instituciones_filtradas = Institucion.objects.filter(
        Q(representante__in=vendedores_permitidos) | 
        Q(visitas_programadas__representante__in=vendedores_permitidos)
    ).distinct()

    context = {
        'instituciones': instituciones_filtradas, # ¡Ahora DEMO1 solo verá las suyas!
        'contactos': Contacto.objects.filter(institucion__in=instituciones_filtradas).distinct(),      
        'productos': Producto.objects.filter(stock__gt=0),
    }
    return render(request, 'visitas/agendar_visita.html', context)

# ==========================================
# VISTA HISTORIAL (CON JERARQUÍA)
# ==========================================
@login_required(login_url='usuarios:login')
def historial_view(request):
    query = request.GET.get('q', '')
    
    # --- 1. LÓGICA DE PERMISOS (Filtro Jerárquico) ---
    # Usamos la misma lógica que en 'nueva_visita' y 'agendar_visita'
    if request.user.is_superuser:
        # IMPORTANTE: Asegúrate de usar el modelo de Usuario correcto aquí (ej: UsuarioPersonalizado)
        vendedores_permitidos = UsuarioPersonalizado.objects.all() 
    elif getattr(request.user, 'es_gerente', False) or request.user.groups.filter(name='Gerente').exists():
        vendedores_permitidos = UsuarioPersonalizado.objects.filter(Q(id=request.user.id) | Q(jefe=request.user))
    else:
        vendedores_permitidos = UsuarioPersonalizado.objects.filter(id=request.user.id)
    
    # --- 2. TRAEMOS DATOS DE AMBOS MODELOS ---
    # Usamos select_related para optimizar las consultas a la base de datos
    agendas = Visita.objects.filter(representante__in=vendedores_permitidos).select_related('institucion', 'contacto', 'representante')
    registros = RegistroVisita.objects.filter(representante__in=vendedores_permitidos).select_related('institucion', 'contacto', 'representante')
    
    # --- 3. BUSCADOR INTELIGENTE UNIFICADO ---
    if query:
        filtro_busqueda = (
            Q(institucion__nombre__icontains=query) |
            Q(contacto__nombre__icontains=query) |
            Q(tipo_gestion__icontains=query) |
            Q(representante__first_name__icontains=query) | 
            Q(representante__username__icontains=query)
        )
        agendas = agendas.filter(filtro_busqueda)
        registros = registros.filter(filtro_busqueda)
        
    # --- 4. PREPARAR Y ESTANDARIZAR DATOS PARA EL HTML ---
    # Convertimos los querysets a listas para poder modificarlos e inyectar atributos
    lista_agendas = list(agendas)
    for a in lista_agendas:
        a.tipo_origen = 'Agendada' 
        # El modelo 'Visita' ya debería tener un campo 'estado' (Pendiente, Realizada, Cancelada)
        
    lista_registros = list(registros)
    for r in lista_registros:
        r.tipo_origen = 'Directa'
        # El modelo 'RegistroVisita' no suele tener campo de estado, así que se lo inventamos para el HTML
        # Le ponemos 'Completada' para que tu HTML pinte el borde verde ( #10B981 ) y el badge verde claro
        r.estado = 'Completada' 

    # --- 5. UNIR Y ORDENAR ---
    # Juntamos las dos listas y las ordenamos por 'fecha_hora' de más reciente a más antigua
    # ASUNCIÓN: Ambos modelos (Visita y RegistroVisita) deben tener un campo llamado 'fecha_hora'.
    historial_completo = sorted(
        chain(lista_agendas, lista_registros),
        key=attrgetter('fecha_hora'),
        reverse=True
    )
        
    # --- 6. PAGINACIÓN ---
    paginator = Paginator(historial_completo, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'total_registros': len(historial_completo), # Total de ambas listas combinadas
    }
    return render(request, 'visitas/historial.html', context)

# ==========================================
# VISTA DE AGENDA (CON JERARQUÍA)
# ==========================================
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
# Asegúrate de importar tu modelo Visita y Usuario

@login_required(login_url='usuarios:login')
def mi_agenda_view(request):
    fecha_str = request.GET.get('fecha')
    
    if fecha_str:
        try:
            fecha_seleccionada = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            fecha_seleccionada = timezone.now().date()
    else:
        fecha_seleccionada = timezone.now().date()
    
    # Calcular la semana
    lunes = fecha_seleccionada - timedelta(days=fecha_seleccionada.weekday())
    dias_semana = [lunes + timedelta(days=i) for i in range(7)]

    semana_anterior = fecha_seleccionada - timedelta(days=7)
    semana_siguiente = fecha_seleccionada + timedelta(days=7)

    # 1. LÓGICA DE PERMISOS (Jerarquía)
    if request.user.is_superuser:
        vendedores_permitidos = Usuario.objects.all()
    elif getattr(request.user, 'es_gerente', False) or request.user.groups.filter(name='Gerente').exists():
        vendedores_permitidos = Usuario.objects.filter(Q(id=request.user.id) | Q(jefe=request.user))
    else:
        vendedores_permitidos = Usuario.objects.filter(id=request.user.id)

    # --- 2. MAGIA DE FUSIÓN (TIMELINE DIARIO) ---
    # A) Buscamos las visitas programadas
    visitas_agendadas = Visita.objects.filter(
        representante__in=vendedores_permitidos,
        fecha_hora__date=fecha_seleccionada
    )

    # B) Buscamos las visitas espontáneas (Nueva Visita)
    visitas_espontaneas = RegistroVisita.objects.filter(
        representante__in=vendedores_permitidos,
        fecha_hora__date=fecha_seleccionada
    )
    
    # Truco de ingeniera: Como RegistroVisita no tiene campo "estado" por defecto, 
    # le inyectamos uno temporalmente para que tu HTML lo pinte verde (Realizada)
    for visita in visitas_espontaneas:
        visita.estado = 'Realizada'

    # Juntamos ambas listas y las ordenamos por hora
    visitas_dia = sorted(
        chain(visitas_agendadas, visitas_espontaneas),
        key=attrgetter('fecha_hora')
    )

   # --- 3. TABLA INFERIOR (PANEL GENERAL DE ACTIVIDAD) ---
    
    # A) Traemos las visitas agendadas (sin importar la fecha, solo las que no estén canceladas)
    lista_agendadas = Visita.objects.filter(
        representante__in=vendedores_permitidos
    ).exclude(estado='Cancelada')

    # B) Traemos todas las visitas espontáneas (RegistroVisita)
    lista_espontaneas = RegistroVisita.objects.filter(
        representante__in=vendedores_permitidos
    )
    
    # Inyectamos el estado para el diseño
    for v in lista_espontaneas:
        v.estado = 'Realizada'

    # C) Juntamos ambas listas y ordenamos de más nueva a más antigua
    todas_las_visitas = sorted(
        chain(lista_agendadas, lista_espontaneas),
        key=attrgetter('fecha_hora'),
        reverse=True
    )[:20] # Traemos los últimos 20 movimientos para agrupar

    # D) LA MAGIA: Agrupamos por Institución (Diccionario)
    visitas_agrupadas = {}
    for visita in todas_las_visitas:
        inst_id = visita.institucion.id
        if inst_id not in visitas_agrupadas:
            visitas_agrupadas[inst_id] = {
                'institucion': visita.institucion,
                'visitas': [], # Aquí guardaremos la lista del historial
                'conteo': 0,
                'ultima_fecha': visita.fecha_hora # Para mostrar cuándo fue la última
            }
        visitas_agrupadas[inst_id]['visitas'].append(visita)
        visitas_agrupadas[inst_id]['conteo'] += 1

    # Convertimos el diccionario en una lista para enviarla al HTML
    proximas_visitas = list(visitas_agrupadas.values())

    contexto = {
        'fecha_actual': fecha_seleccionada,
        'visitas': visitas_dia, 
        'proximas_visitas': proximas_visitas,
        'dias_semana': dias_semana, 
        'semana_anterior': semana_anterior,  
        'semana_siguiente': semana_siguiente, 
    }
    
    return render(request, 'visitas/agenda.html', contexto)

#----------------------------------
#-------VISTA CON JERARQUIA------
#----------------------------------
@login_required(login_url='usuarios:login')
def cambiar_estado_visita(request, visita_id, nuevo_estado):
    # 1. LÓGICA DE PERMISOS (Jerarquía)
    if request.user.is_superuser:
        vendedores_permitidos = Usuario.objects.all()
    elif getattr(request.user, 'es_gerente', False) or request.user.groups.filter(name='Gerente').exists():
        vendedores_permitidos = Usuario.objects.filter(Q(id=request.user.id) | Q(jefe=request.user))
    else:
        vendedores_permitidos = Usuario.objects.filter(id=request.user.id)

    # 2. Buscamos la visita dentro del equipo permitido (Evita el error 404)
    visita = get_object_or_404(Visita, id=visita_id, representante__in=vendedores_permitidos)
    
    # 3. Validamos por seguridad que el estado sea correcto
    estados_permitidos = ['Realizada', 'Pendiente', 'Cancelada', 'Completada']
    if nuevo_estado in estados_permitidos:
        visita.estado = nuevo_estado
        visita.save()
        messages.success(request, f'Estado actualizado a {nuevo_estado}.')
        
    # 4. Magia de navegación: Volver a la página exacta desde donde se hizo clic
    url_anterior = request.META.get('HTTP_REFERER', 'visitas:mi_agenda')
    return redirect(url_anterior)

#FUNCION CARGAR CONTACTOS EN JSON
def cargar_contactos_ajax(request):
    institucion_id = request.GET.get('institucion_id')
    contactos = Contacto.objects.filter(institucion_id=institucion_id).values('id', 'nombre', 'rol')
    return JsonResponse(list(contactos), safe=False)

