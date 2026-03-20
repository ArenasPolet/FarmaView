from django.http import JsonResponse
from .models import Institucion, Contacto  # <-- IMPORTANTE: Asegúrate de importar Contacto

# 1. FUNCIÓN PARA GUARDAR INSTITUCIÓN
def guardar_institucion_ajax(request):
    if request.method == "POST":
        print("--- LLEGÓ AJAX INSTITUCIÓN ---")
        print(request.POST) 
        
        nombre = request.POST.get('nombre')
        razon_social = request.POST.get('razon_social')
        rut = request.POST.get('rut')
        direccion = request.POST.get('direccion')
        comuna = request.POST.get('comuna')
        tipo = request.POST.get('tipo')
        # Captura exacta de los nuevos campos
        horario = request.POST.get('horario_preferido')
        notas_cont = request.POST.get('notas')
        # Convertimos el string "true"/"false" del JS a un Booleano real de Python
        decisor_raw = request.POST.get('decisor_compra')
        es_decisor = True if decisor_raw == 'true' else False

        inst_id = request.POST.get('institucion_id')
        print(f"DEBUG: Guardando {nombre} para inst {inst_id}. Decisor: {es_decisor}")

        if nombre and rut:
            try:
                inst = Institucion.objects.create(
                    nombre=nombre, razon_social=razon_social, rut=rut, direccion=direccion, comuna=comuna, tipo=tipo,horario=horario,
                    notas_cont=notas_cont,decisor_raw=decisor_raw
                )
                return JsonResponse({'status': 'success', 'id': inst.id, 'nombre': f"{inst.nombre} ({inst.rut})"})
            except Exception as e:
                print("Error de Base de Datos:", str(e))
                return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
                
    return JsonResponse({'status': 'error', 'message': 'Faltan datos obligatorios'}, status=400)


# 2. FUNCIÓN PARA GUARDAR CONTACTO 
def guardar_contacto_ajax(request):
    if request.method == "POST":
        print("--- LLEGÓ AJAX CONTACTO ---")
        print(request.POST)

        nombre = request.POST.get('nombre')
        rol = request.POST.get('rol')
        especialidad = request.POST.get('especialidad')
        telefono = request.POST.get('telefono')
        email = request.POST.get('email')
        horario_preferido = request.POST.get('horario_preferido')
        notas = request.POST.get('notas')
        # Los booleanos desde JS llegan como strings de texto
        decisor_compra = True if request.POST.get('decisor_compra') == 'true' else False
        institucion_id = request.POST.get('institucion_id')

        if nombre and institucion_id:
            try:
                contacto = Contacto.objects.create(
                    nombre=nombre, 
                    rol=rol,
                    especialidad=especialidad,
                    telefono=telefono,
                    email=email,
                    horario_preferido=horario_preferido,
                    notas=notas,
                    decisor_compra=decisor_compra,
                    institucion_id=institucion_id
                )
                return JsonResponse({'status': 'success', 'id': contacto.id, 'nombre': f"{contacto.nombre} - {contacto.rol}"})
            except Exception as e:
                print("Error de Base de Datos al guardar contacto:", str(e))
                return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Faltan datos o institución'}, status=400)