from django.core.paginator import Paginator
from django.db.models import Q
from .models import Producto, Categoria
import csv
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test

def catalogo_view(request):
    # 1. Capturamos lo que el usuario quiere buscar y filtrar
    query = request.GET.get('q', '')
    categoria_id = request.GET.get('categoria', 'todos') # Por defecto es 'todos'
    
    # Empezamos con TODOS los productos
    lista_productos = Producto.objects.all().order_by('-id')
    
    # 2. Si escribió algo en el buscador, filtramos
    if query:
        lista_productos = lista_productos.filter(
            Q(nombre__icontains=query) | Q(codigo_sku__icontains=query)
        )
        
    # 3. Si seleccionó una categoría específica (y no es 'todos'), filtramos también por eso
    if categoria_id != 'todos':
        lista_productos = lista_productos.filter(categoria_id=categoria_id)
    
    # 4. Paginamos los resultados finales
    paginator = Paginator(lista_productos, 10)
    numero_pagina = request.GET.get('page')
    page_obj = paginator.get_page(numero_pagina)
    
    categorias = Categoria.objects.all()
    
    # 5. Mandamos todo al HTML
    context = {
        'productos': page_obj,
        'page_obj': page_obj,
        'categorias': categorias,
        'query': query,
        'categoria_activa': str(categoria_id), # Lo convertimos a texto para comparar en el HTML
    }
    return render(request, 'productos/catalogo.html', context)

# ---------------------------------------------------------
# 1. EL "GUARDIA DE SEGURIDAD"
# ---------------------------------------------------------
def es_gerente_check(user):
    # Preguntamos si el usuario existe y si su propiedad 'es_gerente' es Verdadera
    return user.is_authenticated and user.es_gerente

# =========================================================
# IMPORTADOR MASIVO DE CATÁLOGO (SOLO GERENCIA)
# =========================================================
@user_passes_test(es_gerente_check, login_url='visitas:dashboard')
def cargar_catalogo_view(request):
    if request.method == 'POST':
        if 'archivo_csv' not in request.FILES:
            messages.warning(request, "Por favor, selecciona un archivo CSV.")
            return redirect('productos:cargar_catalogo') # Ojo aquí, ahora redirige a productos:

        archivo = request.FILES['archivo_csv']

        if not archivo.name.endswith('.csv'):
            messages.error(request, "Formato inválido. Por favor sube un archivo terminado en .csv")
            return redirect('productos:cargar_catalogo')

        try:
            decoded_file = archivo.read().decode('utf-8-sig').splitlines()
            reader = csv.DictReader(decoded_file, delimiter=';')
            
            if not reader.fieldnames or len(reader.fieldnames) < 2:
                reader = csv.DictReader(decoded_file, delimiter=',')

            creados = 0
            actualizados = 0

            for row in reader:
                sku = row.get('SKU', '').strip()
                nombre = row.get('Nombre', '').strip()
                
                if not nombre: continue

                try: precio = int(float(row.get('Precio', 0)))
                except ValueError: precio = 0
                    
                try: stock = int(float(row.get('Stock', 0)))
                except ValueError: stock = 0

                categoria_nombre = row.get('Categoria', '').strip()
                categoria_obj = None
                if categoria_nombre:
                    categoria_obj, _ = Categoria.objects.get_or_create(nombre=categoria_nombre)

                if sku:
                    producto, creado = Producto.objects.update_or_create(
                        codigo_sku=sku,
                        defaults={'nombre': nombre, 'precio_lista': precio, 'stock': stock, 'categoria': categoria_obj}
                    )
                else:
                    producto, creado = Producto.objects.update_or_create(
                        nombre=nombre,
                        defaults={'precio_lista': precio, 'stock': stock, 'categoria': categoria_obj}
                    )

                if creado: creados += 1
                else: actualizados += 1

            messages.success(request, f"¡Éxito! Se actualizaron {actualizados} productos y se crearon {creados} nuevos.")
            
        except Exception as e:
            messages.error(request, f"Ocurrió un error al leer el archivo: {str(e)}")

        return redirect('productos:cargar_catalogo')

    # Apunta a la carpeta de templates de productos
    return render(request, 'productos/cargar_catalogo.html')