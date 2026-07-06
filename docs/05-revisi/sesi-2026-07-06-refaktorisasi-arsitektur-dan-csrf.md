# Log Harian 07: Refaktorisasi Arsitektur Blueprint dan Penerapan Proteksi CSRF
**Tanggal:** 6 Juli 2026
**Durasi:** ~4 jam

---

## Kegiatan yang Dilakukan

Untuk merapikan struktur kode (*codebase*) agar memenuhi standar rekayasa perangkat lunak (*software engineering*) yang baik, modular, mudah dirawat (*maintainable*), serta aman dari celah keamanan web, saya melakukan restrukturisasi besar-besaran terhadap arsitektur web SPK:

1. **Refaktorisasi Arsitektur Modular (Flask Blueprints):**
   * Memecah berkas tunggal controller `app.py` yang sebelumnya gemuk menjadi beberapa modul rute terpisah berbasis Blueprint di dalam folder `routes/`:
     * `routes/auth.py`: Menangani proses login dan logout admin pendamping.
     * `routes/dashboard.py`: Menangani pengolahan ringkasan statistik dan distribusi spasial desa di halaman beranda.
     * `routes/calon.py`: Menangani seluruh fungsi CRUD data calon penerima serta pemicu prediksi ulang SVM.
     * `routes/about.py`: Menangani tampilan informasi sistem, metrik evaluasi model, dan visualisasi visual.
   * Menyederhanakan berkas utama `app.py` menggunakan pola rancangan **Application Factory** (`create_app()`) agar inisialisasi aplikasi terisolasi dengan rapi.

2. **Penerapan Sistem Proteksi CSRF (Cross-Site Request Forgery) Manual:**
   * Membangun sistem validasi token CSRF kustom tanpa modul tambahan (`Flask-WTF`) di berkas `core/auth.py` guna menjaga performa aplikasi tetap ringan.
   * Membuat utilitas generator token kustom yang disimpan pada *session* menggunakan modul enkripsi kriptografi bawaan Python (`secrets`).
   * Menambahkan dekorator `@csrf_required` untuk memeriksa kesamaan token pada setiap metode request `POST` yang masuk, dan membuang error 403 Forbidden secara otomatis jika terjadi ketidakcocokan token.
   * Menghubungkan input token tersembunyi `_csrf_token` ke seluruh formulir masukan dan tombol aksi yang memicu request POST di sistem web (form login, form tambah/edit data, tombol hapus, dan tombol logout).

3. **Penyusunan Berkas Central Flash Notification & Custom Error Pages:**
   * Ekstraksi blok visual notifikasi flash di template Jinja ke dalam berkas parsial terpisah `_flash.html` yang dimasukkan secara modular (`{% include '_flash.html' %}`) di tata letak dasar (`base.html`).
   * Menambahkan penangan kesalahan (*error handlers*) terpusat untuk HTTP status code **403 (Forbidden)**, **404 (Not Found)**, dan **500 (Internal Server Error)** di berkas `core/error_handlers.py`, lengkap dengan rancangan halaman antarmuka error yang elegan di dalam folder `templates/errors/`.

4. **Dekopling File Static Scripts:**
   * Memindahkan logika toggle panel sidebar responsif ke dalam berkas eksternal `static/js/app.js`.
   * Memisahkan skrip inisialisasi Chart.js ke dalam berkas eksternal `static/js/dashboard.js`. Hal ini membuat berkas HTML template murni berfokus pada visual markup.

---

## Justifikasi Perancangan & Keamanan

| Parameter Perancangan | Penjelasan & Alasan Akademis |
|-----------------------|------------------------------|
| **Modularisasi Blueprint** | Membantu pengembangan aplikasi skala besar dengan membagi fungsionalitas berdasarkan domain bisnis (konsep separation of concerns). Hal ini juga menghindari terjadinya *circular imports* saat melakukan impor silang model database dan prediktor. |
| **Proteksi CSRF Kustom** | CSRF adalah salah satu kerentanan web paling berbahaya (OWASP Top 10) di mana penyerang dapat mengeksploitasi session pengguna untuk mengirimkan request destruktif. Validasi token yang dicocokkan dengan session kriptografi memastikan seluruh input data calon penerima benar-benar berasal dari interaksi user sah. |
| **Separasi Statik (JS/HTML)** | Memisahkan kode skrip JavaScript dari dokumen markup mempermudah proses caching browser, meningkatkan performa rendering (*page load speed*), dan mematuhi kebijakan keamanan konten (*Content Security Policy*). |

---

## Output Sesi

- **Application Factory:** ✅ Berhasil membagi aplikasi ke struktur modular rute Blueprint.
- **CSRF Token:** ✅ Validasi token CSRF bekerja mulus untuk setiap tombol aksi POST di sistem.
- **Error Pages:** ✅ Tampilan error 403, 404, dan 500 terintegrasi rapi di folder `templates/errors/`.
- **Eksternal JS:** ✅ Logika visualisasi Chart.js dan sidebar dimuat aman secara eksternal.
