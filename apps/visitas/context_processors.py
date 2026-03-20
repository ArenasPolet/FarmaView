from django.db.models import Q
# IMPORTANTE: Cambia 'usuarios' por el nombre real de tu app de usuarios si es diferente
from apps.visitas.forms import Usuario
from apps.visitas.models import Visita


def notificaciones_campana(request):
    if not request.user.is_authenticated:
        return {}

    try:
        # 1. Jerarquía igual que en el Dashboard
        if request.user.is_superuser:
            # El admin ve TODAS las visitas pendientes
            alertas_qs = Visita.objects.filter(estado__icontains='Pendiente')
            
        elif getattr(request.user, 'es_gerente', False) or request.user.groups.filter(name='Gerente').exists():
            # El gerente ve las de todo su equipo
            vendedores_permitidos = Usuario.objects.filter(Q(id=request.user.id) | Q(jefe=request.user))
            alertas_qs = Visita.objects.filter(representante__in=vendedores_permitidos, estado__icontains='Pendiente')
            
        else:
            # El vendedor normal solo ve las suyas
            alertas_qs = Visita.objects.filter(representante=request.user, estado__icontains='Pendiente')

        # 2. Ordenamos por fecha (las más antiguas primero)
        alertas_qs = alertas_qs.select_related('institucion').order_by('fecha_hora')
        
        return {
            'notificaciones_campana': list(alertas_qs[:5]),
            'total_notificaciones': alertas_qs.count()
        }
        
    except Exception as e:
        # Si hay un error, lo imprimimos en la consola negra para saber qué falló
        print(f"DEBUG CAMPANA: Error al cargar notificaciones - {e}")
        return {'notificaciones_campana': [], 'total_notificaciones': 0}