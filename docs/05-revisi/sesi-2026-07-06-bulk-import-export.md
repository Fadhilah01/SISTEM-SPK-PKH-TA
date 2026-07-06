# Sesi 9 — Implementasi Fitur Import & Export Data (6 Juli 2026)

## Yang Dikerjakan

Pada sesi ini saya mengimplementasikan fitur import data secara massal (bulk) menggunakan file Excel/CSV dan fitur export data dengan berbagai opsi filter. Tujuannya agar admin Dinsos tidak perlu input data satu per satu jika jumlah calon penerima banyak, dan bisa membuat laporan data secara periodik dengan mudah.

### A. Fitur Import Data (Excel/CSV)
1. **Upload file** — Admin bisa upload file `.xlsx`, `.xls`, atau `.csv` yang berisi banyak data calon sekaligus
2. **Validasi otomatis per baris** — Setiap baris diperiksa kelengkapan dan kesesuaian kategorinya. Jika ada baris yang salah, baris tersebut dilewati tapi baris lainnya tetap diproses
3. **Input boolean fleksibel** — Kolom seperti "Ibu Hamil", "Lansia", dll bisa diisi dengan berbagai format: YA/TIDAK, 1/0, Ada/Tidak — sistem akan otomatis mengenali
4. **Prediksi otomatis** — Setelah data tersimpan, setiap calon langsung diprediksi kelayakannya oleh model SVM
5. **Template Excel** — Saya sediakan template yang bisa di-download, lengkap dengan panduan pengisian dan daftar kategori yang valid
6. **Laporan hasil import** — Admin akan melihat notifikasi berapa data yang berhasil import dan berapa yang gagal

### B. Fitur Export Data (Excel/CSV)
1. **Filter berdasarkan waktu** — Admin bisa export data dalam rentang waktu tertentu:
   - 7 hari terakhir
   - 30 hari
   - 3 bulan
   - 6 bulan
   - 1 tahun
   - Atau tentukan tanggal sendiri
2. **Filter hasil keputusan** — Pilih mau export semua data, hanya yang Layak, atau hanya yang Tidak Layak
3. **Pilih kolom yang di-export** — Ada 24 kolom, admin bisa centang kolom mana saja yang mau dimasukkan ke file
4. **Dua format file** — Excel (.xlsx) untuk laporan rapi, atau CSV (.csv) untuk olah data lanjutan
5. **Nama file otomatis** — File yang di-download otomatis bernama `data_pkh_[filter]_[tanggal].xlsx`

### C. Navigasi & Tampilan
- Di halaman **Tambah Calon**, saya tambahkan informasi dan tombol yang mengarahkan ke halaman import jika ingin input data banyak sekaligus
- Di halaman **Data Calon**, ada tombol Import dan Export untuk akses cepat
- Saat proses import, muncul modal konfirmasi dulu sebelum data benar-benar diproses
- Tombol export akan disable sementara dan menampilkan spinner saat proses berjalan

## Keputusan yang Diambil

| Keputusan | Alasan |
|-----------|--------|
| Validasi per baris, bukan all-or-nothing | Data real bisa mencapai ribuan baris — tidak adil jika satu error menghapus semua |
| Support format boolean fleksibel | Admin Dinsos terbiasa dengan berbagai cara input (YA/TIDAK/1/0/Ada/Tidak) |
| Gunakan openpyxl (bukan library lain) | Bisa membuat file Excel dengan styling profesional (font, warna header, border) |
| Export tanpa menyimpan file sementara | Lebih aman, tidak ada sampah file di server |
| Filter kolom pakai checkbox | Admin bisa custom file export sesuai kebutuhan laporan masing-masing |
| Tombol quick date (7h/30h/3bl/6bl/1th) | Memudahkan pembuatan laporan periodik tanpa harus isi tanggal manual |
| Template Excel 2 sheet (data + petunjuk) | Satu file lengkap — langsung bisa pakai tanpa baca manual terpisah |

## Kendala & Solusi

| Kendala | Solusi |
|---------|--------|
| openpyxl belum terinstall di lingkungan | Tambah ke requirements.txt |
| CSV tidak terbuka rapi di Excel jika tanpa BOM | Gunakan encoding utf-8-sig (BOM) |
| Perlu styling profesional untuk template | openpyxl menyediakan Font, PatternFill, Border, Alignment |

## Perubahan dari Rencana Awal
Tidak ada perubahan signifikan. Semua fitur berjalan sesuai rencana.

## Output Sesi
1. **File baru:** `core/data_io.py` — Service untuk import & export data
2. **File baru:** `templates/calon_import.html` — Halaman upload file import
3. **File baru:** `templates/calon_export.html` — Halaman export dengan filter
4. **File baru:** `static/js/import.js` — Script untuk halaman import
5. **File baru:** `static/js/export.js` — Script untuk halaman export
6. **File diubah:** `routes/calon.py` — Penambahan 3 route baru
7. **File diubah:** `templates/calon_form.html` — Penambahan navigasi ke import
8. **File diubah:** `templates/calon.html` — Penambahan tombol import/export
9. **File diubah:** `templates/base.html` — Penyesuaian menu navigasi
10. **File diubah:** `requirements.txt` — Penambahan openpyxl

### Route Baru

| Method | Endpoint | Fungsi |
|--------|----------|--------|
| GET/POST | `/calon/import` | Mengupload & memproses file import |
| GET | `/calon/import/template` | Mendownload template Excel |
| GET/POST | `/calon/export` | Export data dengan filter |

### Alur Import
```
Upload file → Validasi header → Proses setiap baris:
  ├─ Cek kelengkapan nama & alamat
  ├─ Cek kesesuaian kategori (penghasilan, pekerjaan, aset)
  ├─ Konversi boolean (YA/TIDAK → True/False)
  ├─ Hitung skor ordinal (1-5)
  ├─ Simpan ke database
  └─ Prediksi SVM → simpan hasil kelayakan
→ Tampilkan ringkasan: berapa sukses, berapa gagal
```

### Alur Export
```
Pilih filter (waktu, hasil, kolom, format) →
Sistem query database sesuai filter →
Buat file Excel/CSV →
Download otomatis
```

### Tampilan Halaman Import
Halaman import terdiri dari form upload file, link download template, dan panel informasi yang menjelaskan proses import beserta persyaratan file.

### Tampilan Halaman Export
Halaman export menyediakan berbagai opsi filter: format file (Excel/CSV), pencarian nama/alamat, rentang waktu dengan quick buttons, filter hasil keputusan, dan pilihan kolom yang akan di-export.
