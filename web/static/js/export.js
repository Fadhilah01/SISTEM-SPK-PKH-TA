/**
 * Export Data — Filter controls & form handling
 *
 * Manages quick date range buttons, select/deselect all columns,
 * form validation with Bootstrap modal, and loading overlay.
 *
 * CATATAN: Jangan pernah men-disable tombol submit di event click!
 * Browser membatalkan form submission jika tombol submit di-disable
 * sebelum event submit sempat di-fire. Gunakan loading overlay sebagai gantinya.
 */

document.addEventListener('DOMContentLoaded', function () {
    initDateRangeButtons();
    initColumnSelectors();
    initExportForm();
    initCancelButton();
});

/**
 * Simpan URL redirect untuk tombol Batal.
 * Dibaca dari data attribute halaman agar tidak hardcode.
 */
function initCancelButton() {
    var batalBtn = document.querySelector('[data-cancel-url]');
    if (batalBtn) {
        window._cancelRedirectUrl = batalBtn.dataset.cancelUrl;
    }
}

function initDateRangeButtons() {
    document.querySelectorAll('.set-date-range').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var days = parseInt(this.dataset.days);
            var today = new Date();
            var past = new Date();
            past.setDate(today.getDate() - days);

            document.getElementById('dateFrom').value = past.toISOString().split('T')[0];
            document.getElementById('dateTo').value = today.toISOString().split('T')[0];
        });
    });

    var clearBtn = document.querySelector('.clear-date-range');
    if (clearBtn) {
        clearBtn.addEventListener('click', function () {
            document.getElementById('dateFrom').value = '';
            document.getElementById('dateTo').value = '';
        });
    }
}

function initColumnSelectors() {
    var selectAllBtn = document.querySelector('.select-all-columns');
    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', function () {
            document.querySelectorAll('.column-checkbox').forEach(function (cb) {
                cb.checked = true;
            });
        });
    }

    var clearAllBtn = document.querySelector('.clear-all-columns');
    if (clearAllBtn) {
        clearAllBtn.addEventListener('click', function () {
            document.querySelectorAll('.column-checkbox').forEach(function (cb) {
                cb.checked = false;
            });
        });
    }
}

function initExportForm() {
    var form = document.getElementById('exportForm');
    if (!form) return;

    form.addEventListener('submit', function (e) {
        var checked = document.querySelectorAll('.column-checkbox:checked');
        if (checked.length === 0) {
            e.preventDefault();
            var warningModal = new bootstrap.Modal(document.getElementById('exportWarningModal'));
            warningModal.show();
            return;
        }

        // JANGAN disable tombol submit — itu mencegah form submission!
        // Sebagai gantinya, tampilkan overlay loading.
        // Overlay akan otomatis hilang setelah download selesai
        // (atau user bisa klik overlay untuk menutupnya).
        showLoadingOverlay();
    });
}

/**
 * handleCancel — fungsi global untuk tombol Batal.
 * - Jika overlay loading sedang tampil, tutup saja overlay-nya.
 * - Jika tidak ada overlay, redirect ke daftar calon.
 */
function handleCancel() {
    var overlay = document.getElementById('exportLoadingOverlay');
    if (overlay) {
        overlay.remove();
    } else {
        window.location.href = window._cancelRedirectUrl || '/calon';
    }
}


function showLoadingOverlay() {
    // Cegah duplikasi overlay
    if (document.getElementById('exportLoadingOverlay')) return;

    var overlay = document.createElement('div');
    overlay.id = 'exportLoadingOverlay';
    overlay.style.cssText = [
        'position: fixed',
        'top: 0',
        'left: 0',
        'width: 100%',
        'height: 100%',
        'background: rgba(0, 0, 0, 0.5)',
        'z-index: 9999',
        'display: flex',
        'align-items: center',
        'justify-content: center',
    ].join(';');

    overlay.innerHTML = [
        '<div class="bg-white rounded-3 p-4 text-center shadow-lg" style="min-width: 280px;">',
        '  <div class="spinner-border text-primary mb-3" role="status"></div>',
        '  <p class="mb-1 fw-semibold">Sedang memproses export...</p>',
        '  <small class="text-muted">File akan terdownload secara otomatis.</small>',
        '  <hr>',
        '  <button type="button" class="btn btn-sm btn-outline-secondary" id="btnCloseOverlay">',
        '    Tutup (jika download sudah selesai)',
        '  </button>',
        '</div>',
    ].join('');

    document.body.appendChild(overlay);

    // Klik overlay (di luar card) untuk menutup
    overlay.addEventListener('click', function (e) {
        if (e.target === this) {
            this.remove();
        }
    });

    // Tombol tutup
    document.getElementById('btnCloseOverlay').addEventListener('click', function () {
        overlay.remove();
    });

    // Auto-hide setelah 15 detik (fallback — file kecil harusnya < 1 detik)
    setTimeout(function () {
        var el = document.getElementById('exportLoadingOverlay');
        if (el) el.remove();
    }, 15000);
}
