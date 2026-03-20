
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('buscadorHistorial');
    const tableBody = document.getElementById('tablaPedidosBody');
    const trs = Array.from(tableBody.querySelectorAll('.fila-pedido')); // Solo tomamos filas reales
    const contenedorPaginacion = document.getElementById('contenedorPaginacion');
    const infoPaginacion = document.getElementById('infoPaginacion');
    const ulPaginacion = document.getElementById('ulPaginacion');
    
    // Configuración
    const rowsPerPage = 10; // Cuántas ventas quieres mostrar por página
    let currentPage = 1;
    let filteredRows = [...trs]; // Inicia con todas las filas
    
    // Si no hay pedidos, no hacemos nada
    if (trs.length === 0) return;

    // Función principal que dibuja la tabla
    function renderTable() {
        // 1. Filtrar por el texto del buscador
        const searchTerm = searchInput.value.toLowerCase().trim();
        filteredRows = trs.filter(tr => {
            const instName = tr.querySelector('.nombre-institucion').textContent.toLowerCase();
            return instName.includes(searchTerm);
        });

        // 2. Calcular páginas
        const totalPages = Math.ceil(filteredRows.length / rowsPerPage) || 1;
        if (currentPage > totalPages) currentPage = totalPages;
        if (currentPage < 1) currentPage = 1;

        // 3. Ocultar todas y mostrar solo las de la página actual
        const start = (currentPage - 1) * rowsPerPage;
        const end = start + rowsPerPage;

        trs.forEach(tr => tr.style.display = 'none'); // Esconder todas
        filteredRows.slice(start, end).forEach(tr => tr.style.display = ''); // Mostrar segmento

        // 4. Actualizar textos y botones
        renderPagination(totalPages, start, end);
    }

    function renderPagination(totalPages, start, end) {
        // Si hay menos de 1 página (o solo 1), podemos ocultar el paginador para que sea más limpio
        if (filteredRows.length <= rowsPerPage && searchInput.value === '') {
            contenedorPaginacion.style.setProperty('display', 'none', 'important');
            return;
        } else {
            contenedorPaginacion.style.setProperty('display', 'flex', 'important');
        }

        // Texto informativo
        const totalItems = filteredRows.length;
        const actualEnd = Math.min(end, totalItems);
        infoPaginacion.innerHTML = `Mostrando <span class="fw-bold text-dark">${totalItems === 0 ? 0 : start + 1} - ${actualEnd}</span> de <span class="fw-bold text-dark">${totalItems}</span>`;

        // Limpiar botones anteriores
        ulPaginacion.innerHTML = '';

        // Botón Anterior
        const prevLi = document.createElement('li');
        prevLi.className = `page-item ${currentPage === 1 ? 'disabled' : ''}`;
        prevLi.innerHTML = `<a class="page-link border-0 rounded-circle text-dark shadow-sm" href="#" style="width: 32px; height: 32px; display: flex; align-items: center; justify-content: center;"><i class="bi bi-chevron-left"></i></a>`;
        prevLi.addEventListener('click', (e) => { e.preventDefault(); if (currentPage > 1) { currentPage--; renderTable(); } });
        ulPaginacion.appendChild(prevLi);

        // Números de Página
        for (let i = 1; i <= totalPages; i++) {
            const li = document.createElement('li');
            li.className = `page-item ${currentPage === i ? 'active' : ''}`;
            li.innerHTML = `<a class="page-link border-0 rounded-circle fw-bold shadow-sm mx-1 ${currentPage === i ? 'bg-primary text-white' : 'text-dark bg-light'}" href="#" style="width: 32px; height: 32px; display: flex; align-items: center; justify-content: center;">${i}</a>`;
            li.addEventListener('click', (e) => {
                e.preventDefault();
                currentPage = i;
                renderTable();
            });
            ulPaginacion.appendChild(li);
        }

        // Botón Siguiente
        const nextLi = document.createElement('li');
        nextLi.className = `page-item ${currentPage === totalPages || totalPages === 0 ? 'disabled' : ''}`;
        nextLi.innerHTML = `<a class="page-link border-0 rounded-circle text-dark shadow-sm" href="#" style="width: 32px; height: 32px; display: flex; align-items: center; justify-content: center;"><i class="bi bi-chevron-right"></i></a>`;
        nextLi.addEventListener('click', (e) => { e.preventDefault(); if (currentPage < totalPages) { currentPage++; renderTable(); } });
        ulPaginacion.appendChild(nextLi);
    }

    // Escuchar cuando el usuario escribe en el buscador
    searchInput.addEventListener('input', function() {
        currentPage = 1; // Volver a la página 1 al buscar
        renderTable();
    });

    // Iniciar
    renderTable();
});
