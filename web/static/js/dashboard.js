/**
 * SPK PKH - Dashboard Dynamic Analytics & Visualization (Chart.js)
 * 
 * Melayani:
 *   1. Integrasi dengan global custom select dropdown (app.js) untuk filter spasial bertingkat
 *   2. Chart utama analitis dinamis via AJAX /api/analytics
 *   3. Doughnut Chart kelayakan global statis pada inisialisasi (Monokrom)
 *   4. Paginasi client-side hasil keputusan terbaru
 *   5. Kontrol filter dinamis dan monokromatik
 *   6. Penanganan status data kosong (UI placeholder text overlay)
 */

document.addEventListener('DOMContentLoaded', function () {
    // Inisialisasi Doughnut Chart Kelayakan Global
    initKelayakanChart();

    // Inisialisasi Analitik & Filter Interaktif
    initInteractiveAnalytics();

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

function initInteractiveAnalytics() {
    const selectProv = document.getElementById("select_provinsi");
    const selectKab = document.getElementById("select_kabupaten");
    const selectKec = document.getElementById("select_kecamatan");
    const selectDesa = document.getElementById("select_desa");

    if (!selectProv) return;

    // Set Default Dates untuk Komparasi Periode
    const today = new Date();
    const formatDate = (d) => d.toISOString().split('T')[0];
    const sixMonthsAgo = new Date();
    sixMonthsAgo.setMonth(today.getMonth() - 6);
    const twelveMonthsAgo = new Date();
    twelveMonthsAgo.setMonth(today.getMonth() - 12);

    document.getElementById("compare_a_start").value = formatDate(sixMonthsAgo);
    document.getElementById("compare_a_end").value = formatDate(today);
    document.getElementById("compare_b_start").value = formatDate(twelveMonthsAgo);
    document.getElementById("compare_b_end").value = formatDate(sixMonthsAgo);

    let mainChartInstance = null;

    // Fungsi untuk menyembunyikan/menampilkan filter secara dinamis sesuai tab aktif
    function adjustFilterVisibility(type) {
        document.querySelectorAll(".filter-spasial").forEach(el => el.classList.add("d-none"));
        document.querySelectorAll(".filter-tanggal").forEach(el => el.classList.add("d-none"));
        document.querySelectorAll(".filter-tren").forEach(el => el.classList.add("d-none"));
        document.querySelectorAll(".filter-komparasi").forEach(el => el.classList.add("d-none"));
        document.querySelectorAll(".filter-komparasi-period").forEach(el => el.classList.add("d-none"));
        document.querySelectorAll(".filter-komparasi-criteria").forEach(el => el.classList.add("d-none"));

        if (type === 'wilayah') {
            document.querySelectorAll(".filter-spasial").forEach(el => el.classList.remove("d-none"));
            document.querySelectorAll(".filter-tanggal").forEach(el => el.classList.remove("d-none"));
        } else if (type === 'tren') {
            document.querySelectorAll(".filter-tren").forEach(el => el.classList.remove("d-none"));
            document.querySelectorAll(".filter-tanggal").forEach(el => el.classList.remove("d-none"));
        } else if (type === 'komparasi') {
            document.querySelectorAll(".filter-komparasi").forEach(el => el.classList.remove("d-none"));
            const mode = document.getElementById("compare_mode").value;
            if (mode === 'period') {
                document.querySelectorAll(".filter-komparasi-period").forEach(el => el.classList.remove("d-none"));
            } else {
                document.querySelectorAll(".filter-komparasi-criteria").forEach(el => el.classList.remove("d-none"));
            }
        }
    }

    // Fungsi pemuatan chart utama
    function updateCharts() {
        const activeTab = document.querySelector("#analyticsTabs button.active");
        if (!activeTab) return;
        const chartType = activeTab.dataset.type; // wilayah, tren, komparasi

        const provVal = selectProv ? selectProv.value : "";
        const kabVal = selectKab ? selectKab.value : "";
        const kecVal = selectKec ? selectKec.value : "";
        const desaVal = selectDesa ? selectDesa.value : "";
        
        const dateFrom = document.getElementById("filter_date_from").value;
        const dateTo = document.getElementById("filter_date_to").value;

        let url = `/api/analytics?type=${chartType}&provinsi=${encodeURIComponent(provVal)}&kabupaten=${encodeURIComponent(kabVal)}&kecamatan=${encodeURIComponent(kecVal)}&desa_kelurahan=${encodeURIComponent(desaVal)}&date_from=${dateFrom}&date_to=${dateTo}`;

        if (chartType === 'tren') {
            const scale = document.getElementById("filter_scale").value;
            url += `&scale=${scale}`;
        } else if (chartType === 'komparasi') {
            const mode = document.getElementById("compare_mode").value;
            url += `&compare=${mode}`;
            if (mode === 'period') {
                const aStart = document.getElementById("compare_a_start").value;
                const aEnd = document.getElementById("compare_a_end").value;
                const bStart = document.getElementById("compare_b_start").value;
                const bEnd = document.getElementById("compare_b_end").value;
                url += `&period_a_start=${aStart}&period_a_end=${aEnd}&period_b_start=${bStart}&period_b_end=${bEnd}`;
            } else {
                const critType = document.getElementById("compare_criteria_type").value;
                url += `&criteria_type=${critType}`;
            }
        }

        fetch(url)
            .then(res => res.json())
            .then(data => {
                renderMainChart(chartType, data);
            })
            .catch(err => console.error("Error loading analytics data: ", err));
    }

    function renderMainChart(type, data) {
        const canvas = document.getElementById("mainChart");
        const placeholder = document.getElementById("chartPlaceholder");
        if (!canvas) return;

        // Cek apakah data kosong untuk menampilkan placeholder UI
        const hasData = (data.values && data.values.length > 0 && data.values.some(v => v > 0)) ||
                        (data.values_a && data.values_a.length > 0 && data.values_a.some(v => v > 0)) ||
                        (data.values_b && data.values_b.length > 0 && data.values_b.some(v => v > 0));

        if (!hasData) {
            canvas.style.display = "none";
            if (placeholder) placeholder.classList.remove("d-none");
            if (mainChartInstance) {
                mainChartInstance.destroy();
                mainChartInstance = null;
            }
            return;
        } else {
            canvas.style.display = "block";
            if (placeholder) placeholder.classList.add("d-none");
        }

        if (mainChartInstance) {
            mainChartInstance.destroy();
        }

        const colors = getThemeColors();
        let chartConfig = {};

        if (type === 'wilayah') {
            chartConfig = {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Calon Penerima',
                        data: data.values,
                        backgroundColor: colors.primaryColor,
                        borderRadius: 6,
                        barThickness: data.labels.length > 5 ? 24 : 35
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        title: { display: true, text: data.title, color: colors.textColor, font: { family: 'Inter', size: 13, weight: 'bold' } }
                    },
                    scales: {
                        x: { ticks: { color: colors.textColor, font: { family: 'Inter', size: 10 } }, grid: { display: false } },
                        y: { beginAtZero: true, ticks: { precision: 0, color: colors.textColor, font: { family: 'Inter', size: 10 } }, grid: { color: colors.gridColor } }
                    }
                }
            };
        } else if (type === 'tren') {
            chartConfig = {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Registrasi Calon',
                        data: data.values,
                        borderColor: colors.primaryColor,
                        backgroundColor: colors.isDark ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.03)',
                        fill: true,
                        tension: 0.25,
                        pointRadius: 4,
                        pointBackgroundColor: colors.primaryColor
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        title: { display: true, text: data.title, color: colors.textColor, font: { family: 'Inter', size: 13, weight: 'bold' } }
                    },
                    scales: {
                        x: { ticks: { color: colors.textColor, font: { family: 'Inter', size: 10 } }, grid: { display: false } },
                        y: { beginAtZero: true, ticks: { precision: 0, color: colors.textColor, font: { family: 'Inter', size: 10 } }, grid: { color: colors.gridColor } }
                    }
                }
            };
        } else if (type === 'komparasi') {
            const mode = document.getElementById("compare_mode").value;
            if (mode === 'period') {
                chartConfig = {
                    type: 'bar',
                    data: {
                        labels: data.labels,
                        datasets: [
                            {
                                label: data.label_a,
                                data: data.values_a,
                                backgroundColor: colors.primaryColor,
                                borderRadius: 4,
                                barThickness: 30
                            },
                            {
                                label: data.label_b,
                                data: data.values_b,
                                backgroundColor: colors.secondaryColor,
                                borderRadius: 4,
                                barThickness: 30
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: true, position: 'bottom', labels: { color: colors.textColor, font: { family: 'Inter', size: 11 } } },
                            title: { display: true, text: data.title, color: colors.textColor, font: { family: 'Inter', size: 13, weight: 'bold' } }
                        },
                        scales: {
                            x: { ticks: { color: colors.textColor, font: { family: 'Inter', size: 10 } }, grid: { display: false } },
                            y: { beginAtZero: true, ticks: { precision: 0, color: colors.textColor, font: { family: 'Inter', size: 10 } }, grid: { color: colors.gridColor } }
                        }
                    }
                };
            } else { // criteria
                chartConfig = {
                    type: 'bar',
                    data: {
                        labels: data.labels,
                        datasets: [{
                            label: 'Jumlah Calon',
                            data: data.values,
                            backgroundColor: colors.primaryColor,
                            borderRadius: 6,
                            barThickness: 28
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: false },
                            title: { display: true, text: data.title, color: colors.textColor, font: { family: 'Inter', size: 13, weight: 'bold' } }
                        },
                        scales: {
                            x: { ticks: { color: colors.textColor, font: { family: 'Inter', size: 10 } }, grid: { display: false } },
                            y: { beginAtZero: true, ticks: { precision: 0, color: colors.textColor, font: { family: 'Inter', size: 10 } }, grid: { color: colors.gridColor } }
                        }
                    }
                };
            }
        }

        const ctx = canvas.getContext('2d');
        mainChartInstance = new Chart(ctx, chartConfig);
    }

    // Pemuatan instansi dropdown bertingkat kustom menggunakan event listener global
    selectProv.addEventListener("change", function(e) {
        const val = e.detail.value;
        const kode = e.detail.kode;

        selectKab.disable(true);
        selectKec.disable(true);
        selectDesa.disable(true);
        
        if (!kode) {
            updateCharts();
            return;
        }
        
        fetch(`/api/daerah?level=kabupaten&parent=${kode}`)
            .then(res => res.json())
            .then(data => {
                selectKab.disable(false);
                selectKab.setItems(data);
                updateCharts();
            });
    });

    selectKab.addEventListener("change", function(e) {
        const val = e.detail.value;
        const kode = e.detail.kode;

        selectKec.disable(true);
        selectDesa.disable(true);
        
        if (!kode) {
            updateCharts();
            return;
        }
        
        fetch(`/api/daerah?level=kecamatan&parent=${kode}`)
            .then(res => res.json())
            .then(data => {
                selectKec.disable(false);
                selectKec.setItems(data);
                updateCharts();
            });
    });

    selectKec.addEventListener("change", function(e) {
        const val = e.detail.value;
        const kode = e.detail.kode;

        selectDesa.disable(true);
        
        if (!kode) {
            updateCharts();
            return;
        }
        
        fetch(`/api/daerah?level=desa&parent=${kode}`)
            .then(res => res.json())
            .then(data => {
                selectDesa.disable(false);
                selectDesa.setItems(data);
                updateCharts();
            });
    });

    selectDesa.addEventListener("change", updateCharts);

    // Ambil data provinsi untuk inisialisasi dropdown pertama
    fetch("/api/daerah?level=provinsi")
        .then(res => res.json())
        .then(data => {
            selectProv.setItems(data);
            
            // Atur visibilitas filter kontrol awal
            adjustFilterVisibility('wilayah');
            
            // Render chart pertama kali
            updateCharts();
        });

    // Event listener untuk Date Inputs global
    document.getElementById("filter_date_from").addEventListener("change", updateCharts);
    document.getElementById("filter_date_to").addEventListener("change", updateCharts);

    // Event listener untuk Tab Switching
    const tabs = document.querySelectorAll('#analyticsTabs button');
    tabs.forEach(tab => {
        tab.addEventListener('shown.bs.tab', function (e) {
            const type = e.target.dataset.type;
            
            // Sesuaikan visibilitas filter kontrol
            adjustFilterVisibility(type);

            updateCharts();
        });
    });

    // Event listener untuk Opsi Tren
    document.getElementById("filter_scale").addEventListener("change", updateCharts);

    // Event listener untuk Opsi Komparasi
    document.getElementById("compare_mode").addEventListener("change", function () {
        const mode = this.value;
        adjustFilterVisibility('komparasi');
        updateCharts();
    });

    document.getElementById("compare_criteria_type").addEventListener("change", updateCharts);
    
    // Perbandingan tanggal periode
    document.getElementById("compare_a_start").addEventListener("change", updateCharts);
    document.getElementById("compare_a_end").addEventListener("change", updateCharts);
    document.getElementById("compare_b_start").addEventListener("change", updateCharts);
    document.getElementById("compare_b_end").addEventListener("change", updateCharts);
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
