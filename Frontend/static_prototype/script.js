document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('theme-toggle');
    const body = document.body;
    
    // Fonction pour basculer le thème
    function toggleTheme() {
        if (body.classList.contains('light-mode')) {
            body.classList.remove('light-mode');
            body.classList.add('dark-mode');
            themeToggle.innerHTML = '<i class="fas fa-sun"></i>'; // Icône Soleil pour retourner au clair
            localStorage.setItem('theme', 'dark');
        } else {
            body.classList.remove('dark-mode');
            body.classList.add('light-mode');
            themeToggle.innerHTML = '<i class="fas fa-moon"></i>'; // Icône Lune pour retourner au sombre
            localStorage.setItem('theme', 'light');
        }
    }

    // Chargement du thème préféré de l'utilisateur (depuis la dernière session)
    const storedTheme = localStorage.getItem('theme');
    if (storedTheme === 'dark') {
        body.classList.remove('light-mode');
        body.classList.add('dark-mode');
        themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
    } else {
        // S'assurer que le mode clair est par défaut si rien n'est stocké ou si 'light' est stocké
        body.classList.add('light-mode');
        themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
    }

    // Écouteur d'événement sur le bouton
    themeToggle.addEventListener('click', toggleTheme);
});
