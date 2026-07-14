const Chat = (() => {
  let currentConversationId = null;
  let currentModel = 'llama-3.1-8b-instant';

  const chatBox = document.getElementById('chat-box');
  const input = document.getElementById('message');

  function renderMessage(content, isUser) {
    const div = document.createElement('div');
    div.className = `message ${isUser ? 'user' : 'ai'}`;

    let inner = '';
    if (!isUser) {
      inner += `<div class="avatar-ai"><i class="fa-solid fa-sparkles"></i></div>`;
    }

    const rendered = isUser ? UI.escapeHtml(content) : UI.renderMarkdown(content);
    inner += `<div class="message-content">${rendered}</div>`;
    div.innerHTML = inner;

    if (!isUser) {
      UI.addCopyButtons(div);
      if (typeof hljs !== 'undefined') {
        div.querySelectorAll('pre code').forEach((b) => hljs.highlightElement(b));
      }
    }

    return div;
  }

  function addUserMessage(text) {
    const el = renderMessage(text, true);
    chatBox.appendChild(el);
    UI.scrollBottom();
  }

  function addBotMessage(text, tokens) {
    const el = renderMessage(text, false);
    chatBox.appendChild(el);
    UI.scrollBottom();
    UI.updateTokenDisplay(tokens);
  }

  function addTyping() {
    const id = 'typing-' + Date.now();
    const div = document.createElement('div');
    div.className = 'message ai';
    div.id = id;
    div.innerHTML = `
      <div class="avatar-ai"><i class="fa-solid fa-sparkles"></i></div>
      <div class="message-content typing">
        <span></span><span></span><span></span>
      </div>
    `;
    chatBox.appendChild(div);
    UI.scrollBottom();
    return id;
  }

  function removeTyping(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
  }

  function clearMessages() {
    chatBox.querySelectorAll('.message').forEach((m) => m.remove());
    const welcome = document.getElementById('welcome-screen');
    if (welcome) welcome.style.display = 'block';
    currentConversationId = null;
    document.getElementById('delete-chat-btn').style.display = 'none';
    UI.updateTokenDisplay(null);
  }

  function removeWelcome() {
    const welcome = document.getElementById('welcome-screen');
    if (welcome) welcome.style.display = 'none';
  }

  function setConversationId(id) {
    currentConversationId = id;
    const btn = document.getElementById('delete-chat-btn');
    if (btn) btn.style.display = id ? 'inline-flex' : 'none';
  }

  function getConversationId() {
    return currentConversationId;
  }

  function getModel() {
    return currentModel;
  }

  function setModel(model) {
    currentModel = model;
  }

  async function send() {
    const text = input.value.trim();
    if (!text) return;

    removeWelcome();
    addUserMessage(text);
    input.value = '';
    UI.showLoading(true);

    const typingId = addTyping();
    let streamContent = '';
    const streamDiv = document.createElement('div');
    streamDiv.className = 'message ai';

    try {
      removeTyping(typingId);

      streamDiv.innerHTML = `
        <div class="avatar-ai"><i class="fa-solid fa-sparkles"></i></div>
        <div class="message-content streaming"></div>
      `;
      chatBox.appendChild(streamDiv);
      UI.scrollBottom();

      await API.chatStream(
        text,
        currentConversationId,
        (chunk) => {
          streamContent += chunk;
          const contentEl = streamDiv.querySelector('.message-content');
          if (contentEl) {
            contentEl.innerHTML = UI.renderMarkdown(streamContent);
            UI.addCopyButtons(streamDiv);
            if (typeof hljs !== 'undefined') {
              streamDiv.querySelectorAll('pre code').forEach((b) => hljs.highlightElement(b));
            }
          }
          UI.scrollBottom();
        },
        (newConvId, tokens) => {
          if (newConvId && !currentConversationId) {
            setConversationId(newConvId);
            app.loadConversations();
          }
          UI.updateTokenDisplay(tokens);
          UI.scrollBottom();
        },
        (error) => {
          streamDiv.remove();
          addBotMessage(error || 'An error occurred. Please try again.');
          console.error('Stream error:', error);
          UI.toast('Failed to get response', 'error');
        }
      );
    } catch (err) {
      removeTyping(typingId);
      const existing = document.getElementById(streamDiv.id || '');
      if (existing) existing.remove();
      addBotMessage('Connection error. Please check your connection and try again.');
      console.error('Chat error:', err);
      UI.toast('Failed to send message', 'error');
    } finally {
      UI.showLoading(false);
    }
  }

  function loadMessages(messages) {
    chatBox.querySelectorAll('.message').forEach((m) => m.remove());
    removeWelcome();

    if (!messages || messages.length === 0) {
      document.getElementById('welcome-screen').style.display = 'block';
      return;
    }

    for (const msg of messages) {
      if (msg.role === 'user') {
        chatBox.appendChild(renderMessage(msg.content, true));
      } else if (msg.role === 'assistant') {
        chatBox.appendChild(renderMessage(msg.content, false));
      }
    }

    UI.scrollBottom();
  }

  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  });

  return {
    send,
    clearMessages,
    removeWelcome,
    addUserMessage,
    addBotMessage,
    loadMessages,
    setConversationId,
    getConversationId,
    setModel,
    getModel,
  };
})();
