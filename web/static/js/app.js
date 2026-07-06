/**
 * SPK PKH - App Shell: Sidebar Toggle, Password Toggle, Delete Modal
 *
 * Handles responsive sidebar drawer behavior, password visibility toggles,
 * and Bootstrap modal interactions for delete confirmations.
 */

document.addEventListener('DOMContentLoaded', function () {
    initSidebar();
    initPasswordToggles();
    initDeleteModal();
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

/**
 * Password Visibility Toggle
 * Adds click-to-toggle behavior on .password-toggle buttons.
 * Button must have data-target="elementId" pointing to the password input.
 */
function initPasswordToggles() {
    document.querySelectorAll('.password-toggle').forEach(function (btn) {
        btn.addEventListener('click', function () {
            const input = document.getElementById(this.dataset.target);
            const icon = this.querySelector('i');
            if (!input) return;

            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.replace('bi-eye', 'bi-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.replace('bi-eye-slash', 'bi-eye');
            }
        });
    });
}

/**
 * Delete Confirmation Modal
 * Handles the #hapusModal Bootstrap modal: sets form action and body text
 * from the triggering button's data-id and data-nama attributes.
 */
function initDeleteModal() {
    const modal = document.getElementById('hapusModal');
    if (!modal) return;

    modal.addEventListener('show.bs.modal', function (event) {
        const btn = event.relatedTarget;
        if (!btn) return;

        const id = btn.dataset.id;
        const nama = btn.dataset.nama;

        const bodyEl = modal.querySelector('#hapusModalBody');
        const formEl = modal.querySelector('#hapusForm');

        if (bodyEl) {
            bodyEl.textContent = 'Hapus akses admin untuk ' + nama + '? Tindakan ini tidak dapat dibatalkan.';
        }
        if (formEl) {
            formEl.action = '/admin/users/' + id + '/hapus';
        }
    });
}
