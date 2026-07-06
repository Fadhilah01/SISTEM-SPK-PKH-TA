/**
 * SPK PKH - App Shell: Sidebar Toggle & DOM Utilities
 *
 * Handles responsive sidebar drawer behavior, theme detection,
 * and shared UI interactions.
 */

document.addEventListener('DOMContentLoaded', function () {
    initSidebar();
});

function initSidebar() {
    const toggleBtn = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebarPanel');
    const overlay = document.getElementById('sidebarOverlay');
    const closeBtn = document.getElementById('sidebarClose');

    if (!sidebar) return; // No sidebar on this page

    if (toggleBtn && overlay) {
        toggleBtn.addEventListener('click', function () {
            sidebar.classList.add('show');
            overlay.classList.add('show');
        });

        var closeSidebar = function () {
            sidebar.classList.remove('show');
            overlay.classList.remove('show');
        };

        overlay.addEventListener('click', closeSidebar);
        if (closeBtn) {
            closeBtn.addEventListener('click', closeSidebar);
        }
    }
}
