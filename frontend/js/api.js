const API = (() => {
  const BASE_URL = 'https://eva-jqur.onrender.com';

  function getToken() {
    const session = JSON.parse(sessionStorage.getItem('eva_session') || 'null');
    return session?.access_token || null;
  }

  function authHeaders() {
    const token = getToken();
    const headers = { 'Content-Type': 'application/json' };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
  }

  async function request(method, path, body) {
    const url = `${BASE_URL}${path}`;
    const options = { method, headers: authHeaders() };
    if (body) {
      options.body = JSON.stringify(body);
    }

    const response = await fetch(url, options);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || `HTTP ${response.status}`);
    }

    return data;
  }

  async function getTokenRefreshed() {
    const sessionData = sessionStorage.getItem('eva_session');
    if (!sessionData) return null;
    const { data, error } = await supabaseClient.auth.refreshSession();
    if (error || !data.session) {
      sessionStorage.removeItem('eva_session');
      window.location.href = 'login.html';
      return null;
    }
    sessionStorage.setItem('eva_session', JSON.stringify(data.session));
    return data.session.access_token;
  }

  async function chatStream(message, conversationId, onChunk, onDone, onError) {
    const token = getToken();
    if (!token) {
      onError('Not authenticated');
      return;
    }

    try {
      const response = await fetch(`${BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          message,
          conversation_id: conversationId,
          stream: true,
        }),
      });

      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        onError(data.error || `HTTP ${response.status}`);
        return;
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          const jsonStr = line.slice(6).trim();
          if (jsonStr === '[DONE]') continue;

          try {
            const data = JSON.parse(jsonStr);
            if (data.type === 'chunk') {
              onChunk(data.content);
            } else if (data.type === 'done') {
              onDone(data.conversation_id, data.tokens);
            } else if (data.type === 'error') {
              onError(data.error);
            }
          } catch {
            // skip malformed lines
          }
        }
      }
    } catch (err) {
      onError('Connection error. Please check your connection.');
    }
  }

  return {
    async chat(message, conversationId) {
      return request('POST', '/chat', { message, conversation_id: conversationId });
    },

    chatStream,

    async getConversations(query) {
      const qs = query ? `?q=${encodeURIComponent(query)}` : '';
      return request('GET', `/conversations${qs}`);
    },

    async createConversation(title) {
      return request('POST', '/conversations', { title });
    },

    async getConversation(id) {
      return request('GET', `/conversations/${id}`);
    },

    async renameConversation(id, title) {
      return request('PATCH', `/conversations/${id}/rename`, { title });
    },

    async deleteConversation(id) {
      return request('DELETE', `/conversations/${id}`);
    },

    async exportConversation(id) {
      return request('GET', `/conversations/${id}/export`);
    },

    async getProfile() {
      return request('GET', '/auth/me');
    },

    async health() {
      try {
        const resp = await fetch(`${BASE_URL}/health`);
        return await resp.json();
      } catch {
        return null;
      }
    },

    getToken,
    getTokenRefreshed,
    authHeaders,
  };
})();
