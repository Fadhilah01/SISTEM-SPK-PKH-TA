/**
 * Export Data — Filter controls & form handling
 *
 * Manages quick date range buttons, select/deselect all columns,
 * form validation with Bootstrap modal, and submission state.
 */

document.addEventListener('DOMContentLoaded', function () {
    initDateRangeButtons();
    initColumnSelectors();
    initExportForm();
});

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
    var exportBtn = document.getElementById('btnExport');
    if (!exportBtn) return;

    exportBtn.addEventListener('click', function (e) {
        var checked = document.querySelectorAll('.column-checkbox:checked');
        if (checked.length === 0) {
            e.preventDefault();
            // Show Bootstrap modal warning
            var warningModal = new bootstrap.Modal(document.getElementById('exportWarningModal'));
            warningModal.show();
            return;
        }

        // Disable button to prevent double click
        this.disabled = true;
        this.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Memproses Export...';
    });
}
