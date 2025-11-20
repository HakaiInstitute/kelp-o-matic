// Make the site name text in header clickable and navigate to home
document.addEventListener('DOMContentLoaded', function() {
  const headerTitleText = document.querySelector('.md-header__title .md-header__ellipsis .md-header__topic');
  if (headerTitleText) {
    headerTitleText.addEventListener('click', function() {
      // Navigate to the site root
      const logo = document.querySelector('.md-header__button.md-logo');
      window.location.href = logo ? logo.href : '/';
    });
  }
});
