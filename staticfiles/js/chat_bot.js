class ProductChatBot {
    constructor() {
        this.products = [];
        this.currentFilters = {};
        this.loadProducts();
    }

    async loadProducts() {
        try {
            const response = await fetch('/api/productos/');
            if (response.ok) {
                this.products = await response.json();
            } else {
                // Datos de ejemplo si la API falla
                this.products = [
                    {id: 1, nombre: "Uñas Rosa Almendra", precio: "25.00", forma: "almendra", tamaño: "m", color_principal: "rosa", imagen: ""},
                    {id: 2, nombre: "French Clásico", precio: "30.00", forma: "cuadrada", tamaño: "s", color_principal: "blanco", imagen: ""},
                    {id: 3, nombre: "Stiletto Negro", precio: "35.00", forma: "stiletto", tamaño: "l", color_principal: "negro", imagen: ""},
                    {id: 4, nombre: "Uñas Rojo Ovaladas", precio: "22.00", forma: "ovalada", tamaño: "m", color_principal: "rojo", imagen: ""},
                    {id: 5, nombre: "Azul Premium", precio: "45.00", forma: "almendra", tamaño: "l", color_principal: "azul", imagen: ""},
                    {id: 6, nombre: "Rosa Pastel", precio: "28.00", forma: "cuadrada", tamaño: "s", color_principal: "rosa", imagen: ""}
                ];
            }
        } catch (error) {
            console.error('Error loading products:', error);
        }
    }

    processMessage(message) {
        const lowerMessage = message.toLowerCase().trim();
        
        if (this.isGreeting(lowerMessage)) {
            return this.getGreetingResponse();
        }
        
        if (this.isHelpRequest(lowerMessage)) {
            return this.getHelpResponse();
        }
        
        if (this.isProductRequest(lowerMessage) || this.isFilterRequest(lowerMessage)) {
            return this.handleProductRequest(lowerMessage);
        }
        
        if (this.isClearRequest(lowerMessage)) {
            return this.handleClearFilters();
        }
        
        return this.getDefaultResponse();
    }

    isGreeting(message) {
        const greetings = ['hola', 'holi', 'holis', 'buenos días', 'buenas', 'hi', 'hello', 'hey'];
        return greetings.some(greet => message.includes(greet));
    }

    isHelpRequest(message) {
        return message.includes('ayuda') || message.includes('help') || message.includes('qué puedes hacer');
    }

    isProductRequest(message) {
        const productKeywords = ['uñas', 'nail', 'esmalte', 'manicura', 'producto', 'ver', 'mostrar', 'buscar', 'encontrar', 'quiero', 'necesito'];
        return productKeywords.some(keyword => message.includes(keyword));
    }

    isFilterRequest(message) {
        const filterKeywords = ['color', 'forma', 'tamaño', 'precio', 'rosa', 'rojo', 'azul', 'almendra', 'cuadrada', 'larga', 'corta', 'barato', 'caro', 'económico'];
        return filterKeywords.some(keyword => message.includes(keyword));
    }

    isClearRequest(message) {
        return message.includes('limpiar') || message.includes('reset') || message.includes('empezar de nuevo');
    }

    getGreetingResponse() {
        return {
            type: 'text',
            content: `¡Hola! 👋 Soy tu asistente de The Latte Bear Nails.\n\nPuedo ayudarte a encontrar productos de uñas. Puedes pedirme:\n• "Ver todos los productos"\n• "Uñas rosas"\n• "Forma almendra"\n• "Precio económico"\n• "Limpiar filtros"\n\n¿Qué te gustaría ver? 💅`
        };
    }

    getHelpResponse() {
        return {
            type: 'text',
            content: `🔍 **Puedo buscar productos por:**\n\n🎨 COLORES: rosa, rojo, azul, negro, blanco, morado\n✂️ FORMAS: almendra, cuadrada, ovalada, stiletto\n📏 TAMAÑOS: corta, media, larga\n💰 PRECIOS: económico, medio, premium\n\n💡 **Ejemplos:**\n• "Mostrar uñas rosas"\n• "Forma almendra precio económico"\n• "Ver todos los productos"\n• "Limpiar filtros"`
        };
    }

    handleProductRequest(message) {
        this.extractFilters(message);
        const filteredProducts = this.filterProducts();
        
        if (filteredProducts.length === 0) {
            return {
                type: 'text',
                content: 'No encontré productos con esos criterios. 😔\n\n¿Quieres intentar con otros filtros? Puedo buscar por color, forma, tamaño o precio.'
            };
        }
        
        return {
            type: 'products',
            content: filteredProducts.slice(0, 4), // Mostrar máximo 4 productos
            filters: {...this.currentFilters}
        };
    }

    handleClearFilters() {
        this.currentFilters = {};
        return {
            type: 'text',
            content: '✅ Filtros limpiados. Ahora puedes hacer una nueva búsqueda.'
        };
    }

    extractFilters(message) {
        const colors = {'rosa': 'rosa', 'rojo': 'rojo', 'azul': 'azul', 'negro': 'negro', 'blanco': 'blanco', 'morado': 'morado'};
        const shapes = {'almendra': 'almendra', 'cuadrada': 'cuadrada', 'ovalada': 'ovalada', 'stiletto': 'stiletto'};
        const sizes = {'corta': 's', 'media': 'm', 'larga': 'l'};
        const prices = {'económico': 'low', 'barato': 'low', 'medio': 'medium', 'premium': 'high', 'caro': 'high'};
        
        for (const [key, value] of Object.entries(colors)) {
            if (message.includes(key)) this.currentFilters.color = value;
        }
        for (const [key, value] of Object.entries(shapes)) {
            if (message.includes(key)) this.currentFilters.forma = value;
        }
        for (const [key, value] of Object.entries(sizes)) {
            if (message.includes(key)) this.currentFilters.tamaño = value;
        }
        for (const [key, value] of Object.entries(prices)) {
            if (message.includes(key)) this.currentFilters.precio = value;
        }
    }

    filterProducts() {
        return this.products.filter(product => {
            if (this.currentFilters.color && !product.color_principal.toLowerCase().includes(this.currentFilters.color)) return false;
            if (this.currentFilters.forma && product.forma !== this.currentFilters.forma) return false;
            if (this.currentFilters.tamaño && product.tamaño !== this.currentFilters.tamaño) return false;
            if (this.currentFilters.precio) {
                const price = parseFloat(product.precio);
                if (this.currentFilters.precio === 'low' && price > 20) return false;
                if (this.currentFilters.precio === 'medium' && (price <= 20 || price > 50)) return false;
                if (this.currentFilters.precio === 'high' && price <= 50) return false;
            }
            return true;
        });
    }

    getDefaultResponse() {
        return {
            type: 'text',
            content: 'No entendí tu mensaje. 😅\n\n¿Quieres que te ayude a encontrar productos de uñas? Puedes pedirme por color, forma, tamaño o precio. O escribe "ayuda" para ver opciones.'
        };
    }
}

// INICIALIZAR CHATBOT
const productChatBot = new ProductChatBot();

// FUNCIONES DEL CHATBOT UI
function initChatBot() {
    const chatBotBtn = document.querySelector('.icono-chat-bot');
    const chatBotModal = document.getElementById('chatBotModal');
    const closeChatBot = document.querySelector('.close-chatbot');
    const sendBotBtn = document.getElementById('sendBotMessage');
    const botInput = document.getElementById('chatBotInput');
    const botMessages = document.getElementById('chatBotMessages');

    // Abrir chatbot
    chatBotBtn.addEventListener('click', () => {
        chatBotModal.classList.add('active');
        botInput.focus();
    });

    // Cerrar chatbot
    closeChatBot.addEventListener('click', () => {
        chatBotModal.classList.remove('active');
    });

    // Enviar mensaje
    function sendBotMessage() {
        const message = botInput.value.trim();
        if (!message) return;

        // Agregar mensaje del usuario
        addBotMessage(message, 'user');
        botInput.value = '';

        // Procesar con el bot
        setTimeout(() => {
            const response = productChatBot.processMessage(message);
            if (response.type === 'text') {
                addBotMessage(response.content, 'bot');
            } else if (response.type === 'products') {
                displayBotProducts(response.content, response.filters);
            }
        }, 500);
    }

    // Enviar con botón
    sendBotBtn.addEventListener('click', sendBotMessage);

    // Enviar con Enter
    botInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendBotMessage();
        }
    });

    function addBotMessage(content, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `${type}-message`;
        
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        
        if (typeof content === 'string') {
            // Reemplazar saltos de línea por <br>
            bubble.innerHTML = content.replace(/\n/g, '<br>');
        } else {
            bubble.appendChild(content);
        }
        
        messageDiv.appendChild(bubble);
        botMessages.appendChild(messageDiv);
        botMessages.scrollTop = botMessages.scrollHeight;
    }

    function displayBotProducts(products, filters) {
        const productsContainer = document.createElement('div');
        productsContainer.className = 'bot-products';
        
        if (filters && Object.keys(filters).length > 0) {
            const filtersDiv = document.createElement('div');
            filtersDiv.className = 'active-filters';
            filtersDiv.textContent = `Filtros: ${Object.values(filters).join(', ')}`;
            productsContainer.appendChild(filtersDiv);
        }
        
        const grid = document.createElement('div');
        grid.className = 'products-grid';
        
        products.forEach(product => {
            const productCard = document.createElement('div');
            productCard.className = 'product-card';
            productCard.innerHTML = `
                ${product.imagen ? `<img src="${product.imagen}" alt="${product.nombre}" class="product-image">` : '<div class="product-image" style="background: #f0f0f0; display: flex; align-items: center; justify-content: center; color: #999;">📷</div>'}
                <div class="product-info">
                    <h4 class="product-name">${product.nombre}</h4>
                    <p class="product-price">$${product.precio}</p>
                    <p class="product-details">${product.forma} • ${product.tamaño}</p>
                </div>
            `;
            
            productCard.addEventListener('click', () => {
                agregarAlCarritoDesdeBot(product);
            });
            
            grid.appendChild(productCard);
        });
        
        productsContainer.appendChild(grid);
        addBotMessage(productsContainer, 'bot');
    }
    
    function agregarAlCarritoDesdeBot(producto) {
        // Usar la función existente de carrito.js
        if (typeof agregarAlCarrito === 'function') {
            agregarAlCarrito(
                producto.id,
                producto.nombre,
                producto.precio,
                producto.imagen || ''
            );
            
            // Mostrar confirmación
            const confirmacion = document.createElement('div');
            confirmacion.className = 'bot-message';
            confirmacion.innerHTML = `
                <div class="message-bubble">
                    ✅ <strong>${producto.nombre}</strong> agregado al carrito!
                </div>
            `;
            botMessages.appendChild(confirmacion);
            botMessages.scrollTop = botMessages.scrollHeight;
        } else {
            console.error('Función agregarAlCarrito no encontrada');
        }
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', initChatBot);