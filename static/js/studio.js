/* Zenvyrolabs Voice Studio - Global JavaScript */

// Sidebar Toggle
(function () {
  var sidebar = document.getElementById('sidebar');
  var toggle  = document.getElementById('sidebarToggle');
  if (toggle && sidebar) {
    toggle.addEventListener('click', function () { sidebar.classList.toggle('open'); });
    document.addEventListener('click', function (e) {
      if (window.innerWidth <= 768 && sidebar.classList.contains('open') &&
          !sidebar.contains(e.target) && e.target !== toggle) {
        sidebar.classList.remove('open');
      }
    });
  }
})();

// Toast Notifications
function showToast(message, type, duration) {
  type     = type     || 'info';
  duration = duration || 4000;
  var icons = {
    success: '<i class="bi bi-check-circle-fill text-success"></i>',
    error:   '<i class="bi bi-x-circle-fill text-danger"></i>',
    warning: '<i class="bi bi-exclamation-triangle-fill text-warning"></i>',
    info:    '<i class="bi bi-info-circle-fill text-info"></i>'
  };
  var container = document.getElementById('toastContainer');
  if (!container) return;
  var toast = document.createElement('div');
  toast.className = 'toast-item toast-' + type;
  toast.innerHTML = (icons[type] || '') + '<span>' + message + '</span>';
  container.appendChild(toast);
  setTimeout(function () {
    toast.style.opacity   = '0';
    toast.style.transform = 'translateX(20px)';
    toast.style.transition = 'all 0.3s';
    setTimeout(function () { if (toast.parentNode) toast.remove(); }, 300);
  }, duration);
}

// Loading Overlay
function showLoading(text) {
  text = text || 'Processing...';
  var overlay = document.getElementById('loadingOverlay');
  var textEl  = document.getElementById('loadingText');
  if (overlay) overlay.style.display = 'flex';
  if (textEl)  textEl.textContent = text;
}

function hideLoading() {
  var overlay = document.getElementById('loadingOverlay');
  if (overlay) overlay.style.display = 'none';
}

window.showToast   = showToast;
window.showLoading = showLoading;
window.hideLoading = hideLoading;
