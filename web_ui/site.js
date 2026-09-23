const currentYear = document.getElementById('currentYear');
if (currentYear) currentYear.textContent = new Date().getFullYear();

const authAction = document.getElementById('authAction');
if (authAction && document.cookie.split('; ').includes('nsy_signed_in=1')) {
  authAction.classList.add('signed-in');
  if (document.body.dataset.page === 'projects') {
    authAction.textContent = 'Sign out';
    authAction.href = `https://dem.nsyprojects.com/logout?next=${encodeURIComponent(window.location.href)}`;
  } else {
    authAction.textContent = 'Signed in';
    authAction.href = '/projects.html';
  }
}
