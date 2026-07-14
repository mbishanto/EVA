const app = (() => {
  async function init() {
    const session = await handleAuthRedirect();
    if (!session) {
      window.location.href = 'login.html';
      return;
    }

    const avatar = document.getElementById('profile-avatar');
    const nameEl = document.getElementById('profile-name');
    if (session.user?.email) {
      nameEl.textContent = session.user.email.split('@')[0] || 'User';
      avatar.textContent = nameEl.textContent[0].toUpperCase();
    }

    await loadConversations();
  }

  async function sendMessage() {
    await Chat.send();
  }

  async function loadConversations(query) {
    try {
      const data = await API.getConversations(query);
      const list = data.data || [];
      const container = document.getElementById('conversation-list');

      if (!list || list.length === 0) {
        container.innerHTML = '<div class="conv-count">No conversations yet</div>';
        return;
      }

      container.innerHTML = '';
      list.forEach((conv) => {
        const item = document.createElement('button');
        item.className = 'menu-item';
        item.dataset.convId = conv.id;
        if (conv.id === Chat.getConversationId()) {
          item.classList.add('active');
        }

        const title = conv.title || 'New Chat';
        item.innerHTML = `
          <i class="fa-regular fa-message"></i>
          <span class="conv-title">${escapeHtml(title)}</span>
          <span class="conv-actions">
            <button data-action="rename" title="Rename">
              <i class="fa-solid fa-pen"></i>
            </button>
            <button data-action="delete" title="Delete">
              <i class="fa-solid fa-xmark"></i>
            </button>
          </span>
        `;

        item.querySelector('[data-action="rename"]').onclick = (e) => {
          e.stopPropagation();
          app.renameConversation(conv.id, title);
        };
        item.querySelector('[data-action="delete"]').onclick = (e) => {
          e.stopPropagation();
          app.deleteConversation(conv.id);
        };
        item.onclick = () => openConversation(conv.id);
        container.appendChild(item);
      });
    } catch (err) {
      console.error('Failed to load conversations:', err);
    }
  }

  async function openConversation(id) {
    Chat.setConversationId(id);
    try {
      const data = await API.getConversation(id);
      if (data.success && data.data) {
        Chat.loadMessages(data.data.messages);
        const title = data.data.conversation?.title || 'Chat';
        document.getElementById('chat-title').textContent = title;

        document.querySelectorAll('.menu-item').forEach((el) => {
          el.classList.toggle('active', el.dataset.convId === id);
        });
      }
    } catch (err) {
      console.error('Failed to load conversation:', err);
      UI.toast('Failed to load conversation', 'error');
    }
  }

  function newChat() {
    Chat.clearMessages();
    Chat.setConversationId(null);
    document.getElementById('chat-title').textContent = 'Eva AI';
    document.querySelectorAll('.menu-item').forEach((el) => el.classList.remove('active'));
  }

  async function renameConversation(id, currentTitle) {
    UI.showModal({
      title: 'Rename Conversation',
      value: currentTitle,
      confirmText: 'Rename',
      async onConfirm(newTitle) {
        if (!newTitle || newTitle === currentTitle) return;
        try {
          await API.renameConversation(id, newTitle);
          UI.toast('Conversation renamed', 'success');
          await loadConversations();
          if (Chat.getConversationId() === id) {
            document.getElementById('chat-title').textContent = newTitle;
          }
        } catch (err) {
          UI.toast('Failed to rename', 'error');
        }
      },
    });
  }

  async function deleteConversation(id) {
    UI.showModal({
      title: 'Delete Conversation?',
      value: undefined,
      confirmText: 'Delete',
      confirmClass: 'btn-danger',
      async onConfirm() {
        try {
          await API.deleteConversation(id);
          UI.toast('Conversation deleted', 'success');
          if (Chat.getConversationId() === id) {
            newChat();
          }
          await loadConversations();
        } catch (err) {
          UI.toast('Failed to delete', 'error');
        }
      },
    });
  }

  async function deleteCurrentConversation() {
    const id = Chat.getConversationId();
    if (id) await deleteConversation(id);
  }

  async function exportChat() {
    const id = Chat.getConversationId();
    if (!id) {
      UI.toast('No conversation to export', 'warning');
      return;
    }

    try {
      const data = await API.exportConversation(id);
      if (data.success && data.data) {
        const json = JSON.stringify(data.data, null, 2);
        const blob = new Blob([json], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `eva-${data.data.title || 'chat'}.json`;
        a.click();
        URL.revokeObjectURL(url);
        UI.toast('Conversation exported', 'success');
      }
    } catch (err) {
      UI.toast('Failed to export', 'error');
    }
  }

  function searchConversations(query) {
    loadConversations(query);
  }

  function clearChat() {
    Chat.clearMessages();
    Chat.setConversationId(null);
  }

  function changeModel(model) {
    Chat.setModel(model);
    UI.toast(`Model switched to ${model}`, 'info');
  }

  function logout() {
    logoutUser();
  }

  document.addEventListener('DOMContentLoaded', init);

  return {
    init,
    sendMessage,
    loadConversations,
    openConversation,
    newChat,
    renameConversation,
    deleteConversation,
    deleteCurrentConversation,
    exportChat,
    searchConversations,
    clearChat,
    changeModel,
    logout,
  };
})();

function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebar-overlay');
  sidebar.classList.toggle('open');
  overlay.classList.toggle('active');
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
