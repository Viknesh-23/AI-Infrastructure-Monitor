(() => {
  const root = document.documentElement;
  const savedTheme = localStorage.getItem('infrasight-theme');
  const applyTheme = (theme) => {
    root.setAttribute('data-bs-theme', theme);
    localStorage.setItem('infrasight-theme', theme);
    document.querySelectorAll('#themeToggle i, #settingsThemeToggle i').forEach((icon) => {
      icon.className = theme === 'dark' ? 'bi bi-sun' : 'bi bi-moon-stars';
    });
  };
  applyTheme(savedTheme || 'light');
  const toggleTheme = () => applyTheme(root.getAttribute('data-bs-theme') === 'dark' ? 'light' : 'dark');
  document.getElementById('themeToggle')?.addEventListener('click', toggleTheme);
  document.getElementById('settingsThemeToggle')?.addEventListener('click', toggleTheme);
  document.getElementById('sidebarToggle')?.addEventListener('click', () => document.getElementById('sidebar')?.classList.toggle('open'));
  const notify = (message, variant = 'success') => {
    let tray = document.getElementById('toastTray');
    if (!tray) { tray = document.createElement('div'); tray.id = 'toastTray'; tray.className = 'toast-container position-fixed top-0 end-0 p-3'; document.body.append(tray); }
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-bg-${variant} border-0`;
    toast.setAttribute('role', 'status');
    const row = document.createElement('div');
    row.className = 'd-flex';
    const body = document.createElement('div');
    body.className = 'toast-body';
    body.textContent = message;
    const close = document.createElement('button');
    close.type = 'button';
    close.className = 'btn-close btn-close-white me-2 m-auto';
    close.dataset.bsDismiss = 'toast';
    close.setAttribute('aria-label', 'Close');
    row.append(body, close);
    toast.append(row);
    tray.append(toast);
    const instance = new bootstrap.Toast(toast, { delay: 2600 });
    toast.addEventListener('hidden.bs.toast', () => toast.remove());
    instance.show();
  };
  document.querySelectorAll('form[data-metric-action]').forEach((form) => form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const button = form.querySelector('button[type="submit"], button');
    const original = button.innerHTML;
    button.disabled = true;
    button.innerHTML = '<span class="spinner-border spinner-border-sm" aria-hidden="true"></span> Collecting';
    try {
      const response = await fetch(form.dataset.apiUrl, { method: 'POST', credentials: 'same-origin', headers: { Accept: 'application/json' } });
      const data = await response.json();
      if (!response.ok) throw new Error(data.message || 'Metric collection failed.');
      notify(`${data.message} Risk: ${data.metric.risk_score}%.`, data.incident ? 'danger' : 'success');
      window.setTimeout(() => window.location.reload(), 700);
    } catch (error) {
      notify(error.message || 'Metric collection failed. Please try again.', 'danger');
      button.disabled = false;
      button.innerHTML = original;
    }
  }));
  document.querySelectorAll('form').forEach((form) => form.addEventListener('submit', () => {
    const submit = form.querySelector('button[type="submit"]');
    if (submit && !submit.dataset.noLoading) { submit.classList.add('is-loading'); }
  }));
})();
