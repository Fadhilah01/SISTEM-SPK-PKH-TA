# Log Harian 03: Pengembangan Aplikasi Web SPK Menggunakan Flask
**Tanggal:** 2 Juli 2026
**Durasi:** ~2 jam

---

## Kegiatan yang Dilakukan

1. **Inisialisasi Proyek Flask** — Menyiapkan struktur folder `web/` serta menginstal dependensi dasar seperti Flask dan Flask-SQLAlchemy.
2. **Perancangan Model Database (SQLAlchemy)** — Membuat skema relasi database yang terdiri dari 2 tabel utama:
   - `CalonPenerima` (Menyimpan 11 atribut: nama, alamat, penghasilan, pekerjaan, kepemilikan aset, status ibu hamil, anak usia dini, anak sekolah, anggota disabilitas, lansia, dan waktu pembuatan data).
   - `HasilKeputusan` (Menyimpan log hasil prediksi: id_calon, hasil_prediksi, label_prediksi, nilai probabilitas, tanggal prediksi, dan petugas penginput).
3. **Pembuatan Layanan SVM Predictor** — Merancang kelas *Singleton* Python (`svm_predictor.py`) untuk memuat file model pipeline `.pkl` ke memori server saat web pertama kali dijalankan, guna menghemat resource server.
4. **Implementasi Routing Aplikasi (Routes)**:
   - `GET /` — Halaman utama dashboard (menampilkan visualisasi sebaran data, ringkasan jumlah penerima layak/tidak layak, dan metrik performa model).
   - `GET /calon` — Menampilkan tabel daftar seluruh calon penerima beserta status kelayakan hasil prediksi model.
   - `GET+POST /calon/tambah` — Form input data calon penerima baru yang langsung memicu proses klasifikasi otomatis oleh model SVM.
   - `GET+POST /calon/<id>/edit` — Fasilitas memperbarui data calon penerima yang memicu proses prediksi ulang otomatis.
   - `POST /calon/<id>/hapus` — Fungsi untuk menghapus baris data calon penerima dari database.
   - `POST /calon/<id>/prediksi-ulang` — Fasilitas memicu klasifikasi ulang secara manual terhadap data tertentu.
   - `GET /about` — Halaman informasi sistem dan panduan interpretasi model bagi pengguna.
5. **Pembuatan Halaman Antarmuka (HTML Templates)**:
   - `base.html` — Layout utama aplikasi menggunakan Bootstrap 5 (termasuk komponen navbar dan footer).
   - `dashboard.html` — Panel dashboard interaktif yang memuat informasi statistik kelayakan.
   - `calon.html` — Tabel data calon penerima dengan tombol aksi (edit, hapus, dan prediksi ulang).
   - `calon_form.html` — Halaman formulir input untuk merekam data kriteria calon penerima.
   - `about.html` — Halaman panduan teoretis sistem untuk mempermudah penjelasan alur kerja program saat demonstrasi sidang skripsi.

---

## Keputusan Pengembangan

| Aspek Keputusan | Opsi Terpilih | Justifikasi Teknis / Akademis |
|-----------|------|--------|
| **Framework Backend** | Flask | Flask memiliki struktur kode yang minimalis dan fleksibel, memudahkan proses integrasi file model machine learning `.pkl` dibandingkan framework yang lebih kompleks seperti Django. |
| **Sistem Database** | SQLite | SQLite menyimpan data dalam satu file lokal tunggal (`spk_pkh.db`), memudahkan pemindahan aplikasi antar-perangkat komputer saat demonstrasi program di hadapan dosen penguji. |
| **Pemuatan Model** | Pola Singleton | Memastikan file model berukuran besar hanya dimuat sekali ke dalam RAM saat server startup, bukan dimuat berulang-ulang setiap ada permintaan prediksi dari pengguna. |
| **Proses Klasifikasi** | Prediksi Otomatis | Model langsung berjalan memberikan prediksi status kelayakan sesaat setelah pengguna menekan tombol simpan pada form input data. |
| **Pustaka Front-End** | Bootstrap 5 | Pustaka CSS standar yang andal untuk mempercepat pembuatan desain antarmuka yang rapi dan responsif tanpa menulis banyak baris CSS manual. |

---

## Struktur File Aplikasi Web

```
web/
├── app.py                  ← Logika routing utama dan pengontrol halaman
├── config.py               ← Pengaturan konfigurasi database dan direktori model
├── models_db.py            ← Pendefinisian skema database SQLAlchemy
├── svm_predictor.py        ← Modul pemroses prediksi model SVM
├── requirements.txt        ← Daftar pustaka dependensi aplikasi
├── models/
│   └── svm_pkh_pipeline.pkl   ← File model biner SVM (baseline prototype)
├── static/
│   ├── css/style.css       ← Kumpulan gaya desain kustom
│   └── img/
│       ├── confusion_matrix.png   ← Gambar visualisasi performa model
│       └── eda_visualizations.png ← Gambar visualisasi sebaran data awal
├── templates/
│   ├── base.html           ← Kerangka utama halaman web
│   ├── dashboard.html      ← Antarmuka panel statistik
│   ├── calon.html          ← Antarmuka pengelolaan data calon
│   ├── calon_form.html     ← Formulir input data kriteria
│   └── about.html          ← Halaman informasi metode dan sistem
└── spk_pkh.db              ← File database SQLite (terbentuk otomatis)
```

---

## Kendala & Solusi

| Kendala Teknis | Solusi |
|---------|--------|
| Peringatan perbedaan versi pustaka scikit-learn antara lingkungan training dan lokal | Peringatan diabaikan sementara untuk kebutuhan pengujian fungsionalitas dasar. Pada tahap retraining menggunakan data riil, versi scikit-learn di lingkungan Kaggle dan lokal web akan diselaraskan sepenuhnya. |
| Kegagalan encoding karakter unicode khusus pada terminal sistem operasi Windows | Menghapus penulisan karakter emoji khusus pada log keluaran server dan menggantinya dengan karakter standar ASCII. |

---

## Rencana Tindak Lanjut

1. Menjalankan pengujian fungsionalitas dasar seluruh halaman web secara lokal.
2. Melakukan pengujian alur kerja penambahan data calon penerima baru hingga menghasilkan keluaran prediksi status kelayakan.
3. Melengkapi teks panduan teori SVM pada halaman `/about` untuk kebutuhan demo sidang.
4. Mempersiapkan struktur kode integrasi database agar siap diperbarui ketika format data riil dari dinas sosial diimplementasikan.

---

## Output Progres

- ✅ Struktur proyek web Flask terbentuk
- ✅ Skema database relasional (tabel calon penerima dan keputusan) siap digunakan
- ✅ 5 halaman utama antarmuka sistem selesai dirancang
- ✅ Modul integrasi prediksi SVM berfungsi baik secara lokal
- ✅ Fungsi CRUD dasar (Create, Read, Update, Delete) berjalan lancar
- ⏳ Integrasi grafik interaktif Chart.js (Fase Berikutnya)
- ⏳ Retraining dan pembaruan model menggunakan data riil (Fase Berikutnya)

---

## Retrospektif (Ditambahkan 3 Juli 2026)

Setelah audit pada 3 Juli 2026, beberapa komponen web yang sudah dibangun ternyata **tidak sesuai** dengan kriteria resmi dan **perlu diperbarui**:

1. **Form Input (`calon_form.html`):**
   - **Kriteria Penghasilan:** Saat ini menggunakan input nominal angka Rupiah biasa. Kriteria ini **tidak cocok** dan harus diganti menjadi dropdown 5 kategori Desil.
   - **Kriteria Pekerjaan & Aset:** Opsi dropdown saat ini terlalu banyak (11 pilihan pekerjaan). Ini **tidak sesuai** dan harus diringkas menjadi 5 kategori resmi.
   - **Komponen Sosial:** Saat ini menginput kuantitas jumlah anak/lansia. Input ini **tidak sesuai** dan harus diubah menjadi pilihan biner (checkbox Ada/Tidak).

2. **Skema Database (`models_db.py`):**
   - Kriteria `penghasilan` bertipe float masih dipertahankan untuk menyimpan nominal rupiah mentah, namun perlu ditambahkan kolom `penghasilan_skor` (skor desil 1-5) agar model dapat membacanya.
   - Tipe data untuk `anak_usia_dini`, `anak_sekolah`, dan `lansia` yang awalnya integer (jumlah) ternyata **tidak sesuai** dan harus diubah menjadi Boolean (biner).

3. **SVM Predictor (`svm_predictor.py`):**
   - Kode awal menggunakan `LabelEncoder` yang di-load dari file `.pkl`. Skema ini **tidak sesuai** dan harus dihapus karena input web sudah langsung berupa skor ordinal (1-5). Logic prediksi disederhanakan menjadi: `input skor -> scale (MinMaxScaler) -> predict`.

4. **Variabel Dropdown di Controller (`app.py`):**
   - Variabel daftar `pekerjaan_list` dan `aset_list` di-update agar sesuai dengan 5 kategori pilihan resmi dinas sosial.

Seluruh revisi komponen web ini akan dikerjakan bersamaan dengan proses retraining model menggunakan dataset riil.
