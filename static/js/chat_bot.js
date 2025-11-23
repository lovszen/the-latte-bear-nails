class ChatbotInteligente {
    constructor() {
        this.productos = [];
        this.isLoading = false;
        this.initialized = false;
    }

    async cargarProductos() {
        const cards = document.querySelectorAll('.producto-card');
        this.productos = [];
        
        cards.forEach((card, idx) => {
            const prod = {
                elemento: card,
                id: card.querySelector('.btn-agregar-carrito')?.dataset.productoId || idx,
                nombre: card.querySelector('.producto-nombre')?.textContent.trim() || '',
                precio: card.querySelector('.precio-final')?.textContent.trim() || '',
                imagen: card.querySelector('.producto-imagen')?.src || '',
                forma: '',
                tamaño: '',
                color: ''
            };

            card.querySelectorAll('.detalle-item').forEach(det => {
                const label = det.querySelector('.detalle-label')?.textContent.toLowerCase() || '';
                const valor = det.querySelector('.detalle-valor')?.textContent.trim() || '';
                
                if (label.includes('forma')) prod.forma = valor.toLowerCase();
                if (label.includes('tamaño')) prod.tamaño = valor.toLowerCase();
                if (label.includes('color')) prod.color = valor.toLowerCase();
            });

            if (prod.nombre) this.productos.push(prod);
        });
    }

    async init() {
        if (this.initialized) return;
        await this.cargarProductos();
        this.setupEventListeners();
        this.initialized = true;
    }

    setupEventListeners() {
        const closeBtn = document.querySelector('.close-chatbot');
        if (closeBtn) closeBtn.onclick = () => this.close();

        const sendBtn = document.getElementById('sendBotMessage');
        if (sendBtn) sendBtn.onclick = () => this.enviarMensaje();

        const input = document.getElementById('chatBotInput');
        if (input) {
            input.onkeypress = (e) => {
                if (e.key === 'Enter' && !this.isLoading) {
                    this.enviarMensaje();
                }
            };
        }
    }

    async open() {
        const modal = document.getElementById('chatBotModal');
        if (modal) {
            if (!this.initialized) await this.init();
            modal.style.display = 'flex';
            modal.classList.add('active');
            this.mostrarMensajeBienvenida();
            document.getElementById('chatBotInput')?.focus();
        }
    }

    close() {
        const modal = document.getElementById('chatBotModal');
        if (modal) {
            modal.style.display = 'none';
            modal.classList.remove('active');
            this.restaurarProductos();
        }
    }

    mostrarMensajeBienvenida() {
        const messages = document.getElementById('chatBotMessages');
        if (!messages || messages.children.length > 0) return;
        
        const mensaje = `Hola! Soy tu asistente de The Latte Bear Nails.\n\nEncontré ${this.productos.length} productos disponibles.\n\nPuedo ayudarte a buscar por:\n• Color (rosa, negro, blanco, etc.)\n• Forma (almendra, stiletto, coffin, etc.)\n• Tamaño (corto, medio, largo)\n\nEjemplos: "rosa y negro", "almendra", "set floral"\n\n¿Qué te gustaría ver?`;
        this.agregarMensaje('bot', mensaje);
    }

    async enviarMensaje() {
        const input = document.getElementById('chatBotInput');
        const sendBtn = document.getElementById('sendBotMessage');
        const texto = input?.value.trim();
        
        if (!texto || this.isLoading) return;

        this.agregarMensaje('user', texto);
        input.value = '';
        this.isLoading = true;
        
        if (sendBtn) {
            sendBtn.disabled = true;
            sendBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        }

        const typingId = 'typing-' + Date.now();
        this.agregarMensaje('bot', 'Buscando productos...', typingId);

        try {
            document.getElementById(typingId)?.remove();

            let respuestaIA;
            try {
                respuestaIA = await this.llamarGemini(texto, 0);
            } catch {
                respuestaIA = 'No encontré productos. Intenta con otras palabras.';
            }

            this.agregarMensaje('bot', respuestaIA);

        } catch {
            document.getElementById(typingId)?.remove();
            this.agregarMensaje('bot', 'Error al procesar la búsqueda. Intenta de nuevo.');
        } finally {
            this.isLoading = false;
            if (sendBtn) {
                sendBtn.disabled = false;
                sendBtn.innerHTML = '<i class="fas fa-paper-plane"></i>';
            }
        }
    }

    async llamarGemini(query, productosEncontrados) {
        try {
            const productosInfo = this.productos.map(p => 
                `Producto: ${p.nombre} | Colores: ${p.color} | Forma: ${p.forma} | Tamaño: ${p.tamaño}`
            ).join('\n');

            const promptAnalisis = `Eres un asistente de The Latte Bear Nails. Analiza esta consulta y encuentra productos que coincidan.

CONSULTA: "${query}"

PRODUCTOS DISPONIBLES:
${productosInfo}

INSTRUCCIONES:
- Busca coincidencias FLEXIBLES con sinónimos
- "floral" → "flores", "rosas", "floreado"  
- "almendra" → "almendrada", "ovalada"
- "elegante" → "nude", "clásico", "french"
- "largo" → "largas", "extendidas"
- IGNORA mayúsculas/minúsculas y errores ortográficos

Responde con este formato:
PRODUCTOS_COINCIDENTES: [nombres de productos separados por coma]
RESPUESTA: [respuesta amigable mencionando los productos encontrados]`;

            const response = await fetch('/api/gemini/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({
                    message: promptAnalisis,
                    productos_encontrados: 0,
                    contexto: 'analisis_busqueda'
                })
            });

            if (!response.ok) throw new Error('Error en el servidor');
            
            const data = await response.json();
            const respuestaCompleta = data.response;
            const lineas = respuestaCompleta.split('\n');
            const productosCoincidentes = [];

            for (const linea of lineas) {
                if (linea.startsWith('PRODUCTOS_COINCIDENTES:')) {
                    const productosStr = linea.replace('PRODUCTOS_COINCIDENTES:', '').trim();
                    const nombres = productosStr.split(',').map(n => n.trim()).filter(n => n);
                    
                    nombres.forEach(nombreProducto => {
                        const encontrado = this.productos.find(p => 
                            p.nombre.toLowerCase().includes(nombreProducto.toLowerCase())
                        );
                        if (encontrado) productosCoincidentes.push(encontrado);
                    });
                    break;
                }
            }

            if (productosCoincidentes.length > 0) {
                setTimeout(() => {
                    this.mostrarProductosEnChat(productosCoincidentes);
                    this.filtrarPagina(productosCoincidentes);
                }, 100);
            }

            const respuestaLinea = lineas.find(linea => linea.startsWith('RESPUESTA:'));
            return respuestaLinea ? respuestaLinea.replace('RESPUESTA:', '').trim() : respuestaCompleta;

        } catch {
            return 'No pude buscar productos en este momento. Intenta con otras palabras.';
        }
    }

    getCsrfToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        if (token) return token.value;
        
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') return value;
        }
        return '';
    }

    mostrarProductosEnChat(productos) {
        const max = Math.min(productos.length, 4);
        const mostrar = productos.slice(0, max);

        let html = '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px;">';
        
        mostrar.forEach(p => {
            html += `
                <div onclick="mostrarDetalleProducto('${p.id}'); document.getElementById('chatBotModal').style.display='none';" 
                     style="background: white; border-radius: 10px; padding: 10px; cursor: pointer; border: 2px solid #ffe4f4; position: relative;">
                    <img src="${p.imagen}" 
                         onerror="this.style.display='none'" 
                         style="width: 100%; height: 70px; object-fit: cover; border-radius: 8px; margin-bottom: 8px;">
                    <div style="font-size: 0.8em; font-weight: bold; text-align: center; margin-bottom: 5px; min-height: 32px; color: #333; line-height: 1.2;">${p.nombre}</div>
                    <div style="text-align: center; margin: 5px 0;">
                        <span style="font-size: 0.7em; background: #f0f0f0; padding: 2px 6px; border-radius: 10px; margin: 2px; display: inline-block;">${p.color}</span>
                        ${p.forma ? `<span style="font-size: 0.7em; background: #f0f0f0; padding: 2px 6px; border-radius: 10px; margin: 2px; display: inline-block;">${p.forma}</span>` : ''}
                    </div>
                    <div style="text-align: center; color: #ff6b9c; font-weight: bold; font-size: 1.1em; margin-top: 8px;">${p.precio}</div>
                    <div style="position: absolute; top: 5px; right: 5px; background: rgba(255,255,255,0.9); border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; font-size: 0.8em;">👁️</div>
                </div>
            `;
        });

        html += '</div>';

        if (productos.length > max) {
            html += `<p style="text-align: center; margin-top: 10px; font-size: 0.9em; color: #666;">+ ${productos.length - max} más en la tienda</p>`;
        }

        const messages = document.getElementById('chatBotMessages');
        if (!messages) return;

        const div = document.createElement('div');
        div.className = 'bot-message';
        div.innerHTML = `<div class="message-bubble" style="background: transparent; box-shadow: none; max-width: 95%; padding: 10px 5px;">${html}</div>`;
        messages.appendChild(div);
        this.scrollChat();
    }

    filtrarPagina(productos) {
        document.querySelectorAll('.producto-card').forEach(card => {
            card.style.opacity = '0.3';
            card.style.filter = 'grayscale(80%)';
        });

        productos.forEach(p => {
            if (p.elemento) {
                p.elemento.style.opacity = '1';
                p.elemento.style.filter = 'grayscale(0%)';
                p.elemento.style.border = '3px solid #ff6b9c';
                p.elemento.style.boxShadow = '0 0 25px rgba(255, 107, 156, 0.7)';
                p.elemento.style.transform = 'scale(1.02)';
            }
        });

        this.agregarBotonQuitarFiltro();
    }

    restaurarProductos() {
        document.querySelectorAll('.producto-card').forEach(card => {
            card.style.opacity = '1';
            card.style.filter = 'grayscale(0%)';
            card.style.border = '';
            card.style.boxShadow = '';
            card.style.transform = '';
        });
        document.getElementById('btn-reset-filtro')?.remove();
    }

    agregarBotonQuitarFiltro() {
        document.getElementById('btn-reset-filtro')?.remove();

        const btn = document.createElement('button');
        btn.id = 'btn-reset-filtro';
        btn.innerHTML = '✕ Mostrar todos';
        btn.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            z-index: 999;
            background: linear-gradient(135deg, #ff6b9c, #ff8eb4);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            font-weight: bold;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(255,107,156,0.5);
            transition: all 0.3s;
        `;

        btn.onclick = () => this.restaurarProductos();
        btn.onmouseenter = () => btn.style.transform = 'scale(1.05)';
        btn.onmouseleave = () => btn.style.transform = 'scale(1)';

        document.body.appendChild(btn);
    }

    agregarMensaje(tipo, texto, id = null) {
        const messages = document.getElementById('chatBotMessages');
        if (!messages) return;
        
        const div = document.createElement('div');
        div.className = `${tipo}-message`;
        if (id) div.id = id;
        
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        bubble.innerHTML = texto.replace(/\n/g, '<br>');
        
        div.appendChild(bubble);
        messages.appendChild(div);
        this.scrollChat();
    }

    scrollChat() {
        const messages = document.getElementById('chatBotMessages');
        if (messages) setTimeout(() => messages.scrollTop = messages.scrollHeight, 100);
    }
}

window.chatbotInteligente = new ChatbotInteligente();
window.openChatbot = () => window.chatbotInteligente?.open();
window.closeChatbot = () => window.chatbotInteligente?.close();

document.addEventListener('DOMContentLoaded', () => {
    const chatbotModal = document.getElementById('chatBotModal');
    if (chatbotModal && chatbotModal.parentNode !== document.body) {
        document.body.appendChild(chatbotModal);
    }
});