document.addEventListener('DOMContentLoaded', function() {
    const sendBtn = document.getElementById('send-btn');
    const userInput = document.getElementById('user-input');
    const chatWindow = document.getElementById('chat-window');
    const starterPrompts = document.querySelector('.starter-prompts');
    
    // Modal controls
    const crisisModal = new bootstrap.Modal(document.getElementById('crisisModal'));
    const helplineSpan = document.getElementById('helpline-number');
    
    // --- NEW: Settings Modal Controls (Feature 5) ---
    const saveSettingsBtn = document.getElementById('save-settings-btn');
    const locationInput = document.getElementById('location-input');
    
    // --- NEW: Research Consent Checkbox (Feature 7) ---
    const consentCheckbox = document.getElementById('research-consent');
    
    // Mood gauge
    const moodNeedle = document.getElementById('mood-needle');

    // --- NEW: Load location from localStorage on page load ---
    if (locationInput) {
        locationInput.value = localStorage.getItem('userLocation') || '';
    }

    // --- NEW: Save location to localStorage ---
    if (saveSettingsBtn) {
        saveSettingsBtn.addEventListener('click', () => {
            const userLocation = locationInput.value.trim();
            if (userLocation) {
                localStorage.setItem('userLocation', userLocation);
                console.log('Location saved:', userLocation);
            } else {
                localStorage.removeItem('userLocation');
                console.log('Location cleared');
            }
        });
    }

    async function sendMessage(messageText) {
        const message = messageText || userInput.value.trim();
        if (message === '') return;

        appendMessage(message, 'user');
        userInput.value = '';
        if (starterPrompts) {
            starterPrompts.style.display = 'none';
        }
        appendTypingIndicator();

        // --- MODIFIED: Get location and consent values ---
        const userLocation = localStorage.getItem('userLocation') || null;
        const hasConsented = consentCheckbox ? consentCheckbox.checked : false;

        try {
            const response = await fetch("/api/ask", {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                // --- MODIFIED: Send location and consent to backend ---
                body: JSON.stringify({ 
                    message: message,
                    location: userLocation,
                    consent: hasConsented 
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            removeTypingIndicator();
            appendMessage(data.response, 'bot');

            if (data.mood && moodNeedle) {
                updateMoodTracker(data.mood);
            }

            if (data.is_crisis) {
                if (helplineSpan) helplineSpan.textContent = data.helpline;
                if (crisisModal) crisisModal.show();
            }
        } catch (error) {
            console.error("Fetch Error:", error);
            removeTypingIndicator();
            appendMessage('I seem to be having trouble connecting. Please try again in a moment.', 'bot');
        }
    }
    
    function updateMoodTracker(mood) {
        moodNeedle.classList.remove('mood-green-needle', 'mood-yellow-needle', 'mood-red-needle');

        switch (mood.toLowerCase()) {
            case 'happy':
            case 'positive':
                moodNeedle.classList.add('mood-green-needle');
                break;
            case 'upset':
            case 'neutral':
            case 'anxious':
                moodNeedle.classList.add('mood-yellow-needle');
                break;
            case 'sad':
            case 'angry':
            case 'negative':
                moodNeedle.classList.add('mood-red-needle');
                break;
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

    if (sendBtn) {
        sendBtn.addEventListener('click', () => sendMessage());
    }
    
    if (userInput) {
        userInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                sendMessage();
            }
        });
    }
    
    if (starterPrompts) {
        document.querySelectorAll('.prompt-btn').forEach(button => {
            button.addEventListener('click', () => {
                sendMessage(button.textContent.replace(/"/g, ''));
            });
        });
    }
});