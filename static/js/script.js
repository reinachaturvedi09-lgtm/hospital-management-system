/**
 * Hospital Management System - Custom JavaScript
 * Handles sidebar toggle, dark mode, and UI interactions.
 */

document.addEventListener('DOMContentLoaded', function () {

    /* ---------- Sidebar Toggle ---------- */
    const sidebar = document.getElementById('sidebar');
    const pageContent = document.getElementById('page-content-wrapper');
    const toggleBtn = document.getElementById('toggle-sidebar');

    if (toggleBtn && sidebar && pageContent) {
        toggleBtn.addEventListener('click', function () {
            sidebar.classList.toggle('collapsed');
            sidebar.classList.toggle('show');
            pageContent.classList.toggle('full-margin');
        });
    }

    /* ---------- Dark Mode Toggle ---------- */
    const darkModeBtn = document.getElementById('darkModeToggle');
    const body = document.body;

    // Load saved theme
    const savedTheme = localStorage.getItem('hms-theme');
    if (savedTheme === 'dark') {
        body.classList.add('dark-mode');
        updateDarkModeIcon(true);
    }

    if (darkModeBtn) {
        darkModeBtn.addEventListener('click', function () {
            body.classList.toggle('dark-mode');
            const isDark = body.classList.contains('dark-mode');
            localStorage.setItem('hms-theme', isDark ? 'dark' : 'light');
            updateDarkModeIcon(isDark);
        });
    }

    function updateDarkModeIcon(isDark) {
        if (!darkModeBtn) return;
        const icon = darkModeBtn.querySelector('i');
        if (icon) {
            icon.className = isDark ? 'bi bi-sun' : 'bi bi-moon';
        }
    }

    /* ---------- Password Toggle ---------- */
    const togglePassword = document.getElementById('togglePassword');
    if (togglePassword) {
        togglePassword.addEventListener('click', function () {
            const passwordInput = document.getElementById('password');
            if (passwordInput) {
                const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
                passwordInput.setAttribute('type', type);
                const icon = this.querySelector('i');
                icon.className = type === 'password' ? 'bi bi-eye' : 'bi bi-eye-slash';
            }
        });
    }

    /* ---------- Auto-dismiss Alerts ---------- */
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const closeBtn = alert.querySelector('.btn-close');
            if (closeBtn) {
                closeBtn.click();
            }
        }, 5000);
    });

    /* ---------- Confirm Delete Actions ---------- */
    const deleteForms = document.querySelectorAll('form[onsubmit*="confirm"]');
    deleteForms.forEach(function (form) {
        form.addEventListener('submit', function (e) {
            if (!confirm('Are you sure you want to delete this record? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });

});
