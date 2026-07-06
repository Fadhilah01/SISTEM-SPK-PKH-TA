/**
 * SPK PKH - Dashboard Charts (Chart.js)
 *
 * Initialises:
 *   1. Doughnut chart  — Persentase Kelayakan Bantuan (Layak / Tidak Layak)
 *   2. Bar chart       — Distribusi Calon per Desa
 *
 * Data is read from data-* attributes on the <canvas> elements,
 * so the same script works without extra API calls or global variables.
 */

document.addEventListener('DOMContentLoaded', function () {
    initDashboardCharts();
});

function initDashboardCharts() {
    var canvasKelayakan = document.getElementById('chartKelayakan');
    var canvasDesa = document.getElementById('chartDesa');

    if (!canvasKelayakan || !canvasDesa) return;

    /* ── Read data from data-* attributes ── */
    var layak = Number(canvasKelayakan.dataset.layak) || 0;
    var tidak = Number(canvasKelayakan.dataset.tidak) || 0;

    var labels = [];
    var values = [];
    try {
        labels = JSON.parse(canvasDesa.getAttribute('data-labels') || '[]');
        values = JSON.parse(canvasDesa.getAttribute('data-values') || '[]').map(Number);
    } catch (e) {
        console.error("Error parsing dynamic desa_stats:", e);
    }

    /* ── Dark-mode-aware colour palette ── */
    var isDark = document.documentElement.getAttribute('data-bs-theme') === 'dark';
    var textColor = isDark ? '#a1a1aa' : '#71717a';
    var primaryColor = isDark ? '#f4f4f5' : '#09090b';
    var secondaryColor = isDark ? '#27272a' : '#e4e4e7';
    var gridColor = isDark ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)';
    var borderColor = isDark ? '#121214' : '#ffffff';

    /* ── Chart 1: Doughnut — Persentase Kelayakan ── */
    var ctx1 = canvasKelayakan.getContext('2d');
    new Chart(ctx1, {
        type: 'doughnut',
        data: {
            labels: ['Layak', 'Tidak Layak'],
            datasets: [{
                data: [layak, tidak],
                backgroundColor: [primaryColor, secondaryColor],
                borderColor: borderColor,
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
                        color: textColor,
                        padding: 15,
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                }
            },
            cutout: '72%'
        }
    });

    /* ── Chart 2: Bar — Distribusi per Desa ── */
    var ctx2 = canvasDesa.getContext('2d');
    new Chart(ctx2, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Calon Penerima',
                data: values,
                backgroundColor: primaryColor,
                borderRadius: 6,
                barThickness: 28
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: {
                        font: { family: 'Inter', size: 11 },
                        color: textColor
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: { color: gridColor },
                    ticks: {
                        precision: 0,
                        font: { family: 'Inter', size: 11 },
                        color: textColor
                    }
                }
            }
        }
    });
}
