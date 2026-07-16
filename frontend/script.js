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

    // Confirm Modal Elements
    const confirmModal = document.getElementById('confirm-modal');
    const confirmCancelBtn = document.getElementById('confirm-cancel-btn');
    const confirmOkBtn = document.getElementById('confirm-ok-btn');
    let sessionToDelete = null;

    function showConfirmModal(sessionId) {
        sessionToDelete = sessionId;
        confirmModal.classList.add('show');
    }

    function hideConfirmModal() {
        sessionToDelete = null;
        confirmModal.classList.remove('show');
    }

    confirmCancelBtn.addEventListener('click', hideConfirmModal);
    
    confirmOkBtn.addEventListener('click', () => {
        if (!sessionToDelete) return;
        const sessionId = sessionToDelete;
        hideConfirmModal();
        
        fetch(`/api/chat/sessions/${sessionId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${authToken}` }
        }).then(response => {
            if (response.ok) {
                if (currentSessionId === sessionId) {
                    currentSessionId = null;
                    chatMessages.innerHTML = '';
                    addMessage(`¡Hola, ${authUsername || 'Usuario'}! 👋 Soy <b>Bot204</b>, tu asistente de información comercial. ¿En qué te puedo ayudar hoy?`, 'bot-message');
                }
                loadSessions();
            }
        });
    });

    // Check auth
    let currentSessionId = null;
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
            loadSessions();
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

    function loadSessions() {
        if (!authToken) return;
        fetch('/api/chat/sessions', {
            headers: { 'Authorization': `Bearer ${authToken}` }
        })
        .then(response => {
            if (!response.ok) {
                if (response.status === 401) {
                    localStorage.removeItem('auth_token');
                    localStorage.removeItem('auth_username');
                    window.location.reload();
                }
                throw new Error("Failed to load sessions");
            }
            return response.json();
        })
        .then(sessions => {
            tabsList.innerHTML = '';
            if (sessions.length > 0 && !currentSessionId) {
                currentSessionId = sessions[0].id;
            }
            sessions.forEach(session => {
                const tab = document.createElement('div');
                const isActive = session.id === currentSessionId;
                tab.className = `sidebar-item ${isActive ? 'active' : ''}`;
                tab.innerHTML = `
                    <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
                        <span style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;"><span class="status-dot ${isActive ? 'online' : 'offline'}"></span> ${session.title}</span>
                        <button class="delete-session-btn" style="background: none; border: none; cursor: pointer; color: #d6a77a; margin-left: 5px; display: flex; align-items: center;" title="Eliminar consulta">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                        </button>
                    </div>
                `;
                tab.addEventListener('click', (e) => {
                    if (e.target.closest('.delete-session-btn')) {
                        e.stopPropagation();
                        showConfirmModal(session.id);
                        return;
                    }
                    loadSessionMessages(session.id, tab);
                });
                tabsList.appendChild(tab);
            });
            
            if (currentSessionId && document.querySelectorAll('.sidebar-item').length > 0) {
                // To avoid reloading if we just switched
                if (chatMessages.innerHTML.trim() === '' || chatMessages.children.length <= 1) {
                    loadSessionMessages(currentSessionId, null);
                }
            }
        })
        .catch(console.error);
    }

    function loadSessionMessages(sessionId, tabElement) {
        currentSessionId = sessionId;
        if (tabElement) {
            document.querySelectorAll('.sidebar-item').forEach(item => {
                item.classList.remove('active');
                item.querySelector('.status-dot').className = 'status-dot offline';
            });
            tabElement.classList.add('active');
            tabElement.querySelector('.status-dot').className = 'status-dot online';
        } else {
            // Find tab visually
            const tabs = document.querySelectorAll('.sidebar-item');
            tabs.forEach(item => {
                if(item.textContent.includes(sessionId)) { // Not perfectly accurate but handles visual state partially
                    // Actually we don't have session id in DOM text, just skip finding tab if null
                }
            });
        }
        
        chatMessages.innerHTML = '';
        fetch(`/api/chat/sessions/${sessionId}`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        })
        .then(response => {
            if (!response.ok) {
                if (response.status === 401) {
                    localStorage.removeItem('auth_token');
                    localStorage.removeItem('auth_username');
                    window.location.reload();
                }
                throw new Error("Failed to load session messages");
            }
            return response.json();
        })
        .then(messages => {
            if (!messages || messages.length === 0) {
                // Si por alguna razón la sesión está vacía, mostrar mensaje por defecto
                addMessage("Esta consulta no tiene mensajes.", 'bot-message');
                return;
            }
            messages.forEach(msg => {
                addMessage(msg.content || "", msg.role === 'bot' ? 'bot-message' : 'user-message');
            });
        })
        .catch(err => {
            console.error("Error loading messages:", err);
            chatMessages.innerHTML = ''; // Ensure it's clear
            addMessage("Hubo un error al cargar la consulta. Por favor, recarga la página.", 'bot-message');
        });
    }

    // Call loadSessions on init if logged in
    if (authToken) {
        loadSessions();
    }

    newChatBtn.addEventListener('click', () => {
        if (currentSessionId === null && tabsList.children.length > 0) {
            // Ya estamos en una nueva consulta y hay una tab en la UI, no hacer nada
            return;
        }
        
        currentSessionId = null;
        chatMessages.innerHTML = '';
        addMessage(`¡Hola, ${authUsername || 'Usuario'}! 👋 Soy <b>Bot204</b>, tu asistente de información comercial. ¿En qué te puedo ayudar hoy?`, 'bot-message');
        
        document.querySelectorAll('.sidebar-item').forEach(item => {
            item.classList.remove('active');
            item.querySelector('.status-dot').className = 'status-dot offline';
        });
        
        const newTab = document.createElement('div');
        newTab.className = 'sidebar-item active';
        newTab.innerHTML = `<span class="status-dot online"></span> Nueva Consulta`;
        
        newTab.addEventListener('click', () => {
            if (currentSessionId !== null) {
                currentSessionId = null;
                chatMessages.innerHTML = '';
                addMessage(`¡Hola, ${authUsername || 'Usuario'}! 👋 Soy <b>Bot204</b>, tu asistente de información comercial. ¿En qué te puedo ayudar hoy?`, 'bot-message');
                document.querySelectorAll('.sidebar-item').forEach(item => {
                    item.classList.remove('active');
                    item.querySelector('.status-dot').className = 'status-dot offline';
                });
                newTab.classList.add('active');
                newTab.querySelector('.status-dot').className = 'status-dot online';
            }
        });
        
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
            body: JSON.stringify({ message: messageText, session_id: currentSessionId })
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
            if (!response.ok) {
                throw new Error("Error del servidor: " + response.status);
            }
            return response.json();
        })
        .then(data => {
            typingIndicator.remove();
            
            let wasNewSession = !currentSessionId;
            currentSessionId = data.session_id;
            
            if (wasNewSession) {
                loadSessions();
            }
            
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
