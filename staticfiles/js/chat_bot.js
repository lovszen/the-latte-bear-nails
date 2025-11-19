class ChatbotInteligente {
    constructor() {
        this.productos = [];
        this.isLoading = false;
        this.init();
    }

    init() {
        setTimeout(() => {
            this.cargarProductos();
            this.setupChatbot();
        }, 500);
    }

    cargarProductos() {
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

    setupChatbot() {
        this.modal = document.getElementById('chatBotModal');
        this.messages = document.getElementById('chatBotMessages');
        this.input = document.getElementById('chatBotInput');
        this.sendBtn = document.getElementById('sendBotMessage');
        this.closeBtn = document.querySelector('.close-chatbot');
        
        if (!this.modal || !this.messages || !this.input || !this.sendBtn) return;

        this.messages.innerHTML = '';
        
        this.sendBtn.onclick = () => this.enviarMensaje();
        this.input.onkeypress = (e) => {
            if (e.key === 'Enter' && !this.isLoading) this.enviarMensaje();
        };
        
        if (this.closeBtn) {
            this.closeBtn.onclick = () => {
                this.modal.style.display = 'none';
                this.restaurarProductos();
            };
        }
    }

    async enviarMensaje() {
        const texto = this.input.value.trim();
        if (!texto || this.isLoading) return;

        this.agregarMensaje('user', texto);
        this.input.value = '';
        this.isLoading = true;
        this.sendBtn.disabled = true;
        this.sendBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

        const typingId = 'typing-' + Date.now();
        this.agregarMensaje('bot', 'Buscando...', typingId);

        try {
            const encontrados = this.buscarExacto(texto);
            
            const typingEl = document.getElementById(typingId);
            if (typingEl) typingEl.remove();

            let respuestaIA;
            try {
                respuestaIA = await this.llamarGemini(texto, encontrados);
            } catch (error) {
                respuestaIA = encontrados.length > 0 
                    ? `Encontré ${encontrados.length} ${encontrados.length === 1 ? 'producto' : 'productos'} para ti`
                    : `No encontré productos con esos criterios. Intenta buscar por color, forma o nombre.`;
            }

            this.agregarMensaje('bot', respuestaIA);

            if (encontrados.length > 0) {
                this.mostrarProductosEnChat(encontrados);
                this.filtrarPagina(encontrados);
            } else {
                this.mostrarSugerencias(texto);
            }

        } catch (error) {
            const typingEl = document.getElementById(typingId);
            if (typingEl) typingEl.remove();
            this.agregarMensaje('bot', 'Error al procesar la búsqueda. Intenta de nuevo.');
        } finally {
            this.isLoading = false;
            this.sendBtn.disabled = false;
            this.sendBtn.innerHTML = '<i class="fas fa-paper-plane"></i>';
        }
    }

    buscarExacto(query) {
        const q = query.toLowerCase();

        const coloresMencionados = [];
        const coloresComunes = ['rosa', 'negro', 'blanco', 'rojo', 'azul', 'verde', 'amarillo', 'morado', 'nude', 'beige', 'transparente'];
        coloresComunes.forEach(color => {
            if (q.includes(color)) coloresMencionados.push(color);
        });

        const formasMencionadas = [];
        const formasComunes = ['almendra', 'cuadrada', 'stiletto', 'ovalada', 'coffin', 'bailarina'];
        formasComunes.forEach(forma => {
            if (q.includes(forma)) formasMencionadas.push(forma);
        });

        const tamañosMencionados = [];
        const tamañosComunes = ['corto', 'corta', 'medio', 'media', 'largo', 'larga', 'xl', 'pequeño', 'pequeña'];
        tamañosComunes.forEach(tamaño => {
            if (q.includes(tamaño)) tamañosMencionados.push(tamaño);
        });

        const palabrasExcluir = ['set', 'uñas', 'con', 'para', 'de', 'la', 'el', 'y', 'a', 'en'];
        const palabrasQuery = q.split(' ')
            .filter(p => p.length > 2 && !palabrasExcluir.includes(p))
            .filter(p => !coloresComunes.includes(p) && !formasComunes.includes(p) && !tamañosComunes.includes(p));

        const tienesCriteriosEspecificos = coloresMencionados.length > 0 || 
                                            formasMencionadas.length > 0 || 
                                            tamañosMencionados.length > 0;

        const resultados = this.productos.filter(prod => {
            const textoProducto = `${prod.nombre} ${prod.color} ${prod.forma} ${prod.tamaño}`.toLowerCase();
            
            if (coloresMencionados.length > 0) {
                const tieneRosa = coloresMencionados.includes('rosa');
                const tieneNegro = coloresMencionados.includes('negro');
                
                if (tieneRosa && tieneNegro) {
                    const cumpleAmbos = textoProducto.includes('rosa') && textoProducto.includes('negro');
                    if (!cumpleAmbos) return false;
                } else {
                    const cumpleColor = coloresMencionados.every(color => textoProducto.includes(color));
                    if (!cumpleColor) return false;
                }
            }

            if (formasMencionadas.length > 0) {
                const cumpleForma = formasMencionadas.some(forma => textoProducto.includes(forma));
                if (!cumpleForma) return false;
            }

            if (tamañosMencionados.length > 0) {
                const cumpleTamaño = tamañosMencionados.some(tamaño => textoProducto.includes(tamaño));
                if (!cumpleTamaño) return false;
            }

            if (!tienesCriteriosEspecificos && palabrasQuery.length > 0) {
                return palabrasQuery.every(palabra => textoProducto.includes(palabra));
            }

            if (tienesCriteriosEspecificos) return true;

            return false;
        });

        return resultados;
    }

    mostrarSugerencias(queryOriginal) {
        const palabras = queryOriginal.toLowerCase().split(' ').filter(p => p.length > 2);
        const similares = this.productos.filter(prod => {
            const texto = `${prod.nombre} ${prod.color} ${prod.forma}`.toLowerCase();
            return palabras.some(p => texto.includes(p));
        }).slice(0, 3);

        if (similares.length > 0) {
            this.agregarMensaje('bot', 'No hay coincidencias exactas, pero estos podrían interesarte:');
            this.mostrarProductosEnChat(similares);
        }
    }

    async llamarGemini(query, productosEncontrados) {
        try {
            const response = await fetch('/api/gemini/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({
                    message: query,
                    productos_encontrados: productosEncontrados.length,
                    contexto: 'tienda_uñas'
                })
            });

            const data = await response.json();
            
            if (response.ok) {
                return data.response;
            } else {
                throw new Error(data.error || 'Error en el servidor');
            }
        } catch (error) {
            console.error('Error llamando a Gemini:', error);
            if (productosEncontrados.length > 0) {
                return `Encontré ${productosEncontrados.length} producto${productosEncontrados.length === 1 ? '' : 's'} para "${query}"`;
            } else {
                return `No encontré productos exactos para "${query}". Prueba con otros colores, formas o nombres.`;
            }
        }
    }

    getCsrfToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }

    mostrarProductosEnChat(productos) {
        const max = Math.min(productos.length, 4);
        const mostrar = productos.slice(0, max);

        let html = '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px;">';
        
        mostrar.forEach(p => {
            html += `
                <div onclick="mostrarDetalleProducto('${p.id}'); document.getElementById('chatBotModal').style.display='none';" 
                     style="background: white; border-radius: 10px; padding: 10px; cursor: pointer; border: 2px solid #ffe4f4; transition: all 0.3s; position: relative;">
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

        const div = document.createElement('div');
        div.className = 'bot-message';
        div.innerHTML = `<div class="message-bubble" style="background: transparent !important; box-shadow: none !important; max-width: 95% !important; padding: 10px 5px !important;">${html}</div>`;
        this.messages.appendChild(div);
        this.scrollChat();
    }

    filtrarPagina(productos) {
        document.querySelectorAll('.producto-card').forEach(card => {
            card.style.opacity = '0.3';
            card.style.filter = 'grayscale(80%)';
            card.style.transition = 'all 0.5s ease';
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
        const btn = document.getElementById('btn-reset-filtro');
        if (btn) btn.remove();
    }

    agregarBotonQuitarFiltro() {
        let btn = document.getElementById('btn-reset-filtro');
        if (btn) btn.remove();

        btn = document.createElement('button');
        btn.id = 'btn-reset-filtro';
        btn.innerHTML = 'Mostrar todos';
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
        const div = document.createElement('div');
        div.className = `${tipo}-message`;
        if (id) div.id = id;
        
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        bubble.innerHTML = texto.replace(/\n/g, '<br>');
        
        div.appendChild(bubble);
        this.messages.appendChild(div);
        this.scrollChat();
    }

    scrollChat() {
        setTimeout(() => {
            this.messages.scrollTop = this.messages.scrollHeight;
        }, 100);
    }
}

window.chatbotInteligente = new ChatbotInteligente();

window.openChatbot = function() {
    const modal = document.getElementById('chatBotModal');
    if (modal) {
        modal.style.display = 'block';
        document.getElementById('chatBotInput')?.focus();
    }
};