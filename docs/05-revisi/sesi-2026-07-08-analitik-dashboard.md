# Log Harian 10: Implementasi Visualisasi Analitik Interaktif dan Restrukturisasi Dashboard
**Tanggal:** 8 Juli 2026
**Durasi:** ~6 jam

---

## Kegiatan yang Dilakukan

Untuk mempermudah monitoring sebaran calon penerima bantuan PKH serta memperdalam aspek analisis data bagi Dinas Sosial, saya melakukan perombakan tata letak dashboard utama, membuat kontrol filter terpadu, dan menerapkan visualisasi interaktif yang modern:

1. **Pusat Analisis Terpadu & Restrukturisasi Tata Letak:**
   * Menyatukan panel filter dan grafik utama ke dalam satu komponen horizontal terpadu (12 kolom) agar tidak terpisah-pisah.
   * Tombol-tombol filter daerah kini diletakkan langsung di atas grafik secara inline. Panel filter ini juga dinamis: hanya memunculkan filter spasial di Tab Wilayah, skala waktu di Tab Tren, dan opsi perbandingan di Tab Komparasi.
   * Memindahkan tabel "Hasil Keputusan Terbaru" ke kiri bawah sebagai pelengkap, membatasi row visualnya ke maksimal 3 row per halaman dengan paginasi *client-side* Next/Prev berbasis JavaScript.
   * Menghapus semua pewarnaan yang terlalu mencolok dan menstandarkan desain beranda dengan konsep monokromatis minimalis (hitam, putih, abu-abu) sesuai petunjuk dosen pembimbing.

2. **Penerapan Custom Dropdown UI dengan Fitur Pencarian:**
   * Mengganti dropdown `<select>` standar bawaan browser yang kaku menjadi dropdown kustom berbasis Bootstrap.
   * Ketika tombol dropdown diklik, akan muncul menu pilihan yang memiliki **kolom pencarian teks secara real-time** sehingga memudahkan pengguna mencari nama Provinsi, Kabupaten, Kecamatan, atau Desa yang sangat banyak di Indonesia.
   * **Penyebarluasan Desain (Reuse Dropdown):** Menerapkan desain dropdown kustom premium ini ke seluruh bagian sistem untuk konsistensi visual:
     * **Form Tambah Calon:** Kriteria Penghasilan, Pekerjaan, dan Kepemilikan Aset.
     * **Form Tambah Admin:** Pilihan Hak Akses (Role) antara Admin dan Superadmin.
     * **Filter Data Calon:** Pilihan penapisan "Hasil Keputusan" (Semua, Layak, Tidak Layak).
     * **Dashboard Analitik:** Pilihan "Skala Waktu" (Tren) dan "Mode Perbandingan" (Komparasi).

3. **Penyediaan API Endpoint Analitik Internal & Toleransi Prefix:**
   * Mengembangkan endpoint `/api/analytics` pada `routes/dashboard.py` untuk melayani data JSON secara cepat ke Chart.js.
   * Memperbaiki pencarian data wilayah bertingkat agar toleran terhadap penamaan yang memiliki prefix (seperti `KABUPATEN SIGI` dari dropdown dicocokkan dengan data `SIGI` di database) dengan memanfaatkan operator SQL `OR` dan pencocokan substring `LIKE` case-insensitive.
   * Memperbaiki pembatasan hasil di API daerah `/api/daerah` agar menampilkan seluruh 38 provinsi di Indonesia secara lengkap (tidak terpotong 20 data teratas saja).

4. **Penanganan Visual untuk Data Kosong:**
   * Membuat div placeholder `#chartPlaceholder` dengan teks *"Tidak ada data yang ditemukan untuk filter ini"* dan ikon pendukung yang otomatis muncul menggantikan kanvas grafik jika data hasil filter kosong.

5. **Penyuntikan Data Historis Uji Coba:**
   * Menjalankan skrip `seed_historical.py` untuk mengisi database dengan 35 data calon penerima dummy yang tersebar sepanjang 1 tahun ke belakang untuk mendemonstrasikan visualisasi tren waktu dan perbandingan periode secara riil.

---

## Hasil Pengujian & Verifikasi

* **Drill-down Spasial Bertingkat:** Sukses. Memilih Kabupaten Sigi memuat kecamatan-kecamatan di bawahnya dan merender grafik sebaran dengan lancar.
* **Dropdown Search:** Kolom pencarian di dalam dropdown menyaring data provinsi/daerah secara instan saat mengetik.
* **Placeholder Data Kosong:** Ketika data di filter kosong, grafik disembunyikan dan teks placeholder muncul di tengah area.
* **Warna Monokrom & Konsistensi UI:** Sukses besar. Menghapus warna biru default Bootstrap pada tombol tab aktif ("Wilayah"), ikon login admin, badge format file (Excel/CSV), tombol impor/ekspor data, serta **item komponen paginasi tabel** (nomor halaman aktif berwarna hitam, nomor halaman non-aktif/panah berwarna abu-abu). Seluruh visualisasi grafik dan komponen dropdown kustom ter-render rapi hanya menggunakan gradasi warna hitam, putih, dan abu-abu di seluruh halaman.
* **Unit Testing:** Lulus 100% (**OK**) pada pengujian otomatis `test_05_api_analytics` di file `scratch/test_features.py`.

---

## Output Sesi

- **Integrated Dashboard Layout:** Tampilan bersih, ergonomis, terpadu, dan bertema monokrom.
- **Custom Select with Search:** Dropdown pencarian kustom yang ramah pengguna di seluruh sistem (Tambah Calon, Tambah Admin, Filter Data, Dashboard).
- **100% Monochrome Aesthetic:** Navigasi tab, tombol aksi, ikon, form element, dan **paginasi tabel** sepenuhnya menggunakan palet warna hitam, putih, dan abu-abu.
- **Robust API & SQL Tolerant:** API analitik cepat dengan pencocokan wilayah toleran prefix.
- **Empty State UI:** Tampilan placeholder estetis saat pencarian tidak menghasilkan data.
- **Paginasi Keputusan:** Paginasi client-side 3 baris di tabel riwayat terbaru.
