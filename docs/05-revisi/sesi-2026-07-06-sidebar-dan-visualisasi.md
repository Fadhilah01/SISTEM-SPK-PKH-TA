# Log Harian 06: Redesain Layout Sidebar, Chart Visualisasi, dan Fitur Pencarian/Paginasi
**Tanggal:** 6 Juli 2026
**Durasi:** ~3 jam

---

## Kegiatan yang Dilakukan

Untuk menyempurnakan kegunaan praktis (*usability*) dan tampilan antarmuka Sistem Pendukung Keputusan (SPK) ini agar terlihat lebih profesional, modern, serta responsif, saya melakukan perombakan tata letak halaman utama dan menambahkan beberapa fitur interaktif:

1. **Redesain Layout Navigasi (Top Navbar → Sidebar):**
   * Mengganti bar navigasi atas (`navbar`) menjadi panel navigasi samping kiri (`sidebar`) untuk meningkatkan ruang pandang layar desktop.
   * Panel sidebar ini terintegrasi secara dinamis dengan session login (hanya tampil jika pengguna sudah masuk log) dan menampilkan identitas pengguna aktif secara personal.
   * Menambahkan tata letak responsif untuk versi mobile: sidebar otomatis tersembunyi (*collapsible drawer*) dan dapat dipicu melalui tombol menu hamburger di bilah tajuk atas (`mobile header`), lengkap dengan lapisan buram (*sidebar overlay*).

2. **Integrasi Visualisasi Data Interaktif (Chart.js):**
   * Memasang dua diagram interaktif pada Dashboard utama untuk memberikan rangkuman data secara visual bagi admin dinas sosial:
     1. **Doughnut Chart (Persentase Kelayakan):** Menampilkan perbandingan persentase calon penerima bantuan yang diklasifikasikan model SVM sebagai **Layak** vs **Tidak Layak**.
     2. **Bar Chart (Sebaran per Desa):** Menampilkan sebaran statistik jumlah calon penerima bantuan di tiga kelurahan/desa fokus penelitian (Desa Posona, Desa Kasimbar Palapi, dan Desa Posona Atas).
   * Visualisasi ini menggunakan palet warna monokromatik premium (gelap, abu-abu, dan putih) agar selaras dengan konsep desain minimalis modern.

3. **Restrukturisasi Menu & FAQ Accordion:**
   * Memindahkan grafik *Confusion Matrix* dan detail metrik performa model SVM dari Dashboard utama ke halaman **Tentang**. Hal ini bertujuan agar dashboard benar-benar difokuskan untuk kebutuhan operasional data harian pengguna non-teknis.
   * Menghapus bagian dasar teori sidang mahasiswa yang kurang tepat untuk pengguna umum. Sebagai gantinya, saya membangun modul **FAQ berbasis Accordion** interaktif (Bootstrap 5) yang menjelaskan secara sederhana cara kerja sistem, perhitungan desil, dan artian skor keyakinan (*confidence score*).

4. **Peningkatan Manajemen Data (Pencarian & Paginasi):**
   * **Fitur Pencarian:** Menambahkan kolom cari pada daftar data calon penerima bantuan. Pengguna kini dapat memfilter baris data berdasarkan nama atau alamat/desa tertentu.
   * **Fitur Paginasi:** Mengimplementasikan penjelajahan data bertahap (10 data per halaman) untuk menggantikan daftar gulir panjang yang tidak efisien. Alur ini secara dinamis mempertahankan parameter kata kunci pencarian saat pengguna berpindah halaman.

---

## Keputusan Perancangan & Justifikasi

| Keputusan Teknis | Alasan / Justifikasi Akademis |
|------------------|-------------------------------|
| **Penggunaan Sidebar dibanding Top Navbar** | Tata letak sidebar merupakan standar industri modern untuk aplikasi bertipe dashboard/admin panel karena menampung menu lebih teratur dan memberikan area kerja konten yang lebih luas. |
| **Pemisahan Logika Model ML dari Dashboard Utama** | Pengguna akhir (staf/admin dinas sosial) tidak membutuhkan visualisasi teknis confusion matrix atau presisi model pada aktivitas harian mereka. Pemusatan hal tersebut di halaman Tentang menjaga kebersihan desain sistem. |
| **Penerapan Paginasi Sisi Server (Server-side Pagination)** | Berbeda dengan penskalaan sisi klien yang memuat semua data sekaligus (menyebabkan beban memori browser membengkak), paginasi sisi server memotong data di tingkat kueri database (SQL LIMIT & OFFSET via SQLAlchemy), sehingga sistem tetap responsif meski data bertambah ribuan. |

---

## Kendala & Solusi

| Kendala Teknis | Solusi |
|----------------|--------|
| Tampilan laci sidebar di mobile tidak otomatis tertutup saat tautan diklik atau area luar disentuh. | Menambahkan naskah JavaScript sederhana untuk mendengarkan aktivitas klik pada `.sidebar-overlay` dan tombol silang `.btn-close` untuk memicu pembuangan class `.show` pada panel sidebar. |
| Parameter pencarian hilang saat admin mengklik halaman berikutnya pada navigasi paginasi. | Menyesuaikan tautan tombol paginasi di template Jinja agar secara eksplisit menyertakan argumen pencarian `q`, yaitu `href="{{ url_for('daftar_calon', page=p, q=q) }}"`. |

---

## Output Sesi

- **Sidebar Responsif:** ✅ Terintegrasi penuh dengan Bootstrap 5 dan CSS Grid di `base.html` & `style.css`.
- **Dua Chart Interaktif:** ✅ Doughnut chart kelayakan dan Bar chart desa berfungsi di `dashboard.html`.
- **Tentang Halaman Baru:** ✅ FAQ Accordion interaktif aktif dan detail metrik SVM dipindahkan dengan rapi.
- **Pencarian & Paginasi:** ✅ Berhasil memfilter data dan membatasi muatan baris tabel di `calon.html`.
