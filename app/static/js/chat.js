document.addEventListener('DOMContentLoaded', function() {
    const sendBtn = document.getElementById('send-btn');
    const userInput = document.getElementById('user-input');
    const chatWindow = document.getElementById('chat-window');
    const starterPrompts = document.querySelector('.starter-prompts');
    const crisisModal = new bootstrap.Modal(document.getElementById('crisisModal'));
    const helplineSpan = document.getElementById('helpline-number');

    async function sendMessage(messageText) {
        const message = messageText || userInput.value.trim();
        if (message === '') return;

        appendMessage(message, 'user');
        userInput.value = '';
        starterPrompts.style.display = 'none';
        appendTypingIndicator();

        try {
            const response = await fetch("/api/ask", {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            removeTypingIndicator();
            appendMessage(data.response, 'bot');

            if (data.is_crisis) {
                helplineSpan.textContent = data.helpline;
                crisisModal.show();
            }
        } catch (error) {
            console.error("Fetch Error:", error);
            removeTypingIndicator();
            appendMessage('I seem to be having trouble connecting. Please try again in a moment.', 'bot');
        }
    }

    function appendMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        messageDiv.textContent = text;
        chatWindow.appendChild(messageDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    function appendTypingIndicator() {
        const indicatorDiv = document.createElement('div');
        indicatorDiv.className = 'message bot-message typing-indicator';
        indicatorDiv.innerHTML = '<span></span><span></span><span></span>';
        chatWindow.appendChild(indicatorDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    function removeTypingIndicator() {
        const indicator = chatWindow.querySelector('.typing-indicator');
        if (indicator) {
            chatWindow.removeChild(indicator);
        }
    }

    sendBtn.addEventListener('click', () => sendMessage());
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            sendMessage();
        }
    });
    
    document.querySelectorAll('.prompt-btn').forEach(button => {
        button.addEventListener('click', () => {
            sendMessage(button.textContent.replace(/"/g, ''));
        });
    });
});