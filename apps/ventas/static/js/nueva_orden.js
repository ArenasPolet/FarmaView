document.addEventListener('DOMContentLoaded', function() {

    // =========================================================
    // 0. INICIALIZAR BUSCADORES (Tom Select)
    // =========================================================
    let tomSelectInstitucion = null;
    let tomSelectProducto = null;

    if (document.getElementById('selectInstitucion')) {
        tomSelectInstitucion = new TomSelect('#selectInstitucion', {
            create: false,
            placeholder: "Buscar cliente por nombre..."
        });
    }

    if (document.getElementById('selectProducto')) {
        tomSelectProducto = new TomSelect('#selectProducto', {
            create: false,
            placeholder: "Buscar producto por nombre..."
        });
    }

    // =========================================================
    // 1. AJAX DE CONTACTOS DINÁMICOS
    // =========================================================
    const selectInstitucion = document.getElementById('selectInstitucion');
    const selectContacto = document.getElementById('selectContacto');

    if (selectInstitucion && selectContacto) {
        selectInstitucion.addEventListener('change', function() {
            const institucionId = this.value;
            const urlBase = this.getAttribute('data-url');

            selectContacto.innerHTML = '<option value="">Cargando contactos...</option>';
            selectContacto.disabled = true;

            if (institucionId && urlBase) {
                const urlAjax = `${urlBase}?institucion_id=${institucionId}`;

                fetch(urlAjax)
                .then(response => {
                    if (!response.ok) throw new Error("Error en la red");
                    return response.json();
                })
                .then(data => {
                    selectContacto.innerHTML = '<option value="">Seleccione un contacto (Opcional)...</option>';
                    if(data.length > 0) {
                        data.forEach(contacto => {
                            selectContacto.innerHTML += `<option value="${contacto.id}">${contacto.nombre} (${contacto.rol})</option>`;
                        });
                        selectContacto.disabled = false;
                    } else {
                        selectContacto.innerHTML = '<option value="">Sin contactos registrados</option>';
                        selectContacto.disabled = false;
                    }
                })
                .catch(error => {
                    console.error("Error:", error);
                    selectContacto.innerHTML = '<option value="">Error de conexión.</option>';
                });
            } else {
                selectContacto.innerHTML = '<option value="">Primero seleccione una institución...</option>';
            }
        });
    }

    // =========================================================
    // 2. LÓGICA DEL CARRITO CON VALIDACIÓN DE STOCK Y SWEETALERT
    // =========================================================
    const btnAgregar = document.getElementById('btnAgregar');
    const selectProducto = document.getElementById('selectProducto');
    const inputCantidad = document.getElementById('inputCantidad');
    const carritoBody = document.getElementById('carritoBody');
    const filaVacia = document.getElementById('filaVacia');
    const totalEstimadoEl = document.getElementById('totalEstimado');
    const formOrden = document.getElementById('formOrden');

    let totalOrden = 0;

    if (btnAgregar) {
        btnAgregar.addEventListener('click', function() {
            const prodId = selectProducto.value;
            const cantidad = parseInt(inputCantidad.value);

            if (!prodId || cantidad < 1) {
                Swal.fire({
                    icon: 'warning',
                    title: 'Datos incompletos',
                    text: 'Por favor, busca un producto y asigna una cantidad.',
                    confirmButtonColor: '#1784C7'
                });
                return;
            }

            const option = selectProducto.querySelector(`option[value="${prodId}"]`);
            const prodNombre = option.getAttribute('data-nombre');
            const prodPrecio = parseInt(option.getAttribute('data-precio') || 0);
            const prodStock = parseInt(option.getAttribute('data-stock') || 0);

            if (cantidad > prodStock) {
                Swal.fire({
                    icon: 'error',
                    title: 'Stock Insuficiente',
                    text: `Solo quedan ${prodStock} unidades de ${prodNombre} en bodega.`,
                    confirmButtonColor: '#EF4444'
                });
                return;
            }

            const subtotal = prodPrecio * cantidad;
            totalOrden += subtotal;

            if (filaVacia) filaVacia.style.display = 'none';

            // AQUÍ APLICAMOS LA NUEVA CLASE PARA EL BOTÓN ELIMINAR (.btn-delete-row)
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td class="fw-bold text-dark ps-4">
                    ${prodNombre}
                    <input type="hidden" name="producto_id[]" value="${prodId}">
                </td>
                <td class="text-center">
                    <span class="badge bg-light text-dark border px-2 py-1">${cantidad}</span>
                    <input type="hidden" name="cantidad[]" value="${cantidad}">
                </td>
                <td class="text-end fw-bold text-brand-blue">$${subtotal.toLocaleString('es-CL')}</td>
                <td class="text-center pe-4">
                    <button type="button" class="btn btn-delete-row border-0 btn-eliminar" data-subtotal="${subtotal}" title="Eliminar">
                        <i class="bi bi-trash3-fill"></i>
                    </button>
                </td>
            `;

            carritoBody.appendChild(tr);
            actualizarTotal();

            if (tomSelectProducto) {
                tomSelectProducto.clear();
            } else {
                selectProducto.value = "";
            }
            inputCantidad.value = 1;
        });
    }

    if (carritoBody) {
        carritoBody.addEventListener('click', function(e) {
            if (e.target.closest('.btn-eliminar')) {
                const btn = e.target.closest('.btn-eliminar');
                const subtotalRestar = parseInt(btn.getAttribute('data-subtotal'));
                totalOrden -= subtotalRestar;
                btn.closest('tr').remove();

                if (carritoBody.children.length === 1 && carritoBody.children[0].id === 'filaVacia') {
                    filaVacia.style.display = 'table-row';
                }
                actualizarTotal();
            }
        });
    }

    function actualizarTotal() {
        if (totalEstimadoEl) {
            totalEstimadoEl.innerText = '$' + totalOrden.toLocaleString('es-CL');
        }
    }

    // =========================================================
    // 3. VALIDACIÓN ESTRICTA AL GUARDAR 
    // =========================================================
    if (formOrden) {
        formOrden.addEventListener('submit', function(e) {
            const items = document.querySelectorAll('input[name="producto_id[]"]');

            if (items.length === 0) {
                e.preventDefault();
                Swal.fire({
                    icon: 'info',
                    title: 'Carrito Vacío',
                    text: 'Debes agregar al menos un producto al carrito para guardar la orden.',
                    confirmButtonColor: '#F59E0B'
                });
                return;
            }
        });
    }
});