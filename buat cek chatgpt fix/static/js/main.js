function toggleTheme() {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    // Update DOM
    html.setAttribute('data-theme', newTheme);
    
    // Update icon
    const themeIcon = document.getElementById('themeIcon');
    themeIcon.className = newTheme === 'light' ? 'bi bi-sun-fill' : 'bi bi-moon-fill';
    
    // Simpan preferensi di localStorage
    localStorage.setItem('theme', newTheme);
}

// Set tema awal berdasarkan localStorage atau default ke dark
document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    const html = document.documentElement;
    html.setAttribute('data-theme', savedTheme);
    
    const themeIcon = document.getElementById('themeIcon');
    themeIcon.className = savedTheme === 'light' ? 'bi bi-sun-fill' : 'bi bi-moon-fill';
});
