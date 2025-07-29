class ServiceMonitor {
    constructor() {
        this.services = [];
        this.updateInterval = 30000; // 30 segundos
        this.modal = document.getElementById('modal-overlay');
        this.currentSegmentData = null;
        this.init();
    }

    init() {
        // Obtener servicios de la página
        document.querySelectorAll('.service-panel').forEach(panel => {
            this.services.push(panel.dataset.service);
        });

        // Crear segmentos de tiempo para cada servicio
        this.createTimeSegments();

        // Cargar datos iniciales
        this.loadAllData();

        // Configurar actualización automática
        setInterval(() => this.loadAllData(), this.updateInterval);

        // Configurar eventos del modal
        this.setupModalEvents();
    }

    createTimeSegments() {
        this.services.forEach(service => {
            const timeBar = document.getElementById(`timebar-${service}`);
            timeBar.innerHTML = '';

            // Crear 288 segmentos (24 horas * 12 segmentos por hora = cada 5 minutos)
            for (let i = 0; i < 288; i++) {
                const segment = document.createElement('div');
                segment.className = 'time-segment no-data';
                segment.dataset.service = service;
                segment.dataset.timeIndex = i;
                
                // Calcular tiempo
                const totalMinutes = i * 5;
                const hours = Math.floor(totalMinutes / 60);
                const minutes = totalMinutes % 60;
                const timeStr = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
                segment.dataset.time = timeStr;
                
                timeBar.appendChild(segment);
            }
        });
    }

    async loadAllData() {
        try {
            const response = await fetch('/api/data');
            const data = await response.json();
            
            this.services.forEach(service => {
                this.updateServiceDisplay(service, data[service] || {});
            });
        } catch (error) {
            console.error('Error loading data:', error);
        }
    }

    updateServiceDisplay(service, serviceData) {
        // Actualizar indicador de estado
        const statusIndicator = document.getElementById(`status-${service}`);
        const lastUpdateElement = document.getElementById(`lastupdate-${service}`);
        const timeBar = document.getElementById(`timebar-${service}`);

        // Obtener último estado
        const times = Object.keys(serviceData).sort();
        const lastTime = times[times.length - 1];
        const lastStatus = lastTime ? serviceData[lastTime].status : 'no-data';

        // Actualizar indicador principal
        statusIndicator.className = `status-indicator ${lastStatus}`;
        lastUpdateElement.textContent = lastTime ? 
            `Última actualización: ${this.formatTimestamp(serviceData[lastTime].timestamp)}` : 
            'Sin datos';

        // Actualizar segmentos de tiempo
        const segments = timeBar.querySelectorAll('.time-segment');
        segments.forEach(segment => {
            const time = segment.dataset.time;
            if (serviceData[time]) {
                segment.className = `time-segment ${serviceData[time].status}`;
                segment.dataset.hasData = 'true';
                
                // Guardar datos para el tooltip
                segment.dataset.timestamp = serviceData[time].timestamp;
                segment.dataset.request = serviceData[time].request;
                segment.dataset.response = serviceData[time].response;
                segment.dataset.error = serviceData[time].error || '';
            } else {
                segment.className = 'time-segment no-data';
                segment.dataset.hasData = 'false';
            }
        });
    }

    setupModalEvents() {
        // Event listener para click en segmentos
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('time-segment') && e.target.dataset.hasData === 'true') {
                this.showModal(e.target);
                e.preventDefault();
            }
        });

        // Cerrar modal con ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeModal();
            }
        });
    }

    showModal(segment) {
        const time = segment.dataset.time;
        const timestamp = segment.dataset.timestamp;
        const request = segment.dataset.request;
        const response = segment.dataset.response;
        const error = segment.dataset.error;
        const service = segment.dataset.service;
        const status = segment.classList.contains('success') ? 'success' : 'error';
        const statusText = status === 'success' ? 'Éxito' : 'Error';

        // Guardar datos actuales para la función de copiar
        this.currentSegmentData = {
            time,
            service,
            request,
            response,
            error,
            timestamp
        };

        // Actualizar contenido del modal
        document.getElementById('modal-service-name').textContent = service.charAt(0).toUpperCase() + service.slice(1);
        document.getElementById('modal-time').textContent = `${time}`;
        
        const statusBadge = document.getElementById('modal-status');
        statusBadge.textContent = statusText;
        statusBadge.className = `status-badge ${status}`;
        
        document.getElementById('modal-request').textContent = this.formatJson(request);
        document.getElementById('modal-response').textContent = this.formatJson(response);
        
        const errorSection = document.getElementById('modal-error');
        if (error && error.trim()) {
            errorSection.querySelector('.error-content').textContent = error;
            errorSection.style.display = 'block';
        } else {
            errorSection.style.display = 'none';
        }

        // Mostrar modal
        this.modal.classList.add('show');
        document.body.style.overflow = 'hidden'; // Prevenir scroll del body
    }

    closeModal() {
        this.modal.classList.remove('show');
        document.body.style.overflow = ''; // Restaurar scroll del body
        this.currentSegmentData = null;
    }

    formatJson(jsonString) {
        try {
            if (!jsonString) return '';
            const parsed = JSON.parse(jsonString);
            return JSON.stringify(parsed, null, 2);
        } catch (e) {
            return jsonString;
        }
    }

    formatTimestamp(timestamp) {
        try {
            const date = new Date(timestamp);
            return date.toLocaleTimeString('es-ES', {
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
        } catch (e) {
            return timestamp;
        }
    }

    async copyAllData() {
        if (!this.currentSegmentData) return;
        
        const { time, service, request, response, error } = this.currentSegmentData;
        
        // Formatear el contenido
        const formattedRequest = request ? this.formatJson(request) : 'No disponible';
        const formattedResponse = response ? this.formatJson(response) : 'No disponible';
        
        // Crear el texto en el formato solicitado
        let textToCopy = `Servicio: ${service}\nTiempo: ${time}\n\nRequest:\n${formattedRequest}\n\nResponse:\n${formattedResponse}`;
        
        // Agregar error si existe
        if (error && error.trim()) {
            textToCopy += `\n\nError:\n${error}`;
        }
        
        try {
            await navigator.clipboard.writeText(textToCopy);
            this.showCopyConfirmation();
        } catch (err) {
            // Fallback para navegadores que no soportan clipboard API
            this.fallbackCopyData(textToCopy);
        }
    }

    fallbackCopyData(text) {
        const textArea = document.createElement("textarea");
        textArea.value = text;
        
        // Hacer que el textarea sea invisible
        textArea.style.position = "fixed";
        textArea.style.left = "-999999px";
        textArea.style.top = "-999999px";
        document.body.appendChild(textArea);
        
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
            this.showCopyConfirmation();
        } catch (err) {
            console.error('Error al copiar datos:', err);
        }
        
        document.body.removeChild(textArea);
    }

    showCopyConfirmation() {
        const button = document.getElementById('copy-all-button');
        const originalText = button.innerHTML;
        
        // Cambiar el botón temporalmente
        button.innerHTML = '✅ ¡Copiado!';
        button.classList.add('copied');
        
        setTimeout(() => {
            button.innerHTML = originalText;
            button.classList.remove('copied');
        }, 2000);
    }
}

// Variable global para acceder a la instancia del monitor
let serviceMonitorInstance;

// Función global para cerrar el modal
function closeModal() {
    if (serviceMonitorInstance) {
        serviceMonitorInstance.closeModal();
    }
}

// Función global para copiar todos los datos
function copyAllData() {
    if (serviceMonitorInstance) {
        serviceMonitorInstance.copyAllData();
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    serviceMonitorInstance = new ServiceMonitor();
}); 