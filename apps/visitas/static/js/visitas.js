/**
 * Lógica de Negocio para Nueva Visita - FarmaView
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // --- Inicialización de Modales de Bootstrap ---
    const modalElementProd = document.getElementById('modalProductos');
    const modalElementOtro = document.getElementById('modalOtro');
    
    const modalProd = modalElementProd ? new bootstrap.Modal(modalElementProd) : null;
    const modalO = modalElementOtro ? new bootstrap.Modal(modalElementOtro) : null;

    // =========================================================================
        // FILTRO DINÁMICO DE CONTACTOS POR INSTITUCIÓN (Versión Corregida)
        // =========================================================================
        const selectInstitucion = document.getElementById('id_institucion');
        const selectContacto = document.getElementById('id_contacto');

if (selectInstitucion && selectContacto) {
    // Estado inicial
    if (!selectInstitucion.value) {
        selectContacto.disabled = true;
        selectContacto.innerHTML = '<option value="">Seleccione Institución primero...</option>';
    }

    selectInstitucion.addEventListener('change', function() {
        const institucionId = this.value;
        
        if (institucionId) {
            selectContacto.innerHTML = '<option value="">Cargando contactos...</option>';
            selectContacto.disabled = true;

            // IMPORTANTE: Verifica que esta URL sea la misma que en tu urls.py
            
            fetch(`/visitas/cargar-contactos-ajax/?institucion_id=${institucionId}`)
                .then(response => {
                    if (!response.ok) throw new Error('Error en la red');
                    return response.json();
                })
                .then(data => {
                    selectContacto.innerHTML = '<option value="">¿Con quién realizó la gestión?</option>';
                    
                    if (data.length > 0) {
                        data.forEach(contacto => {
                            const option = document.createElement('option');
                            option.value = contacto.id;
                            option.textContent = `${contacto.nombre} - ${contacto.rol}`;
                            selectContacto.appendChild(option);
                        });
                        selectContacto.disabled = false;
                    } else {
                        selectContacto.innerHTML = '<option value="">No hay contactos en esta institución</option>';
                        selectContacto.disabled = true;
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    selectContacto.innerHTML = '<option value="">Error al cargar contactos</option>';
                });
        } else {
            selectContacto.innerHTML = '<option value="">Seleccione Institución primero...</option>';
            selectContacto.disabled = true;
        }
    });
}
});
    // --- ESCUCHADORES PARA BOTONES AJAX (INSTITUCIÓN Y CONTACTO) ---
    
   // Botón Guardar Institución
    const btnInst = document.getElementById('btnGuardarInst');
    if (btnInst) {
        btnInst.onclick = function(e) {
            e.preventDefault();
            const url = this.getAttribute('data-url');
            const csrf = this.getAttribute('data-csrf');
            guardarInstitucionRapido(url, csrf);
        };
    }

    // Botón Guardar Contacto
    const btnCont = document.getElementById('btnGuardarCont');
    if (btnCont) {
        btnCont.onclick = function(e) {
            e.preventDefault();
            const url = this.getAttribute('data-url');
            const csrf = this.getAttribute('data-csrf');
            guardarContactoRapido(url, csrf);
        };
    }

    // --- Funciones Globales (asignadas a window para acceso desde HTML) ---
    window.abrirModalProductos = () => { if(modalProd) modalProd.show(); };
    window.abrirModalOtro = () => { if(modalO) modalO.show(); };

    // --- Lógica del Selector de Productos ---
    window.confirmarSeleccionProductos = function() {
        const checkboxes = document.querySelectorAll('input[name="product_checkbox"]:checked');
        const container = document.getElementById('hidden_products_container');
        
        if (!container) return;
        container.innerHTML = ''; 

        checkboxes.forEach(cb => {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'productos'; 
            input.value = cb.value;
            container.appendChild(input);
        });

        const cant = checkboxes.length;
        const display = document.getElementById('product_selector_display');
        const badge = document.getElementById('product_selection_badge');
        const badgeText = document.getElementById('badge_text');

        if (cant > 0) {
            if (display) display.classList.add('d-none');
            if (badge) badge.classList.remove('d-none');
            if (badgeText) badgeText.innerText = cant === 1 ? "1 Producto" : `${cant} Productos`;
        } else {
            if (display) display.classList.remove('d-none');
            if (badge) badge.classList.add('d-none');
        }

        if (modalElementProd) {
            const modalInst = bootstrap.Modal.getInstance(modalElementProd) || new bootstrap.Modal(modalElementProd);
            modalInst.hide();
        }
    };

    // --- BUSCADOR DE PRODUCTOS ---
    document.addEventListener('input', function (event) {
        if (event.target.id === 'input_busqueda_productos') {
            const texto = event.target.value.toLowerCase().trim();
            const tarjetas = document.querySelectorAll('.product-item');

            tarjetas.forEach(tarjeta => {
                const nombre = tarjeta.getAttribute('data-name')?.toLowerCase();
                if (nombre) {
                    tarjeta.style.display = nombre.includes(texto) ? 'block' : 'none';
                }
            });
        }
    });

    // --- Lógica del Botón Editable "Otro" ---
    window.aplicarOtro = function() {
        const nombre = document.getElementById('custom_gestion_name').value;
        const iconSelect = document.querySelector('input[name="icon_choice"]:checked');
        
        if(nombre && iconSelect) {
            const icon = iconSelect.value;
            document.getElementById('otro_label').innerText = nombre;
            document.getElementById('gest_otro').value = nombre; 
            document.getElementById('otro_icon').className = `bi ${icon} gestion-icon`;
            if (modalO) modalO.hide();
        }
    };

// --- AJAX Guardar Institución ---
window.guardarInstitucionRapido = function(url, csrf) {
    const inputNombre = document.getElementById('inst_nombre');
    const inputRazonSocial = document.getElementById('inst_razon_social'); // <-- 1. CAPTURAMOS EL NUEVO CAMPO
    const inputRut = document.getElementById('inst_rut');
    
    const datos = {
        nombre: inputNombre.value,
        razon_social: inputRazonSocial.value, // <-- 2. LO AGREGAMOS AL PAQUETE DE DATOS
        rut: inputRut.value,
        direccion: document.getElementById('inst_direccion').value,
        comuna: document.getElementById('inst_comuna').value,
        tipo: document.getElementById('inst_tipo').value,
    };
    
    if(!datos.nombre || !datos.rut) { alert("Nombre y RUT obligatorios."); return; }

    fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded", "X-CSRFToken": csrf },
        body: new URLSearchParams(datos)
    })
    .then(res => res.json())
    .then(data => {
        if(data.status === 'success') {
            const selectInst = document.getElementById('id_institucion');
            selectInst.add(new Option(data.nombre, data.id, true, true));
            
            // ESTO ES CLAVE: Disparamos el evento 'change' para que se active nuestro filtro dinámico
            selectInst.dispatchEvent(new Event('change'));

            alert("Institución guardada exitosamente.");
            
            const collapseElement = document.getElementById('collapseNuevaInstitucion');
            if (collapseElement) bootstrap.Collapse.getInstance(collapseElement).hide();

            // 3. LIMPIAMOS TODOS LOS CAMPOS
            inputNombre.value = '';
            inputRazonSocial.value = ''; // <-- LIMPIAMOS LA RAZÓN SOCIAL
            inputRut.value = '';
            document.getElementById('inst_direccion').value = '';
            document.getElementById('inst_comuna').value = '';
            
        } else {
            alert("Error: " + data.message);
        }
    })
    .catch(err => console.error("Error en fetch institución:", err));
};



//GUARDAR CONTACTO ajax

    window.guardarContactoRapido = function(url, csrf) {
    const inst_id = document.getElementById('id_institucion').value;
    if (!inst_id) { alert("Primero selecciona una Institución."); return; }

    const inputNombreCont = document.getElementById('cont_nombre');
    const inputHorario = document.getElementById('cont_horario');
    const inputNotas = document.getElementById('cont_notas');
    const inputDecisor = document.getElementById('cont_decisor');

    const datos = {
        nombre: inputNombreCont.value,
        rol: document.getElementById('cont_rol').value,
        especialidad: document.getElementById('cont_especialidad').value,
        telefono: document.getElementById('cont_telefono').value,
        email: document.getElementById('cont_email').value,
        horario_preferido: inputHorario.value, // Coincide con el request.POST.get
        notas: inputNotas.value,              // Coincide con el request.POST.get
        decisor_compra: inputDecisor.checked,  // Envía true/false
        institucion_id: inst_id
    };
    
    if(!datos.nombre) { alert("El nombre es obligatorio."); return; }

    fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded", "X-CSRFToken": csrf },
        body: new URLSearchParams(datos)
    })
    .then(res => res.json())
    .then(data => {
        if(data.status === 'success') {
            const selectCont = document.getElementById('id_contacto');
            selectCont.add(new Option(data.nombre, data.id, true, true));
            selectCont.dispatchEvent(new Event('change'));

            alert("✅ Contacto guardado exitosamente.");
            
            const collapseElement = document.getElementById('collapseNuevoContacto');
            if (collapseElement) bootstrap.Collapse.getInstance(collapseElement).hide();

            // LIMPIEZA TOTAL DE CAMPOS
            inputNombreCont.value = '';
            inputHorario.value = '';
            inputNotas.value = '';
            inputDecisor.checked = false;
            document.getElementById('cont_telefono').value = '';
            document.getElementById('cont_email').value = '';
            document.getElementById('cont_especialidad').value = '';

        } else {
            alert("Error: " + data.message);
        }
    })
    .catch(err => console.error("Error en fetch contacto:", err));
};
  
// --- Dictado por voz (Versión Escritura en Vivo) ---
window.iniciarDictado = function() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        
        recognition.lang = "es-CL"; 
        recognition.continuous = false; 
        recognition.interimResults = true; // ✨ LA MAGIA: Muestra los resultados en tiempo real
        
        const btnDictar = document.querySelector('button[onclick="iniciarDictado()"]');
        const textarea = document.getElementById('notas_textarea');
        const contenidoOriginal = btnDictar.innerHTML; 
        
        let textoGuardado = textarea.value; // Guardamos lo que ya estaba escrito en la caja

        recognition.onstart = function() {
            btnDictar.innerHTML = '<i class="bi bi-mic-fill me-2 text-danger"></i> Escuchando...';
            btnDictar.style.color = "#dc3545"; // Se pone rojo para avisar que está grabando
        };

        // Esta función ahora se dispara cada vez que dices una palabra
        recognition.onresult = function(event) { 
            let textoTemporal = '';
            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    // Si terminó la frase, la guarda permanentemente
                    textoGuardado += (textoGuardado.length > 0 ? " " : "") + event.results[i][0].transcript;
                } else {
                    // Si sigue hablando, lo muestra temporalmente
                    textoTemporal += event.results[i][0].transcript;
                }
            }
            // Actualiza la caja de texto en vivo
            textarea.value = textoGuardado + (textoTemporal ? " " + textoTemporal : ""); 
        };

        recognition.onend = function() {
            btnDictar.innerHTML = contenidoOriginal;
            btnDictar.style.color = ""; // Vuelve a la normalidad
        };

        recognition.onerror = function(event) {
            console.error("Error del micrófono:", event.error);
            if (event.error === 'not-allowed') {
                alert("Debes permitir el acceso al micrófono en la barra de direcciones (candado) y usar HTTPS.");
            }
            btnDictar.innerHTML = contenidoOriginal; 
        };

        recognition.start();

    } else { 
        alert("Tu navegador actual no soporta el dictado por voz. Usa Safari o Google Chrome actualizados."); 
    }
};