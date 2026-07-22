/* ════════════════════════════════════════════════════════════════════════
   Zenvyrolabs Voice Studio – Global JS
   ════════════════════════════════════════════════════════════════════════ */

'use strict';

// ── Theme ──────────────────────────────────────────────────────────────
const THEME_KEY = 'zv-theme';

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  const btn = document.getElementById('themeToggle');
  if (btn) {
    btn.querySelector('i').className = theme === 'light'
      ? 'bi bi-sun'
      : 'bi bi-moon-stars';
  }
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme') || 'dark';
  const next    = current === 'dark' ? 'light' : 'dark';
  localStorage.setItem(THEME_KEY, next);
  applyTheme(next);
}

(function initTheme() {
  const saved = localStorage.getItem(THEME_KEY) || 'dark';
  applyTheme(saved);
})();

// ── Sidebar ─────────────────────────────────────────────────────────────
(function initSidebar() {
  const sidebar     = document.getElementById('sidebar');
  const wrapper     = document.getElementById('mainWrapper');
  const toggleBtn   = document.getElementById('sidebarToggle');
  if (!sidebar || !toggleBtn) return;

  function isMobile() { return window.innerWidth <= 768; }

  toggleBtn.addEventListener('click', () => {
    if (isMobile()) {
      sidebar.classList.toggle('mobile-open');
    } else {
      sidebar.classList.toggle('collapsed');
      wrapper.classList.toggle('sidebar-collapsed');
      localStorage.setItem('zv-sidebar', sidebar.classList.contains('collapsed') ? '1' : '0');
    }
  });

  // Restore on desktop
  if (!isMobile() && localStorage.getItem('zv-sidebar') === '1') {
    sidebar.classList.add('collapsed');
    wrapper.classList.add('sidebar-collapsed');
  }
})();

document.getElementById('themeToggle')?.addEventListener('click', toggleTheme);

// ── Toasts ──────────────────────────────────────────────────────────────
function showToast(title, msg = '', type = 'info', duration = 4000) {
  const container = document.getElementById('toastStack');
  if (!container) return;

  const icons = { success: 'bi-check-circle-fill', error: 'bi-x-circle-fill', info: 'bi-info-circle-fill' };
  const icon  = icons[type] || icons.info;

  const el = document.createElement('div');
  el.className = `toast-item ${type}`;
  el.innerHTML = `
    <i class="bi ${icon} ti-icon"></i>
    <div class="ti-body">
      <div class="ti-title">${title}</div>
      ${msg ? `<div class="ti-msg">${msg}</div>` : ''}
    </div>`;

  container.appendChild(el);

  setTimeout(() => {
    el.classList.add('out');
    el.addEventListener('animationend', () => el.remove());
  }, duration);
}

// ── Loading Overlay ──────────────────────────────────────────────────────
function showLoading(msg = 'Processing…') {
  const ov = document.getElementById('loadingOverlay');
  const lt = document.getElementById('loadingText');
  if (!ov) return;
  if (lt) lt.textContent = msg;
  ov.classList.add('active');
}
function hideLoading() {
  document.getElementById('loadingOverlay')?.classList.remove('active');
}

// ── Log Console ──────────────────────────────────────────────────────────
function appendLog(consoleEl, text, type = '') {
  if (!consoleEl) return;
  const line = document.createElement('span');
  if (type) line.className = `log-${type}`;
  line.textContent = text + '\n';
  consoleEl.appendChild(line);
  consoleEl.scrollTop = consoleEl.scrollHeight;
}

function clearLog(consoleEl) {
  if (consoleEl) consoleEl.innerHTML = '';
}

function logFromEntries(consoleEl, entries) {
  if (!consoleEl || !entries) return;
  entries.forEach(e => {
    const map = { success: 'success', error: 'error', warning: 'warning', info: 'info' };
    appendLog(consoleEl, e.message || e, map[e.level] || '');
  });
}

// ── Progress Helpers ────────────────────────────────────────────────────
function setProgress(barEl, pct) {
  if (!barEl) return;
  barEl.style.width = `${Math.min(100, Math.max(0, pct))}%`;
  barEl.setAttribute('aria-valuenow', pct);
}

// ── Drag-and-drop Upload Zone ────────────────────────────────────────────
function initDropZone(zone, inputEl, onFiles) {
  if (!zone) return;

  zone.addEventListener('click', () => inputEl && inputEl.click());

  zone.addEventListener('dragover', e => {
    e.preventDefault();
    zone.classList.add('dragover');
  });
  zone.addEventListener('dragleave', () => zone.classList.remove('dragover'));
  zone.addEventListener('drop', e => {
    e.preventDefault();
    zone.classList.remove('dragover');
    const files = Array.from(e.dataTransfer.files);
    if (onFiles) onFiles(files);
  });

  if (inputEl) {
    inputEl.addEventListener('change', () => {
      const files = Array.from(inputEl.files || []);
      if (onFiles) onFiles(files);
    });
  }
}

// ── API helper ───────────────────────────────────────────────────────────
async function apiPost(url, formData, onProgress) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open('POST', url);

    if (onProgress) {
      xhr.upload.addEventListener('progress', e => {
        if (e.lengthComputable) onProgress(e.loaded / e.total);
      });
    }

    xhr.onload = () => {
      try {
        resolve(JSON.parse(xhr.responseText));
      } catch {
        reject(new Error('Invalid JSON response'));
      }
    };
    xhr.onerror = () => reject(new Error('Network error'));
    xhr.send(formData);
  });
}

async function apiGet(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return r.json();
}

async function apiPostJSON(url, data) {
  const r = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return r.json();
}

// ── Format helpers ───────────────────────────────────────────────────────
function formatBytes(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function formatDuration(secs) {
  if (secs < 60) return `${Math.round(secs)}s`;
  const m = Math.floor(secs / 60);
  const s = Math.round(secs % 60);
  return `${m}m ${s}s`;
}

// ── Expose globals ───────────────────────────────────────────────────────
window.ZV = {
  showToast, showLoading, hideLoading,
  appendLog, clearLog, logFromEntries, setProgress,
  initDropZone, apiPost, apiGet, apiPostJSON,
  formatBytes, formatDuration,
};
