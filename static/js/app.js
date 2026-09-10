document.querySelectorAll('[data-menu-button]').forEach((button) => {
  button.addEventListener('click', () => {
    document.querySelector('.sidebar')?.classList.toggle('open');
  });
});

const themeToggle = document.querySelector('[data-theme-toggle]');
const themeIcons = {
  light: '<svg class="theme-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M21 12.8A8.5 8.5 0 1 1 11.2 3 6.7 6.7 0 0 0 21 12.8Z"></path></svg>',
  dark: '<svg class="theme-icon" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"></circle><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"></path></svg>'
};

function updateThemeToggle(theme) {
  if (!themeToggle) return;
  const isDark = theme === 'dark';
  themeToggle.setAttribute('aria-label', isDark ? 'Switch to light theme' : 'Switch to dark theme');
  themeToggle.setAttribute('title', isDark ? 'Switch to light theme' : 'Switch to dark theme');
  themeToggle.innerHTML = themeIcons[isDark ? 'dark' : 'light'];
}

const activeTheme = document.documentElement.dataset.theme || 'light';
updateThemeToggle(activeTheme);

themeToggle?.addEventListener('click', () => {
  const nextTheme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
  document.documentElement.dataset.theme = nextTheme;
  try {
    localStorage.setItem('apex-homecare-theme', nextTheme);
  } catch (error) {
    // The current page still changes when browser storage is unavailable.
  }
  updateThemeToggle(nextTheme);
});
