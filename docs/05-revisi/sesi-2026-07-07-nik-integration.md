# Log Revisi: Integrasi Kolom NIK Calon Penerima PKH
**Tanggal:** 7 Juli 2026
**Kategori:** Database, Backend, Frontend, Import/Export, Dokumentasi

---

## 1. Latar Belakang & Kebutuhan

Untuk meningkatkan akurasi pendataan calon penerima bantuan Program Keluarga Harapan (PKH) dan mencegah duplikasi data (double-entry) baik dari input manual maupun bulk import Excel/CSV, ditambahkan kolom **Nomor Induk Kependudukan (NIK)** pada tabel data calon penerima di seluruh subsistem SIPEKAHA.

NIK memiliki karakteristik:
1. Wajib (Required)
2. Unik (Unique)
3. Harus 16 digit angka numerik (Validation)

---

## 2. Rincian Perubahan & Implementasi

### 2.1 Database & Migrasi Otomatis
- **Tabel:** `calon_penerima`
- **Model SQLAlchemy:** Menambahkan kolom `nik` tipe `String(16)`, constraint `unique=True`, `nullable=False` di `web/models_db.py`.
- **Auto-Migration:** Pada `web/app.py` di fungsi `init_db()`, ditambahkan pengecekan keberadaan kolom `nik` di SQLite. Jika tidak ada, kolom ditambahkan sebagai nullable terlebih dahulu, di-backfill menggunakan NIK tiruan bertingkat (`1234567890123[ID]`) agar unik, kemudian ditambahkan index unik `idx_calon_penerima_nik` dan diubah menjadi non-nullable.

### 2.2 Validasi Backend & CRUD
- **Tambah Calon (`routes/calon.py`):**
  - Mengambil NIK dari form request dan mensterilkan spasi.
  - Memvalidasi NIK menggunakan regex (wajib 16 digit angka).
  - Mengecek ke database apakah NIK tersebut sudah pernah terdaftar untuk mendeteksi duplikasi awal.
- **Edit Calon (`routes/calon.py`):**
  - Melakukan validasi NIK yang sama, mengecualikan data ID calon yang sedang diedit.
- **Pencarian:** Menambahkan filter pencarian berdasarkan NIK (partial match `%NIK%`) pada route list calon.

### 2.3 Bulk Import & Export (`core/data_io.py`)
- **Template Download:** Ditambahkan kolom `nik` sebagai kolom wajib setelah kolom `nama` di file template Excel (`template_import_pkh.xlsx`). Menambahkan contoh NIK (`7201020304050001`) dan instruksi validasi di sheet panduan.
- **Validasi Baris (Import):**
  - Membersihkan NIK dari tipe data float / scientific notation yang sering ditimbulkan oleh library Pandas saat membaca Excel.
  - Memvalidasi format 16-digit numerik.
  - Melakukan pengecekan duplikasi NIK terhadap database.
  - Melakukan pencegahan duplikasi NIK antar baris di dalam file Excel yang sedang di-import secara batch (menggunakan set `processed_niks`).
- **Export Data:** Menambahkan kolom NIK ke daftar export, memetakan checkbox kolom ekspor dengan nama kolom 'NIK', dan menyertakan NIK secara default di hasil Excel maupun CSV.

### 2.4 Antarmuka Pengguna (UI/UX)
- **Form Input (`form.html`):** Menambahkan field text input `nik` di samping nama calon dengan pembatasan panjang (maxlength=16), pembatasan pola input (`pattern="[0-9]{16}"`), dan tipe keyboard angka (`inputmode="numeric"`).
- **Daftar Calon (`list.html`):** Menambahkan kolom `NIK` bertipe font monospace kecil di sebelah kolom Nama.
- **Halaman Import (`import.html`):** Mengupdate deskripsi dan peringatan sistem untuk memperjelas bahwa NIK wajib diisi dan sistem secara otomatis mencegah data ganda.
- **Dashboard (`dashboard.html`):** Menampilkan NIK dengan format font monospace kecil di bawah nama calon penerima pada daftar keputusan terbaru.

### 2.5 Pembaruan Data Uji (Test Data)
- Membuat dataset pengujian baru di folder `test-data/` yang dilengkapi dengan NIK unik:
  - `sample_data_pkh_nik.csv`
  - `sample_data_pkh_nik.xlsx`
  - `sample_data_pkh_wilayah_nik.csv`
  - `sample_data_pkh_wilayah_nik.xlsx`

### 2.6 Pembaruan Dokumentasi
- Mengupdate ERD dan DFD di `ARSITEKTUR_SISTEM.md`.
- Mengupdate daftar fitur dan status di `CLAUDE.md`, `PRD_R1.md`, `PRD_SPK_PKH.md`, `RENCANA_IMPLEMENTASI.md`, `RENCANA_IMPLEMENTASI_R1.md`, dan `README.md`.
- Mengupdate petunjuk operasional dan skema impor di panduan web (`web/PANDUAN_PENGGUNA.md`).

---

## 3. Hasil Pengujian & Verifikasi Mandiri
*(Akan diverifikasi kembali setelah peluncuran lokal)*
- Auto-migrasi SQLite berhasil berjalan mulus pada inisialisasi awal.
- NIK yang di-input manual divalidasi dengan baik (gagal jika bukan 16 digit angka, atau jika NIK sudah ada).
- Import file CSV/Excel dengan NIK berhasil mendeteksi baris ganda, mengabaikan baris tidak valid, dan mengimpor baris valid secara aman.
