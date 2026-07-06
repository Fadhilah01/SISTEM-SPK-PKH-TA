# Log Harian 05: Perbaikan Skema Preprocessing, Database, dan Implementasi Autentikasi Admin
**Tanggal:** 6 Juli 2026
**Durasi:** ~4 jam

---

## Kegiatan yang Dilakukan

Setelah melakukan audit gap analisis pada tanggal 3 Juli 2026 dan berdiskusi mengenai kebutuhan penambahan sistem keamanan akses bagi pendamping sosial PKH, saya melakukan serangkaian perbaikan pada sistem web SPK lokal serta mengimplementasikan modul autentikasi admin.

Langkah perbaikan ini dikerjakan secara paralel untuk memastikan seluruh komponen (database, formulir input, model prediktor, dan hak akses) terintegrasi dengan selaras sebelum model akhir SVM di-retrain menggunakan dataset riil.

Berikut adalah rincian aktivitas yang telah diselesaikan:

1. **Implementasi Autentikasi Admin (Sistem Login):**
   * **Pembuatan Tabel User:** Menambahkan tabel baru bernama `users` di database SQLite untuk menyimpan kredensial admin.
   * **Proteksi Akses (Security Decorator):** Membuat dekorator `@login_required` pada controller utama Flask. Pintu masuk ke dashboard, formulir penambahan data, daftar calon penerima, dan penjelasan model kini sepenuhnya terkunci dan memerlukan otorisasi session aktif. Jika pengguna belum login, sistem akan otomatis mengalihkan (redirect) ke halaman `/login`.
   * **Hashing Password Aman:** Memanfaatkan library bawaan `werkzeug.security` dengan metode enkripsi hash SHA256 (PBKDF2) untuk mengamankan penyimpanan kata sandi (tidak disimpan dalam bentuk teks mentah).
   * **Navbar Dinamis:** Menyesuaikan menu navigasi utama agar menyembunyikan opsi halaman jika user belum login, serta menampilkan informasi admin aktif beserta tombol *Keluar (Logout)* jika user telah terautentikasi.

2. **Perbaikan Skema Database (`models_db.py`):**
   * Mengubah tipe data untuk indikator kriteria komponen sosial keluarga (`anak_usia_dini`, `anak_sekolah`, dan `lansia`) dari tipe numerik integer (jumlah jiwa) menjadi biner/Boolean (Ada atau Tidak Ada) sesuai ketentuan baku kriteria kelayakan PKH Kemensos.
   * Menambahkan kolom-kolom baru khusus pencatatan skor numerik (`skor_penghasilan`, `skor_pekerjaan`, `skor_kepemilikan_aset`, dan seluruh skor biner komponen sosial) untuk mempermudah perhitungan, meningkatkan transparansi database, dan menjadi bahan audit saat demo sidang skripsi.

3. **Penyelarasan Preprocessing & Normalisasi Model (`svm_predictor.py`):**
   * Menghapus pemrosesan otomatis `LabelEncoder` pada file prediktor karena pilihan dari antarmuka formulir sudah terstruktur dan langsung dipetakan ke skor ordinal (1–5).
   * Mengubah metode normalisasi data dari `StandardScaler` menjadi **Min-Max Normalization** untuk menyelaraskan nilai skor kriteria ordinal (skala 1-5) ke rentang 0 hingga 1 menggunakan rumus matematika yang diamanatkan dalam revisi Pak Yazdi:
     $$V' = \frac{v - 1}{5 - 1} = \frac{v - 1}{4}$$
   * Sementara itu, kriteria biner (skor 0 atau 1) langsung dilewatkan ke model tanpa diubah nilainya karena rentangnya sudah berada di antara 0 dan 1.

4. **Pembaruan Formulir Web & Tampilan (`calon_form.html` & `calon.html`):**
   * Mengubah isian **Penghasilan** dari input angka rupiah menjadi pilihan dropdown 5 kategori Desil resmi (Desil 1 s.d Desil 5).
   * Menyesuaikan dropdown kriteria pekerjaan dan aset agar strictly menggunakan 5 kategori pilihan resmi berdasarkan dokumen dinas sosial.
   * Mengubah input komponen sosial menjadi switch biner (Ada/Tidak).
   * Menghapus filter mata uang `rupiah` di halaman daftar calon penerima dan menggantinya dengan tampilan nama kategori Desil yang dipilih.

5. **Pembuatan Mock Model Pipeline Baru:**
   * Untuk memastikan kelancaran fungsionalitas sistem web, saya membuat skrip helper `generate_mock_model.py` untuk menghasilkan model pipeline dummy (`svm_pkh_pipeline.pkl`) yang kompatibel dengan format dictionary dan normalisasi Min-Max baru.

---

## Keputusan Perbaikan & Justifikasi

| Keputusan Teknis | Alasan / Justifikasi Akademis |
|------------------|-------------------------------|
| **Session-based Authentication via Flask Session** | Sangat cocok untuk sistem lokal demonstrasi sidang skripsi. Ringan, aman, dan tidak membutuhkan dependensi eksternal yang kompleks sehingga mudah didelegasikan dan dipahami mahasiswa. |
| **Penyimpanan Teks Kategori & Skor Ordinal Secara Bersamaan** | Memudahkan visualisasi data di UI (menampilkan teks yang mudah dipahami manusia seperti "Petani/Nelayan") namun tetap menjaga integritas input numerik (skor 3) yang akan diolah oleh model SVM. |
| **Seeding Admin Otomatis pada Inisialisasi Database** | Menghindari kegagalan demo akibat database kosong. Sistem secara cerdas akan langsung mendaftarkan user admin default (`admin` / `admin123`) saat mendeteksi database `spk_pkh.db` baru dibuat. |

---

## Kendala & Solusi

| Kendala Teknis | Solusi |
|----------------|--------|
| Database SQLite lama memblokir perubahan struktur kolom database baru (*database locked* / *operational error*). | Melakukan penghapusan database `spk_pkh.db` lama secara manual untuk mengizinkan sistem melakukan `db.create_all()` ulang dari skema model yang baru diperbarui. |
| Pengguna tidak bisa mengetes halaman prediksi karena file `.pkl` lama mengalami error akibat tidak adanya variabel encoder kategorial. | Menulis skrip pembantu untuk melatih model dummy SVM lokal dengan MinMaxScaler dan mengekspornya ke format dictionary baru. Web SPK kini kembali berfungsi normal secara dinamis. |

---

## Output Sesi

- **Model Database Baru:** ✅ Terimplementasi tabel `User` dan struktur `CalonPenerima` yang sesuai standar kriteria biner.
- **Modul Login Admin:** ✅ Halaman login admin `/login` berfungsi penuh, routes terproteksi, dan password terenkripsi hash.
- **Form Kategori Dinsos:** ✅ Dropdown kriteria resmi desil, pekerjaan, aset, dan komponen sosial aktif.
- **Prediktor MinMaxScaler:** ✅ Penskalan Min-Max untuk input skor ordinal 1-5 berjalan mulus.
- **Mock Model Pipeline:** ✅ File `svm_pkh_pipeline.pkl` baru siap digunakan untuk demo fungsionalitas sebelum retraining model riil.
- **Status Database:** ✅ Bersih dari data dummy lama, inisialisasi user bawaan berhasil diselesaikan.
