const SUPABASE_URL = 'https://jvmicjoprpsgjluupnck.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2bWljam9wcnBzZ2psdXVwbmNrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzkxOTQzMjYsImV4cCI6MjA5NDc3MDMyNn0.WF7JNH_X-JO5CmprslS701ne5ZPBow5q4ysvjQAi-EU';

const supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_KEY, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
    storageKey: 'eva-auth-storage',
  },
});

async function signup() {
  const email = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value;
  const errorEl = document.getElementById('auth-error');
  const btn = document.getElementById('signup-btn');
  const text = document.getElementById('signup-text');
  const spinner = document.getElementById('signup-spinner');

  errorEl.style.display = 'none';

  if (!email || !password) {
    errorEl.textContent = 'Please fill in all fields.';
    errorEl.style.display = 'block';
    return;
  }

  if (password.length < 6) {
    errorEl.textContent = 'Password must be at least 6 characters.';
    errorEl.style.display = 'block';
    return;
  }

  btn.disabled = true;
  text.textContent = 'Creating...';
  spinner.style.display = 'inline-block';

  const { error } = await supabaseClient.auth.signUp({ email, password });

  btn.disabled = false;
  text.textContent = 'Create Account';
  spinner.style.display = 'none';

  if (error) {
    errorEl.textContent = error.message;
    errorEl.style.display = 'block';
    return;
  }

  alert('Account created! Please check your email to confirm, then sign in.');
  window.location.href = 'login.html';
}

async function login() {
  const email = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value;
  const errorEl = document.getElementById('auth-error');
  const btn = document.getElementById('login-btn');
  const text = document.getElementById('login-text');
  const spinner = document.getElementById('login-spinner');

  errorEl.style.display = 'none';

  if (!email || !password) {
    errorEl.textContent = 'Please fill in all fields.';
    errorEl.style.display = 'block';
    return;
  }

  btn.disabled = true;
  text.textContent = 'Signing in...';
  spinner.style.display = 'inline-block';

  const { data, error } = await supabaseClient.auth.signInWithPassword({
    email,
    password,
  });

  btn.disabled = false;
  text.textContent = 'Sign In';
  spinner.style.display = 'none';

  if (error) {
    errorEl.textContent = error.message;
    errorEl.style.display = 'block';
    return;
  }

  if (data?.session) {
    sessionStorage.setItem('eva_session', JSON.stringify(data.session));
    window.location.href = 'index.html';
  }
}

async function handleAuthRedirect() {
  const sessionData = sessionStorage.getItem('eva_session');
  if (sessionData) {
    const session = JSON.parse(sessionData);
    const { data: { session: currentSession }, error } = await supabaseClient.auth.setSession({
      access_token: session.access_token,
      refresh_token: session.refresh_token,
    });

    if (error || !currentSession) {
      sessionStorage.removeItem('eva_session');
      return null;
    }

    sessionStorage.setItem('eva_session', JSON.stringify(currentSession));
    return currentSession;
  }

  const { data: { session } } = await supabaseClient.auth.getSession();
  if (session) {
    sessionStorage.setItem('eva_session', JSON.stringify(session));
    return session;
  }

  return null;
}

async function logoutUser() {
  await supabaseClient.auth.signOut();
  sessionStorage.removeItem('eva_session');
  window.location.href = 'login.html';
}
