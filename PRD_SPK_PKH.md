
# Product Requirements Document (PRD)
## SPK Kelayakan Calon Penerima Bantuan PKH
### Berbasis Algoritma Support Vector Machine (SVM)

---

## 1. Ringkasan Eksekutif

Sistem Pendukung Keputusan (SPK) berbasis web yang mengimplementasikan algoritma **Support Vector Machine (SVM)** untuk mengklasifikasikan kelayakan calon penerima bantuan Program Keluarga Harapan (PKH) di Kecamatan Kasimbar (Desa Posona, Kasimbar Palapi, dan Posona Atas).

## 2. Tujuan

- Mengimplementasikan SVM dalam SPK penentuan kelayakan PKH
- Mengetahui performa algoritma SVM (akurasi, presisi, recall)
- Menyediakan sistem berbasis web yang memudahkan pendamping PKH dalam pengambilan keputusan

## 3. Fitur & Fungsionalitas

### 3.1 Fitur Wajib (MVP)
| Fitur | Deskripsi | Prioritas | Status |
|-------|-----------|-----------|--------|
| Manajemen Data Calon Penerima | CRUD data calon penerima bantuan (dengan validasi & unik NIK) | P0 | ✅ Selesai |
| Klasifikasi SVM | Prediksi layak/tidak layak berdasarkan model SVM | P0 | ⚠️ Perlu retrain (lihat Bab 10) |
| Dashboard SPK | Ringkasan data + Pie/Doughnut Chart proporsi kelayakan (Chart.js) | P0 | ✅ Selesai (6 Juli 2026) |
| Riwayat Keputusan | History prediksi + detail input | P0 | ✅ Selesai |
| Pencarian & Paginasi | Menyaring dan membatasi data calon penerima di tabel (mendukung pencarian NIK) | P1 | ✅ Selesai (6 Juli 2026) |
| Import Data (Excel/CSV) | Import massal data calon dari file Excel/CSV dengan validasi otomatis (termasuk NIK), pencegahan duplikasi NIK, dan batch prediksi SVM | P1 | ✅ Selesai (6 Juli 2026) |
| Export Laporan (Excel/CSV) | Export data dengan filter dinamis (waktu, hasil, kolom termasuk NIK, format) ke Excel/CSV | P1 | ✅ Selesai (6 Juli 2026) |

### 3.2 Fitur Tambahan
| Fitur | Deskripsi | Prioritas | Status |
|-------|-----------|-----------|--------|
| Manajemen Pengguna | Login terproteksi session, Sidebar, Ganti Password mandiri, dan multi-role (Superadmin/Admin) via RBAC | P1 | ✅ Selesai (6 Juli 2026) |
| **Keamanan Sistem** | Proteksi CSRF, Rate Limit Login (5/menit), Auto-lock 10 gagal login, Force Password Change, Security Headers (CSP, XFO DENY, HSTS, nosniff, Permissions-Policy), XSS Prevention (sanitasi input + escape output), Session Security (HTTPOnly, SameSite, 4 jam timeout), Validasi File Upload (ekstensi + MIME + magic bytes), Password Policy (min 8 + huruf + angka) | P1 | ✅ Selesai (7 Juli 2026) |
| Autocomplete Wilayah | Pencarian dan autocomplete wilayah bertingkat (Provinsi s.d. Desa) dari data referensi geospasial | P1 | ✅ Selesai (7 Juli 2026) |
| Grafiks Dinamis Dashboard | Visualisasi analitik interaktif dengan Chart.js: sebaran wilayah, tren waktu, komparasi periode | P1 | ❌ Dihapus atas permintaan klien (11 Juli 2026) |
| Re-training Model | Update model jika dataset baru tersedia | P2 | ✅ Selesai (Dataset real 318 data, akurasi 98.44%) |

## 4. Pengguna Sistem

| Role | Deskripsi |
|------|-----------|
| **Admin/Pendamping PKH** | Mengelola data calon penerima, menjalankan klasifikasi, melihat hasil keputusan |

## 5. Alur Bisnis

```
1. Pendamping PKH mengumpulkan data calon penerima
2. Data dimasukkan ke sistem melalui form input (pilihan kategori)
3. Sistem mengkonversi kategori menjadi skor ordinal (1-5 atau 0/1)
4. Sistem memproses skor melalui model SVM yang sudah dilatih
5. Sistem menampilkan status: LAYAK / TIDAK LAYAK
6. Pendamping PKH menggunakan hasil sebagai rekomendasi keputusan
```

## 6. Atribut/Kriteria Penilaian

Berdasarkan dokumen resmi dari **Zainal — Ketua Tim SDM PKH Provinsi Sulawesi Tengah** (dasar: Keputusan Dirjen Linjamsos No. 9/3/HK.01.1/2025):

| No | Kriteria | Bobot | Tipe Data | Skor | Sumber |
|----|----------|-------|-----------|------|--------|
| 1 | **Penghasilan** | 25% | Ordinal (1-5) | Desil 1(<500k)=5 s.d Desil 5(1.3jt-1.5jt)=1 | Dirjen PKH |
| 2 | **Pekerjaan** | 20% | Ordinal (1-5) | Tidak Bekerja=5 s.d PNS=1 | Dirjen PKH |
| 3 | **Kepemilikan Aset** | 15% | Ordinal (1-5) | Tidak Punya=5 s.d Mobil+Tanah=1 | Dirjen PKH |
| 4 | **Ibu Hamil** | 10% | Biner (0/1) | Ada=1, Tidak=0 | Dirjen PKH |
| 5 | **Anak Usia Dini** | 10% | Biner (0/1) | Ada=1, Tidak=0 | Dirjen PKH |
| 6 | **Anak Sekolah** | 10% | Biner (0/1) | Ada=1, Tidak=0 | Dirjen PKH |
| 7 | **Penyandang Disabilitas** | 5% | Biner (0/1) | Ada=1, Tidak=0 | Dirjen PKH |
| 8 | **Lansia** | 5% | Biner (0/1) | Ada=1, Tidak=0 | Dirjen PKH |
| | **Total** | **100%** | | | |

### Detail Indikator Penilaian

#### Penghasilan (Bobot 25%)
| Skor | Kategori | Rentang |
|------|----------|---------|
| 5 | Desil 1 | < Rp.500.000 |
| 4 | Desil 2 | ± Rp.600.000 – Rp.700.000 |
| 3 | Desil 3 | ± Rp.800.000 – Rp.900.000 |
| 2 | Desil 4 | ± Rp.1.000.000 – Rp.1.200.000 |
| 1 | Desil 5 | ± Rp.1.300.000 – Rp.1.500.000 |

#### Pekerjaan (Bobot 20%)
| Skor | Kategori |
|------|----------|
| 5 | Tidak Bekerja |
| 4 | Pekerja Bebas |
| 3 | Petani/Nelayan |
| 2 | Wiraswasta |
| 1 | PNS/Pegawai Tetap |

#### Kepemilikan Aset (Bobot 15%)
| Skor | Kategori |
|------|----------|
| 5 | Tidak Memiliki Aset |
| 4 | Motor (harga jual rendah) |
| 3 | Motor (harga jual tinggi) |
| 2 | Mobil atau Tanah/Kebun |
| 1 | Mobil dan Tanah/Kebun |

#### Komponen Sosial (Masing-masing Biner: 1=Ada, 0=Tidak)
- **Ibu Hamil** (10%) — kehamilan dibatasi sampai anak kedua
- **Anak Usia Dini 0-6 th** (10%) — belum sekolah di Dapodik
- **Anak Sekolah** (10%) — SD/SMP/SMA di Dapodik
- **Penyandang Disabilitas** (5%) — dalam satu KK
- **Lansia** (5%) — dalam satu KK

## 7. Metrik Evaluasi Model

| Metrik | Target | Hasil Prototype (Sintetis) | Benchmark Pak Yazdi |
|--------|--------|---------------------------|---------------------|
| Akurasi | ≥ 85% | 89% | 88.57% |
| Presisi | ≥ 85% | 90% | 86.49% |
| Recall | ≥ 85% | 88% | 91.43% |
| F1-Score | ≥ 85% | 0.89 | 88.89% |

> **Catatan:** Hasil prototype masih menggunakan dataset sintetis dan encoding LabelEncoder. Saat retrain dengan data real dan encoding ordinal 1-5, angka-angka ini akan berubah. Target minimal tetap ≥ 85%.

## 8. Dataset & Skenario

- **Sumber data:** Pendamping PKH 3 desa (Posona, Kasimbar Palapi, Posona Atas)
- **Jumlah data:** ±350 data (sudah berstatus layak/tidak layak)
- **Pembagian:** 80% Training (280) | 20% Testing (70)
- **Preprocessing:** Encoding ordinal (1-5) → Min-Max Normalization → SVM
- **Revisi penguji (Pak Yazdi Pusadan):** SVM bukan metode SPK, tapi model klasifikasi yang *diintegrasikan* ke SPK
- **Catatan:** Format encoding menggunakan skala 1-5 (bukan LabelEncoder) seperti ditetapkan oleh Tim PKH Sulteng

## 9. Kendala & Asumsi

- Dataset real ±350 data dari pendamping PKH — **masih ditunggu**
- Model akan di-retrain saat dataset real tersedia (encoding sudah fix berdasarkan indikator resmi)
- Sistem berjalan di lingkungan lokal/web hosting sederhana
- Output klasifikasi: **Layak** atau **Tidak Layak** (binary, tidak ada kelas "Sedang")
- SVM tetap bisa mengklasifikasikan data di area perbatasan (margin decision)

## 10. Gap Analisis & Rencana Perbaikan

> **Diidentifikasi:** 3 Juli 2026, setelah menerima dokumen resmi dari Tim PKH Sulteng

### 10.1 Daftar Gap & Status Resolusi

| No | Gap | Dampak | Status Per 6 Juli 2026 |
|----|-----|--------|-------------------------|
| 1 | Encoding pakai LabelEncoder, seharusnya Ordinal 1-5 | Model belajar pola yang salah | ✅ Selesai (Backend & Predictor siap, nunggu dataset real) |
| 2 | Scaler pakai StandardScaler, seharusnya MinMaxScaler | Normalisasi tidak sesuai skala data ordinal | ✅ Selesai (Backend & Predictor siap, nunggu dataset real) |
| 3 | Kategori form web tidak cocok dengan kategori resmi | User input tidak valid | ✅ Selesai (Form & model terintegrasi dropdown resmi Dinsos) |
| 4 | Format .pkl tidak konsisten (class vs dictionary) | Web error saat load model | ✅ Selesai (Predictor diubah untuk load format dictionary) |
| 5 | anak_usia_dini, anak_sekolah, lansia harusnya biner | Data yang disimpan tidak sesuai format resmi | ✅ Selesai (Kolom database & form diubah ke Boolean/Biner) |

### 10.2 Rencana Perbaikan (Tahap Selanjutnya)

Dengan selesainya refactoring Web SPK Lokal, seluruh gap di atas telah berhasil diselesaikan di sisi aplikasi. Saat dataset riil CSV dari pendamping PKH tersedia, langkah selanjutnya adalah:
1. Menjalankan *retraining* model SVM baru di Kaggle menggunakan skema encoding ordinal manual dan normalisasi Min-Max.
2. Mengunduh file `.pkl` berformat dictionary baru hasil latihan.
3. Menimpa file mock model di folder `web/models/svm_pkh_pipeline.pkl`. Aplikasi web akan langsung terintegrasi secara otomatis tanpa perlu mengubah baris kode lagi.


### 10.3 Penjelasan untuk Sidang

Jika ditanya penguji tentang perubahan encoding:

> "Pada tahap awal, saya menggunakan LabelEncoder karena data masih sintetis dan belum ada panduan resmi. Setelah menerima dokumen dari Ketua Tim SDM PKH Sulteng (Keputusan Dirjen Linjamsos No. 9/3/HK.01.1/2025), encoding diubah menjadi ordinal 1-5 agar model SVM dapat memahami urutan tingkat kelayakan — skor 5 berarti paling layak, skor 1 paling tidak layak. Perubahan ini membuat model lebih akurat karena SVM bisa menangkap jarak antar kategori secara bermakna."
