// chat_bot.js - Versión corregida
console.log('🔧 chat_bot.js cargado - Versión corregida');

// Esperar a que la página cargue completamente
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 DOM completamente cargado - Inicializando chatbot...');
    
    // Configuración
    const CHATBOT_CONFIG = {
        GEMINI_API_KEY: 'AIzaSyDAjoPWdBQXbcPkPACQLAZncaYZVj_MO_MW',
        API_URL: 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent'
    };

    class TiendaChatbot {
        constructor() {
            this.isLoading = false;
            // Pequeño delay para asegurar que el DOM esté listo
            setTimeout(() => {
                this.initializeChatbot();
            }, 100);
        }

        initializeChatbot() {
            console.log('🔄 Buscando elementos del chatbot...');
            
            this.modal = document.getElementById('chatBotModal');
            this.messagesContainer = document.getElementById('chatBotMessages');
            this.userInput = document.getElementById('chatBotInput');
            this.sendButton = document.getElementById('sendBotMessage');
            this.closeButton = document.querySelector('.close-chatbot');

            console.log('Elementos encontrados:', {
                modal: !!this.modal,
                messagesContainer: !!this.messagesContainer,
                userInput: !!this.userInput,
                sendButton: !!this.sendButton,
                closeButton: !!this.closeButton
            });

            if (!this.modal || !this.messagesContainer || !this.userInput || !this.sendButton) {
                console.error('❌ No se encontraron todos los elementos del chatbot');
                return;
            }

            // Event listeners
            this.sendButton.addEventListener('click', () => this.sendMessage());
            this.userInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !this.isLoading) {
                    this.sendMessage();
                }
            });
            
            if (this.closeButton) {
                this.closeButton.addEventListener('click', () => this.closeModal());
            }

            // Cerrar modal al hacer click fuera
            this.modal.addEventListener('click', (e) => {
                if (e.target === this.modal) this.closeModal();
            });

            console.log('✅ Chatbot inicializado correctamente');
        }

        openModal() {
            console.log('📱 Abriendo modal del chatbot');
            if (this.modal) {
                this.modal.style.display = 'block';
                if (this.userInput) {
                    this.userInput.focus();
                }
            }
        }

        closeModal() {
            if (this.modal) {
                this.modal.style.display = 'none';
            }
        }

        async sendMessage() {
            if (!this.userInput) return;
            
            const message = this.userInput.value.trim();
            
            if (!message || this.isLoading) {
                return;
            }

            console.log('📤 Enviando mensaje:', message);

            // Mostrar mensaje del usuario
            this.addMessage('user', message);
            this.userInput.value = '';
            this.setLoadingState(true);

            try {
                const botResponse = await this.getAIResponse(message);
                this.addMessage('bot', botResponse);
                console.log('✅ Respuesta recibida');
            } catch (error) {
                console.error('❌ Error del chatbot:', error);
                this.addMessage('bot', '😔 Lo siento, hubo un error. Por favor intenta nuevamente.');
            } finally {
                this.setLoadingState(false);
            }
        }

        async getAIResponse(userMessage) {
            if (!CHATBOT_CONFIG.GEMINI_API_KEY) {
                throw new Error('API Key no configurada');
            }

            const API_URL = `${CHATBOT_CONFIG.API_URL}?key=${CHATBOT_CONFIG.GEMINI_API_KEY}`;
            
            console.log('🌐 Llamando a la API de Gemini...');
            
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    contents: [{
                        parts: [{
                            text: `Eres un asistente especializado en productos de uñas para "The Latte Bear Nails". 
                            Responde en español de manera amable y útil sobre:
                            - Productos de uñas, esmaltes, tips, decoraciones
                            - Colores, formas (cuadrada, almendra, stiletto)
                            - Tamaños y precios
                            - Recomendaciones
                            
                            Usuario: ${userMessage}
                            Asistente:`
                        }]
                    }],
                    generationConfig: {
                        temperature: 0.7,
                        maxOutputTokens: 300,
                    }
                })
            });

            if (!response.ok) {
                throw new Error(`Error API: ${response.status}`);
            }

            const data = await response.json();
            
            if (!data.candidates || !data.candidates[0] || !data.candidates[0].content.parts[0].text) {
                throw new Error('Respuesta inesperada de la API');
            }
            
            return data.candidates[0].content.parts[0].text;
        }

        addMessage(sender, text) {
            if (!this.messagesContainer) return;
            
            const messageDiv = document.createElement('div');
            messageDiv.className = `${sender}-message`;
            
            const bubbleDiv = document.createElement('div');
            bubbleDiv.className = 'message-bubble';
            bubbleDiv.textContent = text;
            
            messageDiv.appendChild(bubbleDiv);
            this.messagesContainer.appendChild(messageDiv);
            
            // Scroll al final
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }

        setLoadingState(loading) {
            this.isLoading = loading;
            
            if (this.sendButton) this.sendButton.disabled = loading;
            if (this.userInput) this.userInput.disabled = loading;
            
            if (loading) {
                if (this.userInput) this.userInput.placeholder = 'Escribiendo respuesta...';
                if (this.sendButton) this.sendButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
                
                // Mostrar mensaje de "escribiendo"
                if (this.messagesContainer) {
                    const typingDiv = document.createElement('div');
                    typingDiv.className = 'bot-message typing';
                    typingDiv.innerHTML = `
                        <div class="message-bubble">
                            Escribiendo<span class="typing-dots">...</span>
                        </div>
                    `;
                    typingDiv.id = 'typing-message';
                    this.messagesContainer.appendChild(typingDiv);
                    this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
                }
                
            } else {
                if (this.userInput) {
                    this.userInput.placeholder = 'Escribe tu consulta...';
                    this.userInput.focus();
                }
                if (this.sendButton) this.sendButton.innerHTML = '<i class="fas fa-paper-plane"></i>';
                
                // Remover mensaje de "escribiendo"
                const typingMsg = document.getElementById('typing-message');
                if (typingMsg) typingMsg.remove();
            }
        }
    }

    // Inicializar chatbot
    window.tiendaChatbot = new TiendaChatbot();
    
    // Función global para abrir el chatbot
    window.openChatbot = function() {
        console.log('🎯 openChatbot() llamado');
        if (window.tiendaChatbot) {
            window.tiendaChatbot.openModal();
        } else {
            console.error('❌ Chatbot no disponible');
        }
    };

    console.log('🎉 Chatbot listo para usar');
});

// Debug adicional
console.log('📜 Script chat_bot.js parseado correctamente');