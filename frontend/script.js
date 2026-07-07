document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');

    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const messageText = userInput.value.trim();
        if (messageText === '') return;

        // Agregar mensaje del usuario
        addMessage(messageText, 'user-message');
        
        // Limpiar input
        userInput.value = '';

        // Petición al backend FastAPI
        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: messageText })
        })
        .then(response => response.json())
        .then(data => {
            addMessage(data.reply, 'bot-message');
        })
        .catch(error => {
            addMessage("Hubo un error al comunicarse con el servidor.", 'bot-message');
            console.error("Error:", error);
        });
    });

    function addMessage(text, className) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${className}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        // El bot puede enviar HTML (negritas, saltos de línea).
        // Los mensajes del usuario se renderizan como texto plano por seguridad.
        if (className === 'bot-message') {
            contentDiv.innerHTML = text;
        } else {
            contentDiv.textContent = text;
        }
        
        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);
        
        // Scroll automático hacia abajo
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});
