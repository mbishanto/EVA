const UI = (() => {
  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  function renderMarkdown(text) {
    if (typeof marked === 'undefined') {
      return escapeHtml(text).replace(/\n/g, '<br>');
    }

    marked.setOptions({
      breaks: true,
      gfm: true,
      highlight: function (code, lang) {
        if (typeof hljs !== 'undefined' && lang && hljs.getLanguage(lang)) {
          try {
            return hljs.highlight(code, { language: lang }).value;
          } catch {}
        }
        try {
          return hljs.highlightAuto(code).value;
        } catch {
          return escapeHtml(code);
        }
      },
    });

    const raw = marked.parse(text);
    return DOMPurify ? DOMPurify.sanitize(raw) : raw;
  }

  function toast(message, type = 'info', duration = 4000) {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const icons = {
      success: 'fa-circle-check',
      error: 'fa-circle-xmark',
      info: 'fa-circle-info',
      warning: 'fa-triangle-exclamation',
    };

    const el = document.createElement('div');
    el.className = `toast ${type}`;
    el.innerHTML = `<i class="fa-solid ${icons[type] || icons.info}"></i> ${escapeHtml(message)}`;
    container.appendChild(el);

    setTimeout(() => {
      el.style.animation = 'toastOut 0.3s ease forwards';
      setTimeout(() => el.remove(), 300);
    }, duration);
  }

  function showModal({ title, value, confirmText, confirmClass, onConfirm, onCancel }) {
    const existing = document.querySelector('.modal-overlay');
    if (existing) existing.remove();

    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.innerHTML = `
      <div class="modal-box">
        <h3>${escapeHtml(title)}</h3>
        ${value !== undefined ? `<input type="text" id="modal-input" value="${escapeHtml(value)}">` : ''}
        <div class="modal-actions">
          <button class="btn-cancel" id="modal-cancel">Cancel</button>
          <button class="${confirmClass || 'btn-confirm'}" id="modal-confirm">${escapeHtml(confirmText || 'Confirm')}</button>
        </div>
      </div>
    `;

    document.body.appendChild(overlay);

    const input = overlay.querySelector('#modal-input');
    if (input) {
      input.focus();
      input.select();
      input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') overlay.querySelector('#modal-confirm').click();
        if (e.key === 'Escape') close();
      });
    }

    function close() {
      overlay.remove();
      if (onCancel) onCancel();
    }

    overlay.querySelector('#modal-cancel').onclick = close;
    overlay.querySelector('#modal-confirm').onclick = () => {
      const val = input ? input.value.trim() : true;
      overlay.remove();
      if (onConfirm) onConfirm(val);
    };

    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) close();
    });
  }

  function createCopyButton(codeEl) {
    const btn = document.createElement('button');
    btn.className = 'copy-btn';
    btn.innerHTML = '<i class="fa-regular fa-clipboard"></i> Copy';
    btn.onclick = async () => {
      try {
        const code = codeEl.textContent || '';
        await navigator.clipboard.writeText(code);
        btn.innerHTML = '<i class="fa-regular fa-clipboard-check"></i> Copied!';
        btn.classList.add('copied');
        setTimeout(() => {
          btn.innerHTML = '<i class="fa-regular fa-clipboard"></i> Copy';
          btn.classList.remove('copied');
        }, 2000);
      } catch {
        toast('Failed to copy', 'error');
      }
    };
    return btn;
  }

  function addCopyButtons(container) {
    container.querySelectorAll('pre code').forEach((block) => {
      const pre = block.parentElement;
      if (!pre.querySelector('.copy-btn')) {
        pre.style.position = 'relative';
        pre.appendChild(createCopyButton(block));
      }
    });
  }

  function scrollBottom() {
    const chatBox = document.getElementById('chat-box');
    requestAnimationFrame(() => {
      chatBox.scrollTop = chatBox.scrollHeight;
    });
  }

  function showLoading(show) {
    const sendBtn = document.getElementById('send-btn');
    if (!sendBtn) return;
    if (show) {
      sendBtn.disabled = true;
      sendBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i>';
    } else {
      sendBtn.disabled = false;
      sendBtn.innerHTML = '<i class="fa-solid fa-arrow-up"></i>';
    }
  }

  function updateTokenDisplay(tokens) {
    const el = document.getElementById('token-display');
    if (!el) return;
    if (tokens && tokens.total > 0) {
      el.textContent = `⚡ ${tokens.total} tokens`;
      el.style.display = 'block';
    } else {
      el.style.display = 'none';
    }
  }

  return {
    escapeHtml,
    renderMarkdown,
    toast,
    showModal,
    createCopyButton,
    addCopyButtons,
    scrollBottom,
    showLoading,
    updateTokenDisplay,
  };
})();
