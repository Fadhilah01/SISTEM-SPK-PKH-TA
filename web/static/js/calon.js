/**
 * Handler Autocomplete Pencarian Wilayah Administratif
 */
document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById("wilayah_search");
    const suggestionsContainer = document.getElementById("wilayah_suggestions");
    const hiddenProvinsi = document.getElementById("hidden_provinsi");
    const hiddenKabupaten = document.getElementById("hidden_kabupaten");
    const hiddenKecamatan = document.getElementById("hidden_kecamatan");
    const hiddenDesa = document.getElementById("hidden_desa_kelurahan");

    if (!searchInput || !suggestionsContainer) return;

    let debounceTimer;

    // input event listener
    searchInput.addEventListener("input", function () {
        clearTimeout(debounceTimer);
        const query = searchInput.value.trim();

        if (query.length < 2) {
            suggestionsContainer.innerHTML = "";
            suggestionsContainer.style.display = "none";
            return;
        }

        debounceTimer = setTimeout(() => {
            fetch(`/api/daerah?q=${encodeURIComponent(query)}`)
                .then(response => {
                    if (!response.ok) throw new Error("Network response was not ok");
                    return response.json();
                })
                .then(data => {
                    suggestionsContainer.innerHTML = "";

                    if (data.length === 0) {
                        const noResult = document.createElement("div");
                        noResult.className = "dropdown-item text-muted small py-2";
                        noResult.innerHTML = "<i class='bi bi-info-circle'></i> Wilayah tidak ditemukan";
                        suggestionsContainer.appendChild(noResult);
                        suggestionsContainer.style.display = "block";
                        return;
                    }

                    // Loop data daerah (kode: "72.08.08.2001", nama: "POSONA", level: "desa")
                    data.forEach(item => {
                        // Hanya tampilkan jika levelnya adalah desa atau kecamatan/kabupaten
                        // Tapi autocomplete biasanya mencari hingga level desa agar spesifik
                        const btn = document.createElement("button");
                        btn.className = "dropdown-item text-start py-2 border-bottom border-light border-opacity-10";
                        btn.type = "button";

                        // Parse info bertingkat dari item.nama
                        // Teks label suggestion dibuat cantik, misal: "POSONA (Desa) - KASIMBAR, PARIGI MOUTONG"
                        // Kita bisa reconstruct dari kode wilayah
                        let labelText = `${item.nama} (${item.level.toUpperCase()})`;

                        btn.innerHTML = `
                            <div class="fw-semibold text-dark-emphasis">${item.fullname || item.nama}</div>
                            <div class="text-muted" style="font-size: 0.75rem;">
                                <i class="bi bi-geo-alt"></i> Kode: ${item.kode} | Tingkat: ${item.level.toUpperCase()}
                            </div>
                        `;

                        btn.addEventListener("click", function () {
                            // User klik suggestion, kita lakukan fetch data detail silsilah wilayah ke atas
                            // Caranya: panggil API daerah dengan menyaring kode parent-nya
                            // Atau karena data flat, kita bisa hit secara rekursif atau parsing dari kodenya!
                            // Kode wilayah Kemendagri:
                            // Provinsi: XX (2 digit)
                            // Kabupaten: XX.XX (5 digit)
                            // Kecamatan: XX.XX.XX (8 digit)
                            // Desa: XX.XX.XX.XXXX (13 digit)

                            const parts = item.kode.split('.');

                            // Siapkan loader
                            hiddenProvinsi.value = "";
                            hiddenKabupaten.value = "";
                            hiddenKecamatan.value = "";
                            hiddenDesa.value = "";

                            const provCode = parts[0];
                            const kabCode = parts.length >= 2 ? parts.slice(0, 2).join('.') : null;
                            const kecCode = parts.length >= 3 ? parts.slice(0, 3).join('.') : null;

                            // Fetch informasi lengkap silsilah untuk mengisi 4 hidden field
                            const fetchPromises = [];

                            if (provCode) {
                                fetchPromises.push(
                                    fetch(`/api/daerah?level=provinsi`)
                                        .then(r => r.json())
                                        .then(list => {
                                            const match = list.find(x => x.kode === provCode);
                                            if (match) hiddenProvinsi.value = match.nama;
                                        })
                                );
                            }
                            if (kabCode && parts.length >= 2) {
                                fetchPromises.push(
                                    fetch(`/api/daerah?parent=${provCode}&level=kabupaten`)
                                        .then(r => r.json())
                                        .then(list => {
                                            const match = list.find(x => x.kode === kabCode);
                                            if (match) hiddenKabupaten.value = match.nama;
                                        })
                                );
                            }
                            if (kecCode && parts.length >= 3) {
                                fetchPromises.push(
                                    fetch(`/api/daerah?parent=${kabCode}&level=kecamatan`)
                                        .then(r => r.json())
                                        .then(list => {
                                            const match = list.find(x => x.kode === kecCode);
                                            if (match) hiddenKecamatan.value = match.nama;
                                        })
                                );
                            }

                            if (item.level === 'desa') {
                                hiddenDesa.value = item.nama;
                            } else if (item.level === 'kecamatan') {
                                hiddenKecamatan.value = item.nama;
                            } else if (item.level === 'kabupaten') {
                                hiddenKabupaten.value = item.nama;
                            } else if (item.level === 'provinsi') {
                                hiddenProvinsi.value = item.nama;
                            }

                            Promise.all(fetchPromises).then(() => {
                                // Tampilkan teks format rapi di input
                                const displayTexts = [];
                                if (hiddenDesa.value) displayTexts.push(hiddenDesa.value);
                                if (hiddenKecamatan.value) displayTexts.push(hiddenKecamatan.value);
                                if (hiddenKabupaten.value) displayTexts.push(hiddenKabupaten.value);
                                if (hiddenProvinsi.value) displayTexts.push(hiddenProvinsi.value);

                                searchInput.value = displayTexts.join(", ");
                                suggestionsContainer.style.display = "none";
                            }).catch(err => {
                                console.error("Error fetching hierarchy details: ", err);
                                // Fallback jika janji gagal
                                searchInput.value = item.nama;
                                suggestionsContainer.style.display = "none";
                            });
                        });

                        suggestionsContainer.appendChild(btn);
                    });

                    suggestionsContainer.style.display = "block";
                })
                .catch(err => {
                    console.error("Autocomplete error:", err);
                });
        }, 300); // 300ms debounce
    });

    // Close suggestions when click outside
    document.addEventListener("click", function (e) {
        if (!searchInput.contains(e.target) && !suggestionsContainer.contains(e.target)) {
            suggestionsContainer.style.display = "none";
        }
    });

    // Keep active styling or focus behavior
    searchInput.addEventListener("focus", function () {
        if (suggestionsContainer.children.length > 0 && searchInput.value.trim().length >= 2) {
            suggestionsContainer.style.display = "block";
        }
    });
});
