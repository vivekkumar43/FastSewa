// ====================
// FASTSEWA CHATBOT JS
// ====================

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Chatbot
    initFastSewaChatbot();
});

function initFastSewaChatbot() {
    // DOM Elements
    const toggleBtn = document.getElementById('fastsewaChatbotToggle');
    const chatContainer = document.getElementById('fastsewaChatbotContainer');
    const closeBtn = document.getElementById('chatbotCloseBtn');
    const sendBtn = document.getElementById('chatbotSendBtn');
    const chatInput = document.getElementById('chatbotInput');
    const messagesContainer = document.getElementById('chatbotMessages');
    
    // Chatbot State
    let isOpen = false;
    let currentService = null;
    let conversationHistory = [];
    
    // API Configuration
    const API_BASE_URL = 'http://localhost:5000/api'; // Change to your backend URL
    const SESSION_ID = 'user_' + Date.now();
    
    // ====================
    // EVENT LISTENERS
    // ====================
    
    toggleBtn.addEventListener('click', toggleChatbot);
    closeBtn.addEventListener('click', closeChatbot);
    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    // Show welcome message on first open
    let firstOpen = true;
    
    // ====================
    // CHATBOT FUNCTIONS
    // ====================
    
    function toggleChatbot() {
        isOpen = !isOpen;
        chatContainer.style.display = isOpen ? 'flex' : 'none';
        
        if (isOpen && firstOpen) {
            showWelcomeMessage();
            firstOpen = false;
            // Hide notification badge
            document.querySelector('.notification-badge').style.display = 'none';
        }
        
        if (isOpen) {
            setTimeout(() => chatInput.focus(), 100);
        }
    }
    
    function closeChatbot() {
        isOpen = false;
        chatContainer.style.display = 'none';
    }
    
    async function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;
        
        // Add user message
        addMessage(message, 'user');
        chatInput.value = '';
        
        // Send to backend API
        try {
            const response = await fetch(`${API_BASE_URL}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    user_id: SESSION_ID,
                    service: currentService
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Update current service
                if (data.service) {
                    currentService = data.service;
                }
                
                // Add bot response
                addMessage(data.response, 'bot');
                
                // Handle PDF download if generated
                if (data.pdf_generated && data.pdf_file) {
                    addPDFDownloadButton(data.pdf_file);
                }
            } else {
                addMessage("Sorry, there was an error. Please try again.", 'bot');
            }
            
        } catch (error) {
            console.error('Chatbot API error:', error);
            addMessage("I'm currently offline. Please call +91 8275723755 for assistance.", 'bot');
        }
    }
    
    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chatbot-message chatbot-${sender}-message`;
        messageDiv.innerHTML = formatMessage(text);
        
        messagesContainer.appendChild(messageDiv);
        conversationHistory.push({ text, sender, time: new Date() });
        
        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    function formatMessage(text) {
        // Convert newlines to <br>
        let formatted = text.replace(/\n/g, '<br>');
        
        // Highlight service names
        const services = ['Construction', 'Security', 'Medical', 'Legal', 'Land', 'Repair'];
        services.forEach(service => {
            const regex = new RegExp(service, 'gi');
            formatted = formatted.replace(regex, `<strong>${service}</strong>`);
        });
        
        return formatted;
    }
    
    function addPDFDownloadButton(filename) {
        const downloadBtn = document.createElement('a');
        downloadBtn.className = 'pdf-download-btn';
        downloadBtn.href = `${API_BASE_URL}/download-pdf/${filename}`;
        downloadBtn.target = '_blank';
        downloadBtn.innerHTML = `
            <i class="fas fa-file-pdf"></i>
            Download Your Quote
        `;
        
        messagesContainer.appendChild(downloadBtn);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    function showWelcomeMessage() {
        const welcomeMsg = `
            <div style="text-align: center; margin-bottom: 15px;">
                <div style="font-size: 32px; margin-bottom: 10px;">👋</div>
                <h3 style="margin: 0 0 10px 0; color: #1f2937;">Welcome to FastSewa!</h3>
                <p style="color: #6b7280; margin: 0 0 20px 0;">I'm your AI assistant for 6 essential services:</p>
            </div>
            
            <div class="service-quick-cards">
                <div class="service-card" data-service="construction">
                    <div class="service-icon">🏗️</div>
                    <div class="service-name">Construction</div>
                </div>
                <div class="service-card" data-service="security">
                    <div class="service-icon">🛡️</div>
                    <div class="service-name">Security</div>
                </div>
                <div class="service-card" data-service="legal">
                    <div class="service-icon">⚖️</div>
                    <div class="service-name">Legal & GST</div>
                </div>
                <div class="service-card" data-service="medical">
                    <div class="service-icon">🏥</div>
                    <div class="service-name">Medical</div>
                </div>
                <div class="service-card" data-service="land">
                    <div class="service-icon">📋</div>
                    <div class="service-name">Land Verification</div>
                </div>
                <div class="service-card" data-service="repair">
                    <div class="service-icon">🔧</div>
                    <div class="service-name">Repair</div>
                </div>
            </div>
            
            <p style="text-align: center; margin-top: 20px; color: #6b7280; font-size: 14px;">
                Click a service above or type your question below
            </p>
        `;
        
        const welcomeDiv = document.createElement('div');
        welcomeDiv.innerHTML = welcomeMsg;
        messagesContainer.appendChild(welcomeDiv);
        
        // Add click events to service cards
        document.querySelectorAll('.service-card').forEach(card => {
            card.addEventListener('click', function() {
                const service = this.getAttribute('data-service');
                selectService(service);
            });
        });
    }
    
    function selectService(service) {
        const serviceMessages = {
            'construction': 'I need construction services',
            'security': 'I need security guards',
            'legal': 'I need legal and GST services',
            'medical': 'I need medical services',
            'land': 'I need land verification',
            'repair': 'I need repair services'
        };
        
        // Simulate user clicking the service
        chatInput.value = serviceMessages[service];
        sendMessage();
    }
    
    // Auto-open chat after 10 seconds (optional)
    setTimeout(() => {
        if (!isOpen) {
            document.querySelector('.notification-badge').style.display = 'flex';
        }
    }, 10000);
}