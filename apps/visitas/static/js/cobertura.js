// buscador de insituciones en cobertura 

document.addEventListener('DOMContentLoaded', function() {
    const inputBusqueda = document.getElementById('inputBuscador');
    const botonesFiltro = document.querySelectorAll('.btn-filtro');
    const tarjetas = document.querySelectorAll('.card-institucion');

    // Función principal de filtrado
    function filtrarLista() {
        const texto = inputBusqueda.value.toLowerCase().trim();
        const filtroActivo = document.querySelector('.btn-filtro.active').getAttribute('data-filtro');

        tarjetas.forEach(card => {
            const nombre = card.querySelector('h6').textContent.toLowerCase();
            const estado = card.getAttribute('data-estado'); // 'pendiente' o 'completa'

            // Condición 1: ¿Coincide con el texto buscado?
            const coincideTexto = nombre.includes(texto);
            
            // Condición 2: ¿Coincide con el botón de filtro seleccionado?
            const coincideFiltro = (filtroActivo === 'todos' || estado === filtroActivo);

            // Solo mostramos si cumple AMBAS condiciones
            if (coincideTexto && coincideFiltro) {
                card.style.display = '';
            } else {
                card.style.display = 'none';
            }
        });
    }

    // Escuchar el buscador
    if (inputBusqueda) {
        inputBusqueda.addEventListener('input', filtrarLista);
    }

    // Escuchar los botones de filtro
    botonesFiltro.forEach(boton => {
        boton.addEventListener('click', function() {
            // 1. Cambiar la clase 'active' visualmente
            botonesFiltro.forEach(b => b.classList.remove('active', 'text-dark', 'shadow-sm'));
            this.classList.add('active', 'text-dark', 'shadow-sm');

            // 2. Ejecutar el filtrado
            filtrarLista();
        });
    });
});