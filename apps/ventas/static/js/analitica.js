document.addEventListener('DOMContentLoaded', function() {
    
    // 1. EXTRAER DATOS DEL HTML
    // Gráficos 1 y 2 (Mensuales)
    const mesesLabels = JSON.parse(document.getElementById('dataMesesLabels').textContent);
    const mesesData = JSON.parse(document.getElementById('dataMesesValues').textContent);
    const mesesPedidos = JSON.parse(document.getElementById('dataMesesPedidos').textContent);
    
    // Gráfico 3 (Instituciones)
    const instLabels = JSON.parse(document.getElementById('dataInstLabels').textContent);
    const instData = JSON.parse(document.getElementById('dataInstValues').textContent);
    
    // Gráfico 4 (Representantes)
    const repLabels = JSON.parse(document.getElementById('dataRepLabels').textContent);
    const repData = JSON.parse(document.getElementById('dataRepValues').textContent);

    // Gráfico 5 (Histórico)
    const histLabels = JSON.parse(document.getElementById('dataHistLabels').textContent);
    const histData = JSON.parse(document.getElementById('dataHistValues').textContent);

    // Gráfico 6 (Productos)
    const prodLabels = JSON.parse(document.getElementById('dataProdLabels').textContent);
    const prodData = JSON.parse(document.getElementById('dataProdValues').textContent);

    // 2. CONFIGURACIÓN DE COLORES
    const colorBlue = '#0ea5e9';
    const colorBlueBg = 'rgba(14, 165, 233, 0.2)';
    const colorGreen = '#10b981';
    const colorPurple = '#8b5cf6';
    const colorOrange = '#f59e0b';
    const palette = ['#0ea5e9', '#f59e0b', '#10b981', '#6366f1', '#ec4899'];
    
    // ==========================================
    // ESCUCHADOR DEL FILTRO DE AÑO
    // ==========================================
    const selectAnio = document.getElementById('selectAnio');
    if (selectAnio) {
        selectAnio.addEventListener('change', function() {
            window.location.href = window.location.pathname + '?anio=' + this.value;
        });
    }

    //selec mes//

    const selectMes = document.getElementById('selectMes');
        if (selectMes) {
            selectMes.addEventListener('change', function() {
                const url = new URL(window.location.href);
                url.searchParams.set('mes', this.value);
                window.location.href = url.href;
            });
        }

    // ==========================================
    // GRÁFICO 1: Ingresos ($) Mensuales (LÍNEA)
    // ==========================================
    const ctxMeses = document.getElementById('chartMeses');
    if (ctxMeses) {
        new Chart(ctxMeses.getContext('2d'), {
            type: 'line',
            data: {
                labels: mesesLabels,
                datasets: [{
                    label: 'Ingresos Netos ($)',
                    data: mesesData,
                    borderColor: colorBlue,
                    backgroundColor: colorBlueBg,
                    borderWidth: 3,
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: '#ffffff',
                    pointBorderColor: colorBlue,
                    pointRadius: 5,
                    pointHoverRadius: 7
                }]
            },
            options: {
                responsive: true,
                animation: {
                    duration: 0 // <--- OJO: Si pones 0, el PDF saldrá instantáneo y perfecto
                },
                devicePixelRatio: 2,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, grid: { color: '#f1f5f9' }, border: { display: false } },
                    x: { grid: { display: false }, border: { display: false } }
                }
                
            }
        });
    }

    // ==========================================
    // GRÁFICO 2: Volumen Mensual de Pedidos (BARRAS VERTICALES)
    // ==========================================
    const ctxVentas = document.getElementById('chartVentasMensuales');
    if (ctxVentas) {
        new Chart(ctxVentas.getContext('2d'), {
            type: 'bar',
            data: {
                labels: mesesLabels, 
                datasets: [{
                    label: 'Cantidad de Pedidos',
                    data: mesesPedidos,
                    backgroundColor: colorGreen, 
                    borderRadius: 6,
                    barPercentage: 0.6
                }]
            },
            options: {
                responsive: true,
                animation: {
                    duration: 0 // <--- OJO: Si pones 0, el PDF saldrá instantáneo y perfecto
                },
                devicePixelRatio: 2,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { display: false }, border: { display: false } },
                    y: { beginAtZero: true, grid: { color: '#f1f5f9', borderDash: [5, 5] }, border: { display: false }, ticks: { precision: 0 } }
                }
            }
        });
    }

    // ==========================================
    // GRÁFICO 3: Instituciones (DONA)
    // ==========================================
    const ctxInst = document.getElementById('chartInstituciones');
    if (ctxInst) {
        new Chart(ctxInst.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: instLabels,
                datasets: [{
                    data: instData,
                    backgroundColor: palette,
                    borderWidth: 0,
                    hoverOffset: 10
                }]
            },
            options: {
                responsive: true,
                animation: {
                    duration: 0 // <--- OJO: Si pones 0, el PDF saldrá instantáneo y perfecto
                },
                devicePixelRatio: 2,
                maintainAspectRatio: false,
                cutout: '75%',
                plugins: {
                    legend: { position: 'bottom', labels: { padding: 10, usePointStyle: true } }
                }
            }
        });
    }

    // ==========================================
    // GRÁFICO 4: Representantes (BARRAS HORIZONTALES)
    // ==========================================
    const ctxReps = document.getElementById('chartReps');
    if (ctxReps) {
        new Chart(ctxReps.getContext('2d'), {
            type: 'bar',
            data: {
                labels: repLabels,
                datasets: [{
                    label: 'Ventas Totales ($)',
                    data: repData,
                    backgroundColor: colorBlue,
                    borderRadius: 6,
                    barThickness: 25
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                animation: {
                    duration: 0 // <--- OJO: Si pones 0, el PDF saldrá instantáneo y perfecto
                },
                devicePixelRatio: 2,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { beginAtZero: true, grid: { color: '#f1f5f9' }, border: { display: false } },
                    y: { grid: { display: false }, border: { display: false } }
                }
            }
        });
    }

    // ==========================================
    // GRÁFICO 5: Crecimiento Histórico Anual (BARRAS VERTICALES)
    // ==========================================
    const ctxHist = document.getElementById('chartHistoricoAnual');
    if (ctxHist) {
        new Chart(ctxHist.getContext('2d'), {
            type: 'bar',
            data: {
                labels: histLabels,
                datasets: [{
                    label: 'Ingresos Históricos ($)',
                    data: histData,
                    backgroundColor: colorPurple,
                    borderRadius: 6,
                    barPercentage: 0.5
                }]
            },
            options: {
                responsive: true,
                animation: {
                    duration: 0 // <--- OJO: Si pones 0, el PDF saldrá instantáneo y perfecto
                },
                devicePixelRatio: 2,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { display: false }, border: { display: false } },
                    y: { beginAtZero: true, grid: { color: '#f1f5f9', borderDash: [5, 5] }, border: { display: false } }
                }
            }
        });
    }

    // ==========================================
    // GRÁFICO 6: Top 5 Productos (BARRAS HORIZONTALES)
    // ==========================================
    const ctxProd = document.getElementById('chartProductos');
    if (ctxProd) {
        new Chart(ctxProd.getContext('2d'), {
            type: 'bar',
            data: {
                labels: prodLabels, 
                datasets: [{
                    label: 'Unidades Vendidas',
                    data: prodData,
                    backgroundColor: colorOrange,
                    borderRadius: 6,
                    barThickness: 25
                }]
            },
            options: {
                indexAxis: 'y', 
                responsive: true,
                animation: {
                    duration: 0 // <--- OJO: Si pones 0, el PDF saldrá instantáneo y perfecto
                },
                devicePixelRatio: 2,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { beginAtZero: true, grid: { color: '#f1f5f9' }, border: { display: false }, ticks: { precision: 0 } },
                    y: { grid: { display: false }, border: { display: false } }
                }
            }
        });
    }
});

// ==========================================================
// FUNCIÓN GLOBAL DE EXPORTACIÓN A PDF (LÓGICA OPTIMIZADA)
// ==========================================================
window.descargarPDFAnalitica = async function(event) {
    if (event) event.preventDefault();
    
    // 1. Resetear posición del scroll para evitar cortes negros
    window.scrollTo(0, 0);

    const { jsPDF } = window.jspdf;
    const elemento = document.getElementById('reporte-analitica');

    if (!elemento) {
        alert("Error: No se encontró el área 'reporte-analitica'");
        return;
    }

    const btn = event.currentTarget;
    const originalHTML = btn.innerHTML;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Generando...';
    btn.classList.add('disabled');

    try {
        // Pausa para que la interfaz se estabilice
        await new Promise(resolve => setTimeout(resolve, 600)); 

        const canvas_captura = await html2canvas(elemento, {
            scale: 2,           
            useCORS: true,      
            backgroundColor: "#f8fafc", 
            logging: false,
            // Forzamos un ancho de ventana virtual para que el diseño no se rompa en móvil
            windowWidth: 1400,
            onclone: (clonedDoc) => {
                const reporteClonado = clonedDoc.getElementById('reporte-analitica');
                reporteClonado.style.width = "1400px";
                reporteClonado.style.padding = "20px";
                
                // Convertimos cada Canvas en Imagen fija para que aparezcan en el PDF
                const canvases = clonedDoc.getElementsByTagName('canvas');
                const originalCanvases = document.getElementsByTagName('canvas');
                
                for (let i = 0; i < canvases.length; i++) {
                    const dataUrl = originalCanvases[i].toDataURL("image/png");
                    const img = clonedDoc.createElement('img');
                    img.src = dataUrl;
                    img.style.width = "100%";
                    img.style.height = "auto";
                    img.style.display = "block";
                    
                    canvases[i].parentNode.replaceChild(img, canvases[i]);
                }
            }
        });

        const imgData = canvas_captura.toDataURL('image/png', 1.0);
        
        if (imgData.length < 5000) {
            throw new Error("Imagen generada demasiado pequeña");
        }

        // Definimos ancho estándar A4 (210mm) y calculamos alto proporcional para no cortar nada
        const pdfWidth = 210; 
        const pdfHeight = (canvas_captura.height * pdfWidth) / canvas_captura.width;

        // Creamos el PDF con las medidas exactas del contenido
        const pdf = new jsPDF('p', 'mm', [pdfWidth, pdfHeight]);
        pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight, undefined, 'FAST');
        
        pdf.save(`Reporte_FarmaView_Analitica_${new Date().getFullYear()}.pdf`);

    } catch (error) {
        console.error("Error al generar PDF:", error);
        alert("Hubo un problema técnico al generar el PDF. Por favor, refresca la página e intenta de nuevo.");
    } finally {
        btn.innerHTML = originalHTML;
        btn.classList.remove('disabled');
    }
};