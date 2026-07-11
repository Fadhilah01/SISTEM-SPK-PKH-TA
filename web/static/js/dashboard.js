/**
 * SPK PKH - Dashboard Dynamic Analytics & Visualization (Chart.js)
 * 
 * Melayani:
 *   1. Doughnut Chart kelayakan global statis pada inisialisasi (Monokrom)
 *   2. Paginasi client-side hasil keputusan terbaru
 */

document.addEventListener('DOMContentLoaded', function () {
    // Inisialisasi Doughnut Chart Kelayakan Global
    initKelayakanChart();

    // Inisialisasi Paginasi Client-Side
    initRecentPaginator();
});

function getThemeColors() {
    const style = getComputedStyle(document.documentElement);
    const isDark = document.documentElement.getAttribute('data-bs-theme') === 'dark';
    
    return {
        isDark: isDark,
        primaryColor: style.getPropertyValue('--color-primary').trim() || '#09090b',
        secondaryColor: style.getPropertyValue('--color-text-muted').trim() || '#71717a',
        borderColor: style.getPropertyValue('--color-border').trim() || '#e4e4e7',
        textColor: isDark ? '#a1a1aa' : '#71717a',
        gridColor: isDark ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)'
    };
}

function initKelayakanChart() {
    const canvasKelayakan = document.getElementById('chartKelayakan');
    if (!canvasKelayakan) return;

    const layak = Number(canvasKelayakan.dataset.layak) || 0;
    const tidak = Number(canvasKelayakan.dataset.tidak) || 0;

    const colors = getThemeColors();

    const ctx = canvasKelayakan.getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Layak', 'Tidak Layak'],
            datasets: [{
                data: [layak, tidak],
                backgroundColor: [colors.primaryColor, colors.secondaryColor],
                borderColor: colors.borderColor,
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        font: { family: 'Inter', size: 12, weight: '500' },
                        color: colors.textColor,
                        padding: 10,
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                }
            },
            cutout: '70%'
        }
    });
}

function initRecentPaginator() {
    const rows = document.querySelectorAll(".recent-row");
    const paginatorInfo = document.getElementById("paginator-info");
    const btnPrev = document.getElementById("btn-prev-page");
    const btnNext = document.getElementById("btn-next-page");

    if (rows.length === 0 || !paginatorInfo) return;

    let currentPage = 1;
    const totalPages = Math.ceil(rows.length / 3);

    function showPage(page) {
        rows.forEach(row => {
            const rowPage = parseInt(row.dataset.page);
            if (rowPage === page) {
                row.classList.remove("d-none");
            } else {
                row.classList.add("d-none");
            }
        });
        paginatorInfo.textContent = `Halaman ${page} dari ${totalPages}`;
        btnPrev.disabled = (page === 1);
        btnNext.disabled = (page === totalPages);
    }

    btnPrev.addEventListener("click", function () {
        if (currentPage > 1) {
            currentPage--;
            showPage(currentPage);
        }
    });

    btnNext.addEventListener("click", function () {
        if (currentPage < totalPages) {
            currentPage++;
            showPage(currentPage);
        }
    });

    showPage(currentPage);
}

