document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');
    
    // Login Modal Elements
    const loginModal = document.getElementById('login-modal');
    const appLayout = document.getElementById('app-layout');
    const loginForm = document.getElementById('login-form');
    const loginError = document.getElementById('login-error');
    const loginBtn = document.getElementById('login-btn');

    // Check auth
    let authToken = localStorage.getItem('auth_token');
    let authUsername = localStorage.getItem('auth_username');
    if (authToken) {
        document.getElementById('current-username').textContent = authUsername || 'Usuario';
        loginModal.style.display = 'none';
        appLayout.style.display = 'flex';
    } else {
        loginModal.style.display = 'flex';
        appLayout.style.display = 'none';
    }

    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        loginError.style.display = 'none';
        
        const originalBtnText = loginBtn.innerHTML;
        loginBtn.innerHTML = '<span>Verificando...</span>';
        loginBtn.disabled = true;

        fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Credenciales incorrectas');
            }
            return response.json();
        })
        .then(data => {
            authToken = data.access_token;
            authUsername = data.user.username;
            localStorage.setItem('auth_token', authToken);
            localStorage.setItem('auth_username', authUsername);
            document.getElementById('current-username').textContent = authUsername;
            loginModal.style.display = 'none';
            appLayout.style.display = 'flex';
        })
        .catch(error => {
            loginError.textContent = error.message;
            loginError.style.display = 'block';
        })
        .finally(() => {
            loginBtn.innerHTML = originalBtnText;
            loginBtn.disabled = false;
        });
    });

    // Profile Dropdown Logic
    const profileBtn = document.getElementById('user-profile-btn');
    const userDropdown = document.getElementById('user-dropdown');
    const logoutBtn = document.getElementById('logout-btn');

    profileBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        userDropdown.classList.toggle('show');
    });

    document.addEventListener('click', (e) => {
        if (!profileBtn.contains(e.target)) {
            userDropdown.classList.remove('show');
        }
    });

    logoutBtn.addEventListener('click', () => {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('auth_username');
        authToken = null;
        authUsername = null;
        appLayout.style.display = 'none';
        loginModal.style.display = 'flex';
    });

    // Theme toggle
    const themeToggleBtn = document.getElementById('theme-toggle');
    const iconSun = document.querySelector('.icon-sun');
    const iconMoon = document.querySelector('.icon-moon');
    const htmlElement = document.documentElement;
    
    // Check saved theme or system preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        htmlElement.setAttribute('data-theme', savedTheme);
        updateThemeIcons(savedTheme);
    }
    
    themeToggleBtn.addEventListener('click', () => {
        const currentTheme = htmlElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        
        htmlElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeIcons(newTheme);
    });
    
    function updateThemeIcons(theme) {
        if (theme === 'dark') {
            iconSun.style.display = 'none';
            iconMoon.style.display = 'block';
        } else {
            iconSun.style.display = 'block';
            iconMoon.style.display = 'none';
        }
    }

    // New Chat functionality
    const newChatBtn = document.getElementById('new-chat-btn');
    const tabsList = document.getElementById('chat-tabs-list');
    let consultationCount = 1;

    newChatBtn.addEventListener('click', () => {
        // Clear messages
        chatMessages.innerHTML = '';
        
        // Add greeting
        addMessage("¡Hola! 👋 Soy <b>Bot204</b>, tu asistente de información comercial. ¿En qué te puedo ayudar hoy?", 'bot-message');
        
        // Add new tab in sidebar
        consultationCount++;
        
        // Remove active class from all
        document.querySelectorAll('.sidebar-item').forEach(item => {
            item.classList.remove('active');
            item.querySelector('.status-dot').className = 'status-dot offline';
        });
        
        const newTab = document.createElement('div');
        newTab.className = 'sidebar-item active';
        newTab.innerHTML = `<span class="status-dot online"></span> Consulta ${consultationCount}`;
        
        // Add click event to tab (just visual for now, as we don't save history)
        newTab.addEventListener('click', function() {
            document.querySelectorAll('.sidebar-item').forEach(item => {
                item.classList.remove('active');
                item.querySelector('.status-dot').className = 'status-dot offline';
            });
            this.classList.add('active');
            this.querySelector('.status-dot').className = 'status-dot online';
        });

        // Insert after the first one or at top
        tabsList.insertBefore(newTab, tabsList.firstChild);
    });

    // Chat functionality
    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const messageText = userInput.value.trim();
        if (messageText === '') return;

        // Agregar mensaje del usuario
        addMessage(messageText, 'user-message');
        
        // Limpiar input
        userInput.value = '';

        // Mostrar indicador de escribiendo...
        const typingIndicator = showTypingIndicator();

        // Petición al backend FastAPI
        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ message: messageText })
        })
        .then(response => {
            if (response.status === 401) {
                localStorage.removeItem('auth_token');
                localStorage.removeItem('auth_username');
                authToken = null;
                appLayout.style.display = 'none';
                loginModal.style.display = 'flex';
                throw new Error("Sesión expirada");
            }
            return response.json();
        })
        .then(data => {
            typingIndicator.remove();
            setTimeout(() => {
                addMessage(data.reply, 'bot-message');
            }, 300);
        })
        .catch(error => {
            typingIndicator.remove();
            if (error.message !== "Sesión expirada") {
                addMessage("Hubo un error al comunicarse con el servidor.", 'bot-message');
            }
            console.error("Error:", error);
        });
    });

    function addMessage(text, className) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${className}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        if (className === 'bot-message') {
            contentDiv.innerHTML = text;
        } else {
            contentDiv.textContent = text;
        }
        
        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);
        scrollToBottom();
    }

    function showTypingIndicator() {
        const indicatorDiv = document.createElement('div');
        indicatorDiv.className = 'typing-indicator bot-message';
        
        for(let i=0; i<3; i++) {
            const dot = document.createElement('div');
            dot.className = 'typing-dot';
            indicatorDiv.appendChild(dot);
        }

        chatMessages.appendChild(indicatorDiv);
        scrollToBottom();
        return indicatorDiv;
    }

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});
