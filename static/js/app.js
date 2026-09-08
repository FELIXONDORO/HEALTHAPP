document.querySelectorAll('[data-menu-button]').forEach((button) => {
  button.addEventListener('click', () => {
    document.querySelector('.sidebar')?.classList.toggle('open');
  });
});
