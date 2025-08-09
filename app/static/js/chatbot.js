// ----- Chatbot popup -----
const launcher = document.getElementById('chat-launcher');
const chatbox = document.getElementById('chatbox');
const closeBtn = document.getElementById('chat-close');
const form = document.getElementById('chat-form');
const input = document.getElementById('chat-text');
const bodyEl = document.getElementById('chat-body');

const openChat = () => { chatbox.classList.add('open'); launcher.style.display = 'none'; input?.focus(); };
const closeChat = () => { chatbox.classList.remove('open'); launcher.style.display = 'inline-flex'; };

launcher.addEventListener('click', openChat);
closeBtn.addEventListener('click', closeChat);

// click outside to close
document.addEventListener('mousedown', (e) => {
    if (!chatbox.classList.contains('open')) return;
    if (!chatbox.contains(e.target) && !launcher.contains(e.target)) closeChat();
});
// ESC to close
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeChat(); });

// Demo chat behavior
form?.addEventListener('submit', (e) => {
    e.preventDefault();
    const text = (input.value || '').trim();
    if (!text) return;
    bodyEl.insertAdjacentHTML('beforeend', `<div class="bubble user"></div>`);
    bodyEl.lastElementChild.textContent = text;
    input.value = ''; bodyEl.scrollTop = bodyEl.scrollHeight;
    setTimeout(() => {
        bodyEl.insertAdjacentHTML('beforeend', `<div class="bubble bot"></div>`);
        bodyEl.lastElementChild.textContent = `You said: ${text}`;
        bodyEl.scrollTop = bodyEl.scrollHeight;
    }, 450);
});