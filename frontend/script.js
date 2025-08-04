const chat = document.getElementById('chat');
const input = document.getElementById('messageInput');
const themeToggle = document.getElementById('themeToggle');

// Configuration variables
let config = {};

// Load config.json and set config
async function loadConfig() {
  try {
    const response = await fetch('config.json');
    if (!response.ok) throw new Error('Failed to load config.json');
    config = await response.json();
    console.log('Loaded config:', config);
  } catch (e) {
    console.error('Could not load config.json:', e);
  }
}

// Initialize theme based on user preference
function initTheme() {
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme === 'dark' || (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    document.body.classList.add('dark-theme');
  }
}

// Toggle theme
function toggleTheme() {
  if (document.body.classList.contains('dark-theme')) {
    document.body.classList.remove('dark-theme');
    localStorage.setItem('theme', 'light');
  } else {
    document.body.classList.add('dark-theme');
    localStorage.setItem('theme', 'dark');
  }
}

// Create and append a message to the chat
function appendMessage(role, text) {
  const msg = document.createElement('div');
  msg.className = `message ${role}`;
  
  const iconDiv = document.createElement('div');
  iconDiv.className = 'message-icon';
  
  const icon = document.createElement('i');
  
  if (role === 'user') {
    icon.className = 'fas fa-user';
  } else {
    icon.className = 'fas fa-robot';
  }
  
  iconDiv.appendChild(icon);
  msg.appendChild(iconDiv);
  
  const contentDiv = document.createElement('div');
  contentDiv.className = 'message-content';
  contentDiv.textContent = text;
  
  msg.appendChild(contentDiv);
  chat.appendChild(msg);
  chat.scrollTop = chat.scrollHeight;
}

async function sendMessage() {
  const text = input.value.trim();
  if (!text) return;
  
  // Display user message in the chat
  appendMessage('user', text);
  
  // Clear the input field after sending
  input.value = '';
  input.style.height = 'auto';

  // Show typing indicator
  const typingMsg = document.createElement('div');
  typingMsg.className = 'message assistant';
  
  const typingIconDiv = document.createElement('div');
  typingIconDiv.className = 'message-icon';
  
  const typingIcon = document.createElement('i');
  typingIcon.className = 'fas fa-robot';
  typingIconDiv.appendChild(typingIcon);
  
  const typingContent = document.createElement('div');
  typingContent.className = 'message-content';
  typingContent.textContent = 'Typing...';
  
  typingMsg.appendChild(typingIconDiv);
  typingMsg.appendChild(typingContent);
  
  chat.appendChild(typingMsg);
  chat.scrollTop = chat.scrollHeight;
  
  try {
    // Make API request to MCP client with the user's message
    const baseUrl = config.MCP_CLIENT_BASE_URL;
    const endpoint = '/ask';
    const url = baseUrl + endpoint;
    
    // Prepare the payload with the user's query from the input field
    const payload = {
      query: text
    };
    
    console.log(`Sending request to ${url}`, payload);
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });
    
    if (!response.ok) {
      throw new Error(`API request failed with status ${response.status}`);
    }
    
    const data = await response.json();
    console.log('API response:', data);
    
    // Update the typing message with the response
    typingContent.textContent = data.response || data.message || JSON.stringify(data);
    chat.scrollTop = chat.scrollHeight;
    
  } catch (error) {
    console.error('Error calling MCP client:', error);
    typingContent.textContent = `Error: Failed to get response from server. ${error.message}`;
    chat.scrollTop = chat.scrollHeight;
  }
}

// Event listeners
themeToggle.addEventListener('click', toggleTheme);

input.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

input.addEventListener('input', () => {
  input.style.height = 'auto';
  input.style.height = input.scrollHeight + 'px';
});

// Initialize when page loads
document.addEventListener('DOMContentLoaded', async () => {
  await loadConfig();
  initTheme();
});
