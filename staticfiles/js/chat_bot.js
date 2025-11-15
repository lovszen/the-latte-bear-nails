const CHATBOT_CONFIG = {
    GEMINI_API_KEY: 'AIzaSyDAjoPWdBQXbcPkPACQLAZncaYZVj_MO_MW',
    API_URL: 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent'
};

class TiendaChatbot {
    constructor() {
        this.isLoading = false;
        this.initializeChatbot();
    }

    initializeChatbot() {
        this.modal = document.getElementById('chatBotModal');
        this.messagesContainer = document.getElementById('chatBotMessages');
        this.userInput = document.getElementById('chatBotInput');
        this.sendButton = document.getElementById('sendBotMessage');
        this.closeButton = document.querySelector('.close-chatbot');
        this.openButton = document.getElementById('openChatBot');

        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });
        
        this.closeButton.addEventListener('click', () => this.closeModal());
        if (this.openButton) {
            this.openButton.addEventListener('click', () => this.openModal());
        }

        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) this.closeModal();
        });

        console.log('Chatbot inicializado');
    }

    openModal() {
        this.modal.style.display = 'block';
        this.userInput.focus();
    }

    closeModal() {
        this.modal.style.display = 'none';
    }

    async sendMessage() {
        const message = this.userInput.value.trim();
        
        if (!message || this.isLoading) return;

        this.addMessage('user', message);
        this.userInput.value = '';
        this.setLoadingState(true);

        try {
            const botResponse = await this.getAIResponse(message);
            this.addMessage('bot', botResponse);
        } catch (error) {
            console.error('Error del chatbot:', error);
            this.addMessage('bot', 'Lo siento, hubo un error. Por favor intenta nuevamente.');
        } finally {
            this.setLoadingState(false);
        }
    }

    async getAIResponse(userMessage) {
        if (!CHATBOT_CONFIG.GEMINI_API_KEY) {
            throw new Error('API Key no configurada');
        }

        const API_URL = `${CHATBOT_CONFIG.API_URL}?key=${CHATBOT_CONFIG.GEMINI_API_KEY}`;
        
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                contents: [{
                    parts: [{
                        text: `Eres un asistente especializado en productos de uñas para la tienda "The Latte Bear Nails". 
                        Tu expertise es en:
                        - Productos de uñas: esmaltes, tips, decoraciones, etc.
                        - Colores, formas (cuadrada, almendra, stiletto, etc.), tamaños
                        - Precios y promociones
                        - Recomendaciones de productos
                        
                        Responde en español de manera amable y útil. Sé conciso pero informativo.
                        Si no sabes algo sobre un producto, sugiere contactar al equipo.
                        
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
        return data.candidates[0].content.parts[0].text;
    }

    addMessage(sender, text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `${sender}-message`;
        
        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'message-bubble';
        bubbleDiv.textContent = text;
        
        messageDiv.appendChild(bubbleDiv);
        this.messagesContainer.appendChild(messageDiv);
        
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    setLoadingState(loading) {
        this.isLoading = loading;
        this.sendButton.disabled = loading;
        this.userInput.disabled = loading;
        
        if (loading) {
            this.userInput.placeholder = 'Escribiendo respuesta...';
            this.sendButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            
            // Mostrar mensaje de "escribiendo"
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
            
        } else {
            this.userInput.placeholder = 'Escribe tu consulta... Ej: "Uñas rosas forma almendra"';
            this.sendButton.innerHTML = '<i class="fas fa-paper-plane"></i>';
            
            const typingMsg = document.getElementById('typing-message');
            if (typingMsg) typingMsg.remove();
            
            this.userInput.focus();
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.tiendaChatbot = new TiendaChatbot();
});

function openChatbot() {
    if (window.tiendaChatbot) {
        window.tiendaChatbot.openModal();
    }
}