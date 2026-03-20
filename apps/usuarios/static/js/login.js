/* * Archivo: login.js
 * Lógica interactiva para la pantalla de inicio de sesión
 */

document.addEventListener('DOMContentLoaded', function() {
    const togglePassword = document.getElementById('togglePassword');
    const passwordInput = document.getElementById('password');
    const toggleIcon = document.getElementById('toggleIcon');

    if (togglePassword && passwordInput) {
        togglePassword.addEventListener('click', function() {
            // Cambiamos el tipo de input (de password a texto o viceversa)
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);

            // Cambiamos el icono (ojo normal vs ojo tachado)
            if (type === 'text') {
                toggleIcon.classList.remove('bi-eye');
                toggleIcon.classList.add('bi-eye-slash');
                togglePassword.classList.add('text-primary'); // Feedback visual activo
                togglePassword.classList.remove('text-muted');
            } else {
                toggleIcon.classList.remove('bi-eye-slash');
                toggleIcon.classList.add('bi-eye');
                togglePassword.classList.remove('text-primary');
                togglePassword.classList.add('text-muted'); // Vuelve a estado inactivo
            }
        });
    }
});