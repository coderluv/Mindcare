const API = window.location.origin;

function getToken() { return localStorage.getItem('mindcare_token'); }
function getUser()  { return JSON.parse(localStorage.getItem('mindcare_user') || '{}'); }
function setAuth(token, user) {
  localStorage.setItem('mindcare_token', token);
  localStorage.setItem('mindcare_user', JSON.stringify(user));
}
function clearAuth() {
  localStorage.removeItem('mindcare_token');
  localStorage.removeItem('mindcare_user');
}
function requireAuth() {
  if (!getToken()) { window.location.href = '/login'; return false; }
  return true;
}
function redirectIfLoggedIn() {
  if (getToken()) { window.location.href = '/dashboard'; }
}

async function apiFetch(path, options = {}) {
  const token = getToken();
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(API + path, { ...options, headers });
  if (res.status === 401) { clearAuth(); window.location.href = '/login'; return; }
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || 'Request failed');
  return data;
}

function showToast(msg, type = 'success', duration = 3000) {
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), duration);
}

function moodColor(score) {
  if (score >= 7) return '#34d399';
  if (score >= 5) return '#fbbf24';
  if (score >= 3) return '#f97316';
  return '#f87171';
}

function moodLabel(score) {
  if (score >= 8) return 'Great';
  if (score >= 6) return 'Good';
  if (score >= 4) return 'Okay';
  if (score >= 2) return 'Low';
  return 'Very low';
}

function formatDate(str) {
  return new Date(str).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
}
function formatTime(str) {
  return new Date(str).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
}
function timeAgo(str) {
  const diff = Date.now() - new Date(str).getTime();
  const m = Math.floor(diff / 60000);
  if (m < 1) return 'just now';
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h ago`;
  return `${Math.floor(h / 24)}d ago`;
}
