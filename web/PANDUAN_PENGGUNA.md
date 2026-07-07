# 📘 Panduan Lengkap Penggunaan Website SPK PKH — SVM

**Sistem Pendukung Keputusan Kelayakan Calon Penerima Bantuan PKH**
**Implementasi Algoritma Support Vector Machine (SVM)**

---

## 📋 Daftar Isi

1. [Pengenalan Sistem](#1-pengenalan-sistem)
2. [Login & Keamanan](#2-login--keamanan)
3. [Dashboard Utama](#3-dashboard-utama)
4. [Manajemen Data Calon Penerima](#4-manajemen-data-calon-penerima)
5. [CRUD Calon Penerima](#5-crud-calon-penerima)
6. [Import Data Massal (Bulk Import)](#6-import-data-massal-bulk-import)
7. [Export Data (Bulk Export)](#7-export-data-bulk-export)
8. [Manajemen Admin (Superadmin)](#8-manajemen-admin-superadmin)
9. [Halaman Tentang Sistem](#9-halaman-tentang-sistem)
10. [Panduan Kategori & Kriteria](#10-panduan-kategori--kriteria)
11. [Pemecahan Masalah (Troubleshooting)](#11-pemecahan-masalah-troubleshooting)
12. [Daftar Lengkap Route & Endpoint](#12-daftar-lengkap-route--endpoint)

---

## 1. Pengenalan Sistem

### 1.1 Tentang Aplikasi

SPK PKH adalah **Sistem Pendukung Keputusan** yang digunakan oleh **Dinas Sosial** dan **Pendamping PKH** untuk menentukan kelayakan calon penerima bantuan **Program Keluarga Harapan (PKH)** secara objektif, cepat, dan terkomputerisasi.

Sistem menggunakan algoritma **Support Vector Machine (SVM) dengan kernel RBF** yang telah dilatih dengan data historis 318 data real dari wilayah Posona, Kasimbar Palapi, dan Posona Atas. Akurasi model mencapai **98.44%**.

### 1.2 Dua Level Akses (RBAC)

Sistem memiliki dua level hak akses berdasarkan **Role-Based Access Control (RBAC)**:

| Role | Hak Akses | Pengguna |
|------|-----------|----------|
| **Superadmin** | Akses penuh + Manajemen Admin | Administrator Dinsos |
| **Admin** | Semua fitur kecuali Manajemen Admin | Pendamping PKH |

**Perbedaan akses:**
- **Superadmin** — melihat menu **"Manajemen Admin"** di sidebar (tambah, lihat, hapus akun admin)
- **Admin** — menu Manajemen Admin **tidak muncul** di sidebar. Tidak bisa mengelola pengguna lain.

### 1.3 Akun Default

| Username | Password | Role | Status |
|----------|----------|------|--------|
| `admin` | `admin123` | superadmin | Wajib ganti password |
| `user1` | `user1123` | admin | Wajib ganti password |

> ⚠️ **PENTING:** Kedua akun default memiliki *flag* `must_change_password=True`. Saat login pertama kali, sistem akan MEMAKSA untuk mengganti password sebelum bisa mengakses fitur apa pun. Ini adalah fitur keamanan.

### 1.4 Arsitektur Sistem Singkat

```
Input Form → Hitung Skor Ordinal (1-5) → MinMaxScaler (0-1) → SVM RBF Classifier → Output: Layak/Tidak Layak
```

1. Admin mengisi data calon melalui form (kategori penghasilan, pekerjaan, aset, komponen sosial)
2. Sistem mengkonversi kategori ke **skor ordinal 1-5** (5 = paling rentan, 1 = paling mampu)
3. Komponen sosial dikonversi ke **biner (0/1)**
4. Skor dinormalisasi ke rentang 0-1 menggunakan **MinMaxScaler**
5. Model SVM RBF memproses 8 fitur input dan menghasilkan keputusan
6. Hasil ditampilkan sebagai **Layak** atau **Tidak Layak** dengan **Confidence Score** (tingkat kepercayaan)

### 1.5 Tech Stack

| Komponen | Teknologi |
|----------|-----------|
| Backend | Python Flask |
| Database | SQLite 3 (file: `spk_pkh.db`) |
| Frontend | Bootstrap 5.3 + Chart.js 4.4 |
| CSS | Monochrome minimalis kustom |
| Model SVM | Scikit-learn (RBF Kernel) |
| File Data Wilayah | `daerah_indonesia.json` (89k+ wilayah) |

---

## 2. Login & Keamanan

### 2.1 Halaman Login

**Akses:** Buka website, otomatis diarahkan ke halaman login.

**Tampilan:**
- Logo ikon gembok
- Judul "Masuk Sistem — SPK Kelayakan Calon Penerima PKH - SVM"
- Form input **Username** (dengan ikon orang)
- Form input **Password** (dengan ikon kunci + tombol 👁️ untuk lihat/sembunyikan password)
- Tombol **"Masuk"** (biru, full width)

**Cara Login:**
1. Masukkan username
2. Masukkan password
3. Klik tombol **"Masuk"**

### 2.2 Fitur Keamanan Login

| Fitur | Detail |
|-------|--------|
| **Rate Limiting** | Maksimal 5 percobaan per menit dari IP yang sama |
| **Lockout Sementara** | Setelah 10 kali gagal login, akun dikunci sementara |
| **Session Timeout** | Session otomatis berakhir setelah **4 jam** tidak aktif |
| **CSRF Protection** | Setiap form POST menggunakan token CSRF unik |
| **Password Policy** | Minimal 8 karakter, mengandung huruf + angka |

### 2.3 Session & Logout

- **Session:** Begitu login berhasil, session aktif selama 4 jam
- **Logout:** Klik tombol **"Keluar"** di sidebar bagian bawah (sebelah kanan nama user)
  - Logout menggunakan metode POST (dilindungi CSRF)
  - Setelah logout, muncul flash message: "Anda telah keluar dari sistem."

### 2.4 Ganti Password

**Akses dari Sidebar:** Klik tombol **"Ganti Password"** (ikon kunci) di sidebar bagian bawah.

**Akses dari URL:** `/change-password`

**Form:**
1. **Password Lama** — masukkan password saat ini
2. **Password Baru** — minimal 8 karakter, harus mengandung huruf dan angka
3. **Konfirmasi Password Baru** — ulangi password baru

**Aturan Password Baru:**
- ✅ Minimal **8 karakter**
- ✅ Mengandung **huruf** (a-z, A-Z)
- ✅ Mengandung **angka** (0-9)
- ❌ Tidak boleh sama dengan password lama
- ❌ Tidak boleh sama dengan password yang sudah pernah digunakan sebelumnya (hash unik)

**Jika dipaksa ganti password (force change):**
- Muncul alert kuning dengan pesan peringatan keamanan
- Tombol "Batal" tidak akan mengarah ke dashboard (karena harus ganti password dulu)

**Tips:** Gunakan tombol 👁️ di sebelah kanan input password untuk melihat karakter yang diketik.

---

## 3. Dashboard Utama

**Akses:** `/` atau klik menu **"Dashboard"** di sidebar.

### 3.1 Header & Status Model

- **Judul:** "Dashboard SPK PKH"
- **Badge Status Model:**
  - 🟢 **Model SVM: Tersedia** — model aktif dan siap memprediksi
  - 🔴 **Model SVM: Tidak Tersedia** — file model belum di-load (hanya mode penyimpanan data)

Jika model tidak tersedia, data tetap bisa diinput/disimpan tetapi **tidak diprediksi**.

### 3.2 Kartu Statistik (Bento Grid)

Tiga kartu metrik utama:

| Kartu | Ikon | Menampilkan |
|-------|------|-------------|
| **Total Calon** | 👥 | Jumlah semua calon yang terdaftar |
| **Dinyatakan Layak** | ✅ | Jumlah calon hasil prediksi = Layak |
| **Dinyatakan Tidak Layak** | ❌ | Jumlah calon hasil prediksi = Tidak Layak |

Setiap kartu memiliki sub-label: "Calon Penerima terdaftar" / "Berdasarkan prediksi SVM"

### 3.3 Pusat Analisis & Monitoring (Grafik Interaktif)

Ini adalah fitur paling canggih di dashboard. Terdapat **3 tab visualisasi** yang bisa dipilih:

#### ▶️ Tab Wilayah (Bar Chart)

Menampilkan **sebaran calon berdasarkan wilayah** dalam bentuk diagram batang.

**Filter yang tersedia:**
1. **Filter Spasial Bertingkat (4 level):**
   - 🌍 **Provinsi** — pilih provinsi (dropdown searchable)
   - 🏛️ **Kabupaten** — otomatis terisi setelah provinsi dipilih
   - 🏘️ **Kecamatan** — otomatis terisi setelah kabupaten dipilih
   - 🏡 **Desa** — otomatis terisi setelah kecamatan dipilih
   
   > 💡 **Cara pakai:** Pilih satu filter, pilihan berikutnya akan terisi otomatis dari database. Ingin reset? Pilih "-- Semua --" di dropdown paling atas.

2. **Filter Rentang Waktu:** Pilih tanggal awal dan akhir (format: YYYY-MM-DD)

**Cara kerja chart:**
- Menampilkan 7 wilayah teratas + sisanya digabung ke "Lainnya"
- Jika tidak ada provinsi dipilih → chart sebaran per **Provinsi**
- Jika provinsi dipilih → chart sebaran per **Kabupaten**
- Jika kabupaten dipilih → chart sebaran per **Kecamatan**
- Jika kecamatan dipilih → chart sebaran per **Desa**

#### ▶️ Tab Tren (Line Chart)

Menampilkan **tren jumlah registrasi calon dari waktu ke waktu**.

**Filter tambahan:**
- **Skala Waktu:** Bulanan (default), Mingguan, Kuartalan, Tahunan
- **Rentang Waktu:** Sama seperti tab Wilayah

**Cocok digunakan untuk:** Melihat pola pendaftaran calon — apakah meningkat atau menurun dalam periode tertentu.

#### ▶️ Tab Komparasi (Grouped Bar Chart)

Dua mode perbandingan:

**Mode A: Bandingkan Periode Waktu**
- Bandingkan dua rentang waktu berbeda
- Isi **Periode A** (tanggal awal - akhir) dan **Periode B** (tanggal awal - akhir)
- Secara otomatis terisi default: Periode A = 6 bulan terakhir, Periode B = 6 bulan sebelum itu
- Chart menampilkan perbandingan Layak vs Tidak Layak di kedua periode

**Mode B: Bandingkan Kriteria KPM**
- Pilih kriteria: **Penghasilan**, **Pekerjaan**, atau **Kepemilikan Aset**
- Chart menampilkan distribusi calon berdasarkan kriteria tersebut (dengan label singkat)

### 3.4 Panel Keputusan Terbaru

- **Judul:** "Keputusan Terbaru (Pelengkap)"
- **Tombol:** "Lihat Semua" → menuju halaman Data Calon
- **Tabel:** 3 kolom — Nama Calon, Hasil Klasifikasi (badge Layak/Tidak Layak), Confidence (persentase)
- **Paginasi Client-Side:** Maksimal 3 baris per halaman, dengan navigasi ◀ ▶
- **Jika kosong:** Menampilkan ikon kotak kosong + tombol "Tambah Calon"

### 3.5 Proporsi Kelayakan (Donat Chart)

- **Judul:** "Proporsi Kelayakan Calon Penerima"
- Diagram donat monokrom: **Layak** (hitam) vs **Tidak Layak** (abu-abu)
- **Jika kosong:** Menampilkan pesan "Data kelayakan belum tersedia."

---

## 4. Manajemen Data Calon Penerima

**Akses:** `/calon` atau klik menu **"Data Calon"** di sidebar.

### 4.1 Tampilan Daftar Calon

Halaman ini menampilkan **tabel data calon penerima PKH** dengan fitur pencarian, filter, dan paginasi.

**Header:**
- **Judul:** "Data Calon Penerima PKH"
- **3 Tombol Aksi:**
  - 🟦 **Tambah** (biru) → halaman tambah calon baru
  - 🟩 **Import** (hijau) → halaman import massal
  - 🟦 **Export** (biru muda) → halaman export data

### 4.2 Panel Filter & Pencarian

Form filter terdiri dari:

| Filter | Tipe | Deskripsi |
|--------|------|-----------|
| **Cari Nama/Alamat/NIK** | Text input | Cari berdasarkan nama, alamat, atau 16-digit NIK (partial match) |
| **Dari Tanggal** | Date picker | Awal rentang tanggal input data |
| **Sampai Tanggal** | Date picker | Akhir rentang tanggal input data |
| **Hasil Keputusan** | Dropdown kustom | Semua / Layak / Tidak Layak |
| **Tombol Filter** | Tombol | Terapkan filter (ikon funnel) |
| **Tombol Reset** | Tombol | Hapus semua filter (ikon panah putar) |

> 💡 **Tips:** Jika sudah melakukan pencarian, muncul tombol ❌ di sebelah kanan input pencarian untuk menghapus cepat.

### 4.3 Tabel Data Calon

| Kolom | Isi |
|-------|-----|
| **#** | Nomor ID (monospace, abu-abu) |
| **Nama** | Nama lengkap (bold) |
| **NIK** | Nomor Induk Kependudukan (16 digit, monospace, abu-abu) |
| **Wilayah** | Nama desa (badge) + kecamatan, kabupaten di bawahnya (jika ada). Jika kosong: badge "Fallback" |
| **Alamat Detail** | Maks 25 karakter, jika lebih panjang akan dipotong dengan "..." |
| **Penghasilan** | Badge dengan ikon uang 💰, warna berdasarkan severity (1-5) |
| **Pekerjaan** | Badge dengan ikon kerja 💼, warna berdasarkan severity (1-5) |
| **Kep. Aset** | Badge dengan ikon rumah 🏠, warna berdasarkan severity (1-5) |
| **Keputusan** | Badge 🟢 **Layak** + confidence % / 🔴 **Tidak Layak** + confidence % / ⚪ **Belum diprediksi** |
| **Aksi** | 3 tombol: ✏️ Edit, 🔄 Prediksi Ulang, 🗑️ Hapus |

**Penjelasan Badge Severitas:**
- Setiap kategori (Penghasilan, Pekerjaan, Aset) memiliki skor 1-5
- Skor 5 = merah (paling rentan) → 4 = oranye → 3 = kuning → 2 = biru muda → 1 = abu-abu (paling mampu)
- Warna badge otomatis menyesuaikan dengan tingkat keparahan

### 4.4 Paginasi

- **10 data per halaman**
- Informasi: "Menampilkan data X - Y dari Z calon"
- Navigasi halaman: ◀ [1] [2] [3] ... [N] ▶
- Nomor halaman aktif diberi highlight
- Jika hanya 1 halaman, paginasi tidak muncul

### 4.5 State Kosong

Jika belum ada data sama sekali:
- Ikon kotak kosong (📥)
- Pesan: "Belum Ada Data Calon Penerima"
- Deskripsi: "Silakan tambah data pertama untuk memulai proses klasifikasi SVM."
- Tombol: **"Tambah Data Pertama"**

### 4.6 Modal Konfirmasi Hapus

Ketika mengklik tombol 🗑️ Hapus:
1. Muncul modal konfirmasi dengan ikon peringatan ⚠️
2. Pesan: "Hapus data [nama calon]? Tindakan ini tidak dapat dibatalkan."
3. Dua tombol: **Batal** (abu-abu) | **Hapus** (merah)
4. Data yang dihapus termasuk **hasil keputusan** terkait (cascade delete)

---

## 5. CRUD Calon Penerima

### 5.1 Tambah Calon Baru

**Akses:** `/calon/tambah` atau klik menu **"Tambah Calon"** di sidebar.

**Form Input:**

| Field | Tipe | Wajib | Keterangan |
|-------|------|-------|------------|
| **Nama Kepala Keluarga** | Text input | ✅ | Maks 100 karakter |
| **NIK** | Text input | ✅ | 16 digit angka, harus unik |
| **Pilih Wilayah** | Autocomplete search | ❌ | Cari desa/kecamatan/kabupaten (min 2 huruf) |
| **Alamat Detail** | Text input | ✅ | RT/RW, Jalan, atau Dusun (maks 255 karakter) |
| **Penghasilan per Bulan** | Dropdown kustom | ✅ | 5 pilihan Desil |
| **Pekerjaan** | Dropdown kustom | ✅ | 5 pilihan pekerjaan |
| **Kepemilikan Aset** | Dropdown kustom | ✅ | 5 pilihan aset |
| **Komponen Keluarga** | Toggle switches | ❌ | 5 komponen (Ibu Hamil, Anak Usia Dini, Anak Sekolah, Disabilitas, Lansia) |

**Fitur Autocomplete Wilayah:**
1. Ketik minimal **2 huruf** — sistem akan otomatis mencari wilayah (debouce 300ms)
2. Hasil pencarian muncul sebagai dropdown dengan informasi: NAMA (TINGKAT), Kode wilayah
3. Pilih hasil yang sesuai — sistem otomatis mengisi 4 field hidden (provinsi, kabupaten, kecamatan, desa)
4. Input akan menampilkan format: "Desa, Kecamatan, Kabupaten, Provinsi"

**Banner Info (hanya di halaman Tambah, tidak di Edit):**
Muncul alert biru: "Gunakan fitur **Import Excel/CSV** untuk memasukkan data dalam jumlah besar sekaligus." dengan tombol "Import Data".

**Panel Panduan Input (sidebar kanan):**
Berisi daftar 8 atribut yang dianalisis SVM dan penjelasan singkat tentang proses klasifikasi.

**Proses Setelah Submit:**
1. Data divalidasi (panjang teks, XSS sanitasi)
2. Skor ordinal dihitung otomatis
3. Data disimpan ke database
4. Model SVM langsung memprediksi
5. Hasil prediksi disimpan ke tabel `hasil_keputusan`
6. Flash message muncul: ✅ "Data berhasil disimpan. Hasil: Layak (confidence: 98.4%)"

**Jika model tidak tersedia:** Data tetap tersimpan, tetapi muncul peringatan "Data disimpan (model belum di-load, prediksi belum jalan)".

### 5.2 Edit Calon

**Akses:** Klik tombol ✏️ Edit di baris data calon.

- Form yang muncul sama persis dengan form tambah
- Semua field terisi dengan data yang sudah ada (pre-filled)
- Setelah disimpan, sistem akan **re-prediksi** otomatis dengan data terbaru
- Flash message: "Data diupdate. Hasil: Layak"

### 5.3 Prediksi Ulang

**Akses:** Klik tombol 🔄 Prediksi Ulang di baris data calon.

Fungsi ini berguna jika:
- Model SVM baru di-update (retrain)
- Admin ingin memastikan hasil prediksi tetap konsisten

Proses:
1. Membaca data calon yang sudah ada di database
2. Menjalankan ulang prediksi SVM
3. Memperbarui field `hasil_prediksi`, `label_prediksi`, `probabilitas`
4. Flash message: "Prediksi ulang berhasil: Layak"

### 5.4 Hapus Calon

**Akses:** Klik tombol 🗑️ Hapus di baris data calon.

- Muncul modal konfirmasi Bootstrap
- Data calon + data hasil keputusan akan dihapus permanen
- Flash message: "Data berhasil dihapus."

> ⚠️ **Peringatan:** Tindakan ini tidak dapat dibatalkan. Tidak ada fitur recycle bin / trash.

---

## 6. Import Data Massal (Bulk Import)

**Akses:** `/calon/import` atau klik tombol **"Import"** di halaman Data Calon, atau klik link banner di halaman Tambah Calon.

### 6.1 Persiapan File

**Format yang didukung:**
- Microsoft Excel (`.xlsx`, `.xls`)
- CSV (`.csv`)

**Template:**
- Download template Excel via tombol **"Download Template Excel"**
- Template berisi:
  - Baris 1: **Header** (nama kolom) — JANGAN DIHAPUS
  - Baris 2: **Contoh data** (bisa ditimpa)
  - Panduan pengisian di bagian bawah
  - Sheet "Petunjuk" dengan panduan lengkap

### 6.2 Kolom dalam Template

| Kolom | Status | Keterangan |
|-------|--------|------------|
| `nama` | ✅ **Wajib** | Nama Kepala Keluarga |
| `nik` | ✅ **Wajib** | NIK (16 digit angka, unik) |
| `alamat` | ✅ **Wajib** | Alamat lengkap |
| `provinsi` | ❌ Opsional | Provinsi |
| `kabupaten` | ❌ Opsional | Kabupaten |
| `kecamatan` | ❌ Opsional | Kecamatan |
| `desa_kelurahan` | ❌ Opsional | Desa/Kelurahan |
| `penghasilan` | ✅ **Wajib** | Kategori Desil (sesuai daftar) |
| `pekerjaan` | ✅ **Wajib** | Kategori pekerjaan (sesuai daftar) |
| `kepemilikan_aset` | ✅ **Wajib** | Kategori aset (sesuai daftar) |
| `ibu_hamil` | ❌ Opsional | YA/TIDAK, 1/0, Ada/Tidak |
| `anak_usia_dini` | ❌ Opsional | YA/TIDAK, 1/0, Ada/Tidak |
| `anak_sekolah` | ❌ Opsional | YA/TIDAK, 1/0, Ada/Tidak |
| `disabilitas` | ❌ Opsional | YA/TIDAK, 1/0, Ada/Tidak |
| `lansia` | ❌ Opsional | YA/TIDAK, 1/0, Ada/Tidak |

### 6.3 Kolom Alias (CSV dari Lapangan)

Sistem secara otomatis mengenali kolom alternatif:
| Nama Kolom Alternatif | Dipetakan Ke |
|----------------------|--------------|
| `kepala_keluarga` | `nama` |
| `aset` | `kepemilikan_aset` |
| `hamil` | `ibu_hamil` |
| `aud` | `anak_usia_dini` |
| `jenis_kelamin` | ⛔ Diabaikan |
| `nik` | `nik` |
| `status` | ⛔ Diabaikan |

### 6.4 Nilai Boolean yang Diterima

Komponen sosial (ibu_hamil, anak_usia_dini, dll) menerima berbagai format:

| Format | Arti |
|--------|------|
| `YA`, `Ya`, `ya`, `y`, `Y` | ✅ True |
| `1`, `True`, `true` | ✅ True |
| `Ada`, `ada` | ✅ True |
| `✔` | ✅ True |
| `TIDAK`, `Tidak`, `tidak`, `t`, `T` | ❌ False |
| `0`, `False`, `false` | ❌ False |
| `None`, `none` | ❌ False |
| `(kosong)` | ❌ False |

### 6.5 Alias Nilai Kategorikal

Sistem otomatis menormalisasi label singkat ke label baku:

**Penghasilan:**
| Input (dari CSV) | Akan Menjadi |
|-----------------|--------------|
| `Desil 1` | `Desil 1 (< Rp.500.000)` |
| `Desil 2` | `Desil 2 (Rp.600.000 - Rp.700.000)` |
| `Desil 3` | `Desil 3 (Rp.800.000 - Rp.900.000)` |
| `Desil 4` | `Desil 4 (Rp.1.000.000 - Rp.1.200.000)` |
| `Desil 5` | `Desil 5 (Rp.1.300.000 - Rp.1.500.000)` |

**Kepemilikan Aset:**
| Input (dari CSV) | Akan Menjadi |
|-----------------|--------------|
| `tidak memiliki aset` | `Tidak Memiliki Aset` |
| `memiliki motor dengan harga jual rendah` | `Memiliki Motor (harga jual rendah)` |
| `memiliki motor dengan harga jual tinggi` | `Memiliki Motor (harga jual tinggi)` |
| `memiliki mobil atau tanah/kebun` | `Memiliki Mobil atau Tanah/Kebun` |
| `memiliki mobil dan tanah/kebun` | `Memiliki Mobil dan Tanah/Kebun` |

### 6.6 Proses Import

1. Upload file → muncul konfirmasi di modal Bootstrap
2. Klik **"Ya, Import"** → tombol berubah menjadi spinner "Memproses..."
3. Sistem membaca file, memvalidasi setiap baris
4. Baris valid → **langsung disimpan + diprediksi otomatis**
5. Baris tidak valid → **dilewati** + error dicatat

**Hasil:**
- ✅ Flash message hijau: "Import berhasil: N data tersimpan dan diprediksi otomatis."
- ⚠️ Flash message kuning (maks 5 error pertama): "Baris X: [pesan error]"
- Jika lebih dari 5 error: "... dan M error lainnya."
- ℹ️ Jika file kosong: "File kosong atau tidak ada data yang diproses."

### 6.7 Validasi Per Baris

Error yang mungkin muncul:
- "Baris X: Nama tidak boleh kosong"
- "Baris X: Alamat tidak boleh kosong"
- "Baris X: Penghasilan '[value]' tidak valid. Pilih: [daftar pilihan]"
- "Baris X: Pekerjaan '[value]' tidak valid. Pilih: [daftar pilihan]"
- "Baris X: Aset '[value]' tidak valid. Pilih: [daftar pilihan]"

### 6.8 Keamanan Upload File

Sistem memvalidasi file upload dengan 3 lapis:
1. **Ekstensi** — hanya .xlsx, .xls, .csv
2. **MIME type** — memeriksa content-type header
3. **Magic bytes** — memeriksa signature file (PK\x03\x04 untuk xlsx, D0CF11E0 untuk xls)

---

## 7. Export Data (Bulk Export)

**Akses:** `/calon/export` atau klik menu **"Export Data"** di sidebar, atau tombol **"Export"** di halaman Data Calon.

### 7.1 Format File

| Format | Ikon | Keterangan |
|--------|------|------------|
| **Excel (.xlsx)** | 📊 | Tampilan rapi, multi-kolom |
| **CSV (.csv)** | 📄 | Lebih ringan, mudah diolah dengan aplikasi statistik |

### 7.2 Filter Export

**1. Filter Pencarian:**
- Cari berdasarkan nama atau alamat (text input)

**2. Filter Rentang Waktu:**
- Dari Tanggal / Sampai Tanggal (date picker)
- **Tombol Cepat (Quick Buttons):**
  - 🗓️ **7 Hari Terakhir**
  - 🗓️ **30 Hari**
  - 🗓️ **3 Bulan**
  - 🗓️ **6 Bulan**
  - 🗓️ **1 Tahun**
  - ❌ **Hapus Filter** (reset tanggal)

**3. Filter Hasil Keputusan (Radio Button):**
- 🔘 Semua
- 🔘 **Layak** ✅
- 🔘 **Tidak Layak** ❌

### 7.3 Pemilihan Kolom

**24 kolom** dapat dipilih/deselect:

| Grup | Kolom |
|------|-------|
| **Identitas** | ID, Nama, Alamat |
| **Wilayah** | Provinsi, Kabupaten, Kecamatan, Desa/Kelurahan |
| **Kriteria** | Penghasilan, Pekerjaan, Kepemilikan Aset |
| **Komponen Sosial** | Ibu Hamil, Anak Usia Dini, Anak Sekolah, Disabilitas, Lansia |
| **Skor Ordinal** | Skor Penghasilan, Skor Pekerjaan, Skor Aset, Skor Ibu Hamil, Skor Anak Usia Dini, Skor Anak Sekolah, Skor Disabilitas, Skor Lansia |
| **Hasil** | Keputusan (Layak/Tidak), Probabilitas (%) |
| **Waktu** | Tanggal Input, Tanggal Prediksi |
| **Petugas** | Oleh (Importir/Petugas) |

**Tombol bantuan:**
- ✅ **Pilih Semua** (centang semua kolom)
- ❌ **Hapus Semua** (uncentang semua)

### 7.4 Validasi & Proses Export

- **Jika tidak ada kolom dipilih:** Muncul modal peringatan "Pilih minimal satu kolom untuk di-export"
- **Proses:** Overlay loading muncul dengan spinner ⏳ "Sedang memproses export..."
- **Otomatis:** File langsung terdownload setelah selesai
- **Overlay bisa ditutup** dengan klik tombol "Tutup (jika download sudah selesai)" atau klik di luar area overlay
- **Auto-hide:** Overlay otomatis hilang setelah 15 detik (fallback)

### 7.5 Tips Export

- Export Excel mendukung banyak kolom dengan tampilan lebih rapi
- Export CSV lebih ringan dan mudah diolah dengan aplikasi statistik (SPSS, Excel, dll)
- Gunakan filter waktu untuk membuat laporan periodik (bulanan/triwulan)
- Kolom Probabilitas (%) menunjukkan confidence score prediksi SVM (0-100%)

---

## 8. Manajemen Admin (Superadmin)

> ⚠️ **Hanya untuk pengguna dengan role Superadmin.** Menu ini tidak muncul di sidebar untuk Admin biasa.

**Akses:** `/admin/users` atau klik menu **"Manajemen Admin"** di sidebar.

### 8.1 Daftar Admin

Tabel menampilkan:
| Kolom | Isi |
|-------|-----|
| **#** | Nomor urut |
| **Nama Lengkap** | Nama user (bold) |
| **Username** | Badge username dengan font monospace |
| **Peran (Role)** | 🟢 **Superadmin** (badge hijau dengan ikon perisai) atau 🔵 **Admin** (badge abu-abu dengan ikon orang) |
| **Tanggal Terdaftar** | Format: DD/MM/YYYY HH:MM |
| **Aksi** | 👁️ **Detail** | 🗑️ **Hapus** (kecuali diri sendiri) |

**Catatan:**
- User yang sedang login ditandai dengan teks "Aktif (Anda)" (tidak bisa dihapus)
- Tidak ada aksi edit untuk admin — hanya tambah, lihat detail, dan hapus

### 8.2 Tambah Admin Baru

**Akses:** Klik tombol **"Tambah Admin"** di halaman Manajemen Admin.

**Form:**
| Field | Tipe | Wajib | Keterangan |
|-------|------|-------|------------|
| **Nama Lengkap** | Text | ✅ | Contoh: Budi Santoso |
| **Username** | Text | ✅ | Contoh: budi123 (harus unik) |
| **Password** | Password | ✅ | Minimal 6 karakter (6 karakter minimal untuk entri, tapi validasi tetap 8+ huruf+angka) |
| **Hak Akses (Role)** | Dropdown kustom | ✅ | Admin (Pendamping Biasa) atau Superadmin (Administrator Utama) |

**Validasi:**
- Username duplikat: "Username 'xxx' sudah terdaftar."
- Password lemah: "Password minimal harus 8 karakter." / "Password harus mengandung minimal 1 huruf." / "Password harus mengandung minimal 1 angka."
- Role tidak valid: "Role tidak valid."

**Default:** User baru dibuat dengan `must_change_password=True` — mereka WAJIB ganti password saat login pertama.

### 8.3 Detail Admin

**Akses:** Klik tombol **"Detail"** di baris user.

Menampilkan informasi lengkap:
- Avatar ikon orang
- Nama lengkap
- @username
- ID User
- Peran (Role) dengan badge
- Tanggal terdaftar
- Update terakhir

### 8.4 Hapus Admin

**Akses:** Klik tombol **"Hapus"** di baris user.

- Muncul modal konfirmasi Bootstrap
- Sistem mencegah menghapus diri sendiri (user yang sedang login)
- Flash message: "User admin 'xxx' berhasil dihapus."

---

## 9. Halaman Tentang Sistem

**Akses:** `/about` atau klik menu **"Tentang"** di sidebar.

### 9.1 Informasi Sistem

| Informasi | Nilai |
|-----------|-------|
| Nama Sistem | **SPK PKH - SVM** |
| Algoritma Klasifikasi | **Support Vector Machine (SVM)** |
| Kernel Trick | **RBF** (Radial Basis Function) |
| Web Framework | Flask (Python 3) & SQLite 3 |
| Status Model | 🟢 **Model Aktif** / 🔴 **Model Nonaktif** |

### 9.2 Detail Performa Model

**Metrik Utama (4 kartu):**

| Metrik | Nilai (dataset real 318 data) |
|--------|-------------------------------|
| 🎯 **Akurasi** | **98.4%** |
| 🎯 **Presisi** | **97.5%** |
| 🎯 **Recall** | **100%** |
| 🎯 **F1-Score** | **0.987** |

**Parameter Terbaik (dari GridSearchCV):**

| Parameter | Nilai |
|-----------|-------|
| **C** (Regularisasi) | 10 |
| **Gamma** | 0.01 |
| **Kernel** | RBF |

### 9.3 FAQ (5 Pertanyaan)

Accordion interaktif dengan pertanyaan:

1. **Apa fungsi utama dari Sistem SPK PKH - SVM ini?**
   → Membantu pendamping sosial memverifikasi kelayakan calon penerima PKH secara objektif.

2. **Bagaimana sistem ini memproses dan menilai data calon penerima?**
   → Setiap data dipetakan ke skor 1-5, dinormalisasi 0-1, lalu diproses SVM.

3. **Apa yang dimaksud dengan Confidence Score?**
   → Probabilitas keyakinan model saat memprediksi — semakin tinggi semakin meyakinkan.

4. **Apakah data calon penerima dapat diubah kembali?**
   → Ya. Edit data → otomatis prediksi ulang dengan hasil terbaru.

5. **Mengapa menggunakan dropdown Desil untuk penghasilan?**
   → Sesuai Keputusan Dirjen Linjamsos Kemensos, penghasilan dikelompokkan ke desil kesejahteraan.

### 9.4 Visualisasi Model

Dua gambar:

1. **Confusion Matrix** — Matriks 2×2: TP=39, TN=24, FP=1, FN=0
   - True Positive (Layak benar): 39
   - True Negative (Tidak Layak benar): 24
   - False Positive (Salah Layak): 1
   - False Negative (Salah Tidak Layak): 0

2. **EDA Visualizations** — Grafik analisis data eksploratori dari dataset training

### 9.5 Halaman Error Kustom

| Halaman | Pesan | Tombol |
|---------|-------|--------|
| **403** — Akses Ditolak | "Anda tidak memiliki izin untuk mengakses halaman ini." | Kembali ke Dashboard |
| **404** — Tidak Ditemukan | "Halaman yang Anda cari tidak tersedia atau telah dipindahkan." | Kembali ke Dashboard |
| **500** — Server Error | "Terjadi kesalahan internal. Silakan coba lagi atau hubungi administrator." | Kembali ke Dashboard |

---

## 10. Panduan Kategori & Kriteria

### 10.1 Penghasilan per Bulan (Desil Kesejahteraan)

| Kategori | Skor | Arti |
|----------|------|------|
| **Desil 1 (< Rp.500.000)** | **5** | 🟡 Paling berhak → penghasilan sangat rendah |
| **Desil 2 (Rp.600.000 - Rp.700.000)** | 4 | 🟠 Rentan |
| **Desil 3 (Rp.800.000 - Rp.900.000)** | 3 | 🟡 Menengah bawah |
| **Desil 4 (Rp.1.000.000 - Rp.1.200.000)** | 2 | 🔵 Menengah |
| **Desil 5 (Rp.1.300.000 - Rp.1.500.000)** | 1 | ⚪ Paling tidak berhak → penghasilan tertinggi |

### 10.2 Jenis Pekerjaan Kepala Keluarga

| Kategori | Skor | Arti |
|----------|------|------|
| **Tidak Bekerja** | **5** | 🟡 Paling berhak → tidak memiliki penghasilan |
| **Pekerja Bebas** | 4 | 🟠 Pekerjaan tidak tetap/harian |
| **Petani/Nelayan** | 3 | 🟡 Sektor informal |
| **Wiraswasta** | 2 | 🔵 Usaha mandiri |
| **PNS/Pegawai Tetap** | 1 | ⚪ Paling tidak berhak → penghasilan tetap |

### 10.3 Kepemilikan Aset

| Kategori | Skor | Arti |
|----------|------|------|
| **Tidak Memiliki Aset** | **5** | 🟡 Paling berhak → tanpa aset |
| **Memiliki Motor (harga jual rendah)** | 4 | 🟠 Motor bekas/murah |
| **Memiliki Motor (harga jual tinggi)** | 3 | 🟡 Motor bagus/baru |
| **Memiliki Mobil atau Tanah/Kebun** | 2 | 🔵 Aset bernilai |
| **Memiliki Mobil dan Tanah/Kebun** | 1 | ⚪ Paling tidak berhak → multi-aset |

### 10.4 Komponen Sosial (Boolean)

| Komponen | Skor jika Ya | Skor jika Tidak |
|----------|--------------|-----------------|
| Ibu Hamil | 1 | 0 |
| Anak Usia Dini (0-6 Th) | 1 | 0 |
| Anak Sekolah (SD-SMA) | 1 | 0 |
| Penyandang Disabilitas | 1 | 0 |
| Lanjut Usia (Lansia) | 1 | 0 |

### 10.5 Logika Scoring — Siapa yang Layak?

Semakin tinggi skor total (5 = paling rentan), semakin besar kemungkinan **Layak**.

Skor tinggi diperoleh jika:
- Penghasilan **Desil 1** (skor 5)
- **Tidak Bekerja** (skor 5)
- **Tidak Memiliki Aset** (skor 5)
- Memiliki komponen sosial: ibu hamil, anak usia dini, anak sekolah, disabilitas, lansia

---

## 11. Pemecahan Masalah (Troubleshooting)

### 11.1 Tidak Bisa Login

| Gejala | Penyebab | Solusi |
|--------|----------|--------|
| "Username atau password salah" | Kredensial salah | Cek username dan password, reset jika lupa |
| "Akun sementara dikunci..." | >10 gagal login | Tunggu beberapa menit, coba lagi |
| Tidak ada response sama sekali | Server tidak jalan | Jalankan `python app.py` di direktori web/ |
| Halaman putih/500 | Error server | Cek `app.log` di direktori web/ |

### 11.2 Model Tidak Tersedia

| Gejala | Penyebab | Solusi |
|--------|----------|--------|
| Badge merah "Model SVM: Tidak Tersedia" | File model .pkl tidak ada | Letakkan `svm_pkh_pipeline.pkl` di `models/` |
| Data tersimpan tapi tidak diprediksi | Model error saat load | Cek log: "Gagal load model: ..." |

### 11.3 Import Gagal

| Gejala | Penyebab | Solusi |
|--------|----------|--------|
| "Kolom wajib tidak ditemukan" | Header file tidak sesuai | Download template, sesuaikan header |
| "Baris X: ... tidak valid" | Nilai kategori salah | Cek daftar kategori yang valid |
| File tidak terupload | Format tidak didukung | Gunakan .xlsx, .xls, atau .csv |
| "File .xlsx tidak valid" | File rusak | Buka di Excel, save as baru |

### 11.4 Error Lainnya

| Gejala | Solusi |
|--------|--------|
| Data tidak muncul di tabel | Cek filter (mungkin terfilter) atau reset filter |
| Export tidak terdownload | Cek apakah kolom sudah dipilih (minimal 1) |
| Grafik dashboard kosong | Belum ada data di database |
| "CSRF token invalid" | Refresh halaman, CSRF token expired |
| Session berakhir tiba-tiba | Login ulang (session timeout 4 jam) |

### 11.5 Cara Memulai Ulang Aplikasi

1. Buka terminal/command prompt
2. Masuk ke direktori: `cd D:\JOKI\web`
3. Jalankan: `python app.py`
4. Buka browser: `http://localhost:5000`

### 11.6 Cara Membuat Database Baru (Reset)

1. Hapus file `spk_pkh.db` di folder `web/`
2. Jalankan `python app.py`
3. Database akan dibuat otomatis dengan akun default

---

## 12. Daftar Lengkap Route & Endpoint

### 12.1 Route Aplikasi

| Method | URL | Nama Route | Fungsi | Hak Akses |
|--------|-----|------------|--------|-----------|
| GET, POST | `/login` | `auth.login` | Halaman login | Publik |
| POST | `/logout` | `auth.logout` | Proses logout | Login |
| GET, POST | `/change-password` | `auth.change_password` | Ganti password | Login |
| GET | `/` | `dashboard.index` | Dashboard utama | Login |
| GET | `/api/analytics` | `dashboard.get_analytics_data` | API data grafik | Login |
| GET | `/calon` | `calon.daftar_calon` | Daftar calon + filter | Login |
| GET, POST | `/calon/tambah` | `calon.tambah_calon` | Tambah calon | Login |
| GET, POST | `/calon/<id>/edit` | `calon.edit_calon` | Edit calon | Login |
| POST | `/calon/<id>/hapus` | `calon.hapus_calon` | Hapus calon | Login |
| POST | `/calon/<id>/prediksi-ulang` | `calon.prediksi_ulang` | Prediksi ulang | Login |
| GET, POST | `/calon/import` | `calon.import_calon` | Import massal | Login |
| GET | `/calon/import/template` | `calon.download_template` | Download template | Login |
| GET, POST | `/calon/export` | `calon.export_calon` | Export data | Login |
| GET | `/api/daerah` | `calon.get_daerah` | API wilayah Indonesia | Login |
| GET | `/about` | `about.index` | Info sistem & metrik | Login |
| GET | `/admin/users` | `admin.list_users` | Daftar admin | Superadmin |
| GET, POST | `/admin/users/tambah` | `admin.tambah_user` | Tambah admin | Superadmin |
| GET | `/admin/users/<id>/detail` | `admin.detail_user` | Detail admin | Superadmin |
| POST | `/admin/users/<id>/hapus` | `admin.hapus_user` | Hapus admin | Superadmin |

### 12.2 API Endpoint (JSON)

| URL | Parameter | Response |
|-----|-----------|----------|
| `/api/analytics?type=wilayah&provinsi=...&kabupaten=...&kecamatan=...&desa_kelurahan=...&date_from=...&date_to=...` | Filter + tipe | `{labels, values, title}` |
| `/api/analytics?type=tren&scale=...&date_from=...&date_to=...` | Scale + tanggal | `{labels, values, title}` |
| `/api/analytics?type=komparasi&compare=period&period_a_start=...&period_a_end=...&period_b_start=...&period_b_end=...` | 2 periode | `{labels, values_a, values_b, label_a, label_b, title}` |
| `/api/analytics?type=komparasi&compare=criteria&criteria_type=...` | Tipe kriteria | `{labels, values, title}` |
| `/api/daerah?q=...&level=...&parent=...` | Pencarian | `[{kode, nama, level, fullname}]` |

### 12.3 Autentikasi API Internal

Semua endpoint (kecuali login) menggunakan:
- **Session-based auth** (tidak ada API token eksternal)
- **CSRF token** di semua form POST
- **Decorator** `@login_required` dan `@superadmin_required` untuk RBAC

---

## 📌 Ringkasan Cepat

### Navigasi Sidebar

| Menu | Ikon | Rute | Akses |
|------|------|------|-------|
| Dashboard | 🏠 | `/` | Semua |
| Data Calon | 👥 | `/calon` | Semua |
| Tambah Calon | ➕ | `/calon/tambah` | Semua |
| Export Data | 📥 | `/calon/export` | Semua |
| Manajemen Admin | 👤 | `/admin/users` | **Superadmin only** |
| Tentang | ℹ️ | `/about` | Semua |
| Ganti Password | 🔑 | `/change-password` | Semua (di sidebar footer) |
| Keluar | 🚪 | `/logout` POST | Semua (di sidebar footer) |

### Tombol Penting di Halaman Data Calon

```
[Tambah] [Import] [Export]     ← Header
  ✏️ [Edit]                     ← Aksi per baris
  🔄 [Prediksi Ulang]           ← Aksi per baris
  🗑️ [Hapus]                    ← Aksi per baris (dengan konfirmasi)
[Filter] [Reset]                ← Panel filter
```

### Default Login

```
Superadmin: admin / admin123
Admin:      user1 / user1123
```

---

*Dokumen panduan ini dibuat pada 7 Juli 2026 untuk mendampingi penggunaan Sistem Pendukung Keputusan Kelayakan Calon Penerima Bantuan PKH — Implementasi Algoritma SVM.*

*Fadhilah Lamangkona (F55120013) — Universitas Tadulako*
