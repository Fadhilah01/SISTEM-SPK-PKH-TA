/**
 * Data Calon — Delete confirmation modal
 *
 * Handles the #hapusCalonModal Bootstrap modal for delete confirmations,
 * setting the form action from the triggering button's data attributes.
 */

document.addEventListener('DOMContentLoaded', function () {
    initHapusCalonModal();
});

function initHapusCalonModal() {
    var modal = document.getElementById('hapusCalonModal');
    if (!modal) return;

    modal.addEventListener('show.bs.modal', function (event) {
        var btn = event.relatedTarget;
        if (!btn) return;

        var id = btn.dataset.id;
        var nama = btn.dataset.nama;

        var bodyEl = modal.querySelector('#hapusCalonModalBody');
        var formEl = modal.querySelector('#hapusCalonForm');

        if (bodyEl) {
            bodyEl.textContent = 'Hapus data "' + nama + '"? Semua hasil keputusan untuk calon ini juga akan dihapus. Tindakan ini tidak dapat dibatalkan.';
        }
        if (formEl) {
            formEl.action = '/calon/' + id + '/hapus';
        }
    });
}
