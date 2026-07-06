/**
 * Import Data — Bulk upload handling
 *
 * Manages file selection validation, confirmation modal,
 * and submission state for the bulk import page.
 */

document.addEventListener('DOMContentLoaded', function () {
    initImportModal();
});

function initImportModal() {
    const importBtn = document.getElementById('btnImport');
    const fileInput = document.getElementById('file');
    const modal = document.getElementById('importConfirmModal');
    if (!importBtn || !fileInput || !modal) return;

    // Show modal on click
    importBtn.addEventListener('click', function (e) {
        e.preventDefault();

        // Validate file selected
        if (!fileInput.files.length) {
            showToast('Silakan pilih file Excel atau CSV terlebih dahulu.', 'warning');
            return;
        }

        // Set modal body text
        const bodyEl = modal.querySelector('#importModalBody');
        const fileName = fileInput.files[0].name;
        if (bodyEl) {
            bodyEl.textContent = 'Import file "' + fileName + '"? Semua data akan divalidasi dan diprediksi otomatis oleh sistem SVM.';
        }

        // Show Bootstrap modal
        var bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    });

    // Handle confirm in modal
    const confirmBtn = modal.querySelector('#confirmImport');
    if (confirmBtn) {
        confirmBtn.addEventListener('click', function () {
            // Hide modal
            var bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) bsModal.hide();

            // Disable button & submit form
            importBtn.disabled = true;
            importBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Memproses...';

            // Submit the parent form
            const form = importBtn.closest('form');
            if (form) form.submit();
        });
    }
}

/**
 * Simple toast notification using Bootstrap alerts.
 * Falls back to a flash-style banner if no toast container exists.
 */
function showToast(message, type) {
    type = type || 'danger';
    // Reuse the flash container at top of main content
    var container = document.querySelector('.container-fluid.p-0.mb-4');
    if (!container) {
        alert(message);
        return;
    }
    var alertHtml =
        '<div class="alert alert-' + type + ' alert-dismissible fade show small py-2 px-3 mb-0" role="alert">' +
        message +
        '<button type="button" class="btn-close py-2" data-bs-dismiss="alert" aria-label="Close"></button>' +
        '</div>';
    container.innerHTML = alertHtml + container.innerHTML;

    // Auto-dismiss after 5 seconds
    setTimeout(function () {
        var alerts = container.querySelectorAll('.alert');
        if (alerts.length > 0) {
            var bsAlert = new bootstrap.Alert(alerts[0]);
            bsAlert.close();
        }
    }, 5000);
}
