// ===== Chatbot popup (v2) =====
const launcher = document.getElementById('chat-launcher');
const chatbox = document.getElementById('chatbox');
const closeBtn = document.getElementById('chat-close');
const form = document.getElementById('chat-form');
const input = document.getElementById('chat-text');
const bodyEl = document.getElementById('chat-body');

const LS_KEY_OPEN = 'chatbot.open';
const MAX_HISTORY_RENDER = 200; // phòng trường hợp file lớn

function addBubble(role, text) {
    const el = document.createElement('div');
    el.className = `bubble ${role}`;
    el.textContent = text;
    bodyEl.appendChild(el);
    bodyEl.scrollTop = bodyEl.scrollHeight;
}

async function loadHistory() {
    try {
        const res = await fetch('/api/chatbot/history', { method: 'GET' });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        const list = (data.history || []).slice(-MAX_HISTORY_RENDER);

        bodyEl.innerHTML = '';
        for (const m of list) addBubble(m.role, m.text);
    } catch (e) {
        // server chưa hỗ trợ / bị lỗi -> vẫn chào
        if (!bodyEl.querySelector('.bubble')) addBubble('bot', 'Xin chào! 👋, tôi có thể giúp gì cho bạn?');
    }
}

function openChat() {
    chatbox.classList.add('open');
    chatbox.setAttribute('aria-hidden', 'false');
    launcher.style.display = 'none';
    launcher.setAttribute('aria-expanded', 'true');
    localStorage.setItem(LS_KEY_OPEN, '1');
    input?.focus();
}

function closeChat() {
    chatbox.classList.remove('open');
    chatbox.setAttribute('aria-hidden', 'true');
    launcher.style.display = 'inline-flex';
    launcher.setAttribute('aria-expanded', 'false');
    localStorage.setItem(LS_KEY_OPEN, '0');
    launcher.focus();
}

launcher.addEventListener('click', openChat);
closeBtn.addEventListener('click', closeChat);

// click outside to close
document.addEventListener('mousedown', (e) => {
    if (!chatbox.classList.contains('open')) return;
    if (!chatbox.contains(e.target) && !launcher.contains(e.target)) closeChat();
});
// ESC to close
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeChat(); });

// Rehydrate on load
document.addEventListener('DOMContentLoaded', async () => {
    await loadHistory();
    if (localStorage.getItem(LS_KEY_OPEN) === '1') openChat();
});

// Submit -> call API + server sẽ tự lưu vào chat_data.json
form?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = (input.value || '').trim();
    if (!text) return;

    addBubble('user', text);
    input.value = '';

    const btn = form.querySelector('.send-btn');
    btn?.setAttribute('disabled', 'true');

    try {
        const res = await fetch('/api/chatbot', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        });

        let reply = 'Có lỗi xảy ra.';
        if (res.ok) {
            const data = await res.json();
            reply = data.reply || data.error || reply;
        } else {
            const data = await res.json().catch(() => ({}));
            reply = data.error || `Lỗi máy chủ (${res.status}).`;
        }
        addBubble('bot', reply);
    } catch (err) {
        addBubble('bot', 'Không kết nối được máy chủ.');
    } finally {
        btn?.removeAttribute('disabled');
    }
});
