const chat = document.getElementById('chat');
const input = document.getElementById('messageInput');
const themeToggle = document.getElementById('themeToggle');

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

function sendMessage() {
  const text = input.value.trim();
  if (!text) return;
  
  appendMessage('user', text);
  input.value = '';
  input.style.height = 'auto';

  // Simulated assistant response
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
  
  setTimeout(() => {
    typingContent.textContent = `I received: ${text}`;
    chat.scrollTop = chat.scrollHeight;
  }, 800);
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

// Initialize the theme when page loads
document.addEventListener('DOMContentLoaded', initTheme);
