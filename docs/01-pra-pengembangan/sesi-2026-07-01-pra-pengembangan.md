# Log Harian 01: Tahap Pra-Pengembangan
**Tanggal:** 1 Juli 2026
**Durasi:** ~3 jam

---

## Kegiatan yang Dilakukan

1. **Analisis Kebutuhan Sistem** — Mengidentifikasi kebutuhan fungsional dan teknis berdasarkan tujuan penelitian skripsi:
   - Membangun model machine learning berbasis Support Vector Machine (SVM) untuk klasifikasi kelayakan penerima Program Keluarga Harapan (PKH).
   - Mempersiapkan pengumpulan data training dari pendamping PKH Kecamatan Kasimbar.
   - Merencanakan integrasi model hasil training ke dalam aplikasi Sistem Pendukung Keputusan (SPK) berbasis web.
   - Merancang diagram pemodelan sistem (DFD, ERD, Flowchart) sebagai bagian utama dari laporan bab perancangan.

2. **Studi Literatur & Review Proposal Skripsi** — Membaca ulang draft proposal skripsi `Revisi_Fadhilah Lamangkona_F55120013.pdf` (49 halaman):
   - Menyelaraskan implementasi program dengan Bab 1-3 skripsi yang telah diujikan.
   - Memeriksa catatan dari dosen pembimbing (Dr. Deny Wiria Nugraha, S.T., M.Eng.).
   - Menentukan cakupan objek penelitian: 3 desa di Kecamatan Kasimbar (Desa Posona, Kasimbar Palapi, dan Posona Atas).
   - Memastikan kriteria biner kelayakan (Layak/Tidak Layak) menggunakan algoritma SVM.
   - Memetakan 8 kriteria utama yang digunakan: penghasilan, pekerjaan, kepemilikan aset, ibu hamil, anak usia dini, anak sekolah, disabilitas, dan lansia.

3. **Riset Dataset Publik di Kaggle** — Mencari dataset referensi:
   - Pencarian dataset PKH spesifik: tidak ditemukan dataset sekunder yang cocok secara langsung untuk kasus PKH lokal.
   - Dataset kemiskinan Indonesia: `ldausl/klasifikasi-tingkat-kemiskinan-di-indonesia` (data level kabupaten, kurang granular untuk analisis tingkat desa).
   - Dataset referensi struktur data: `frederickallensius/adult-income-modified` (32.562 baris, 18 kolom) digunakan sebagai studi banding pengolahan data numerik/kategorikal.
   - Kesimpulan: Memutuskan menggunakan dataset sintetis terlebih dahulu untuk merancang pipeline modeling dan prototype web, sambil mengurus perizinan penarikan data riil dari pendamping PKH.

4. **Penyusunan Rancangan Sistem**:
   - Menyusun dokumen spesifikasi kebutuhan sistem (fitur input data, proses klasifikasi, halaman dashboard).
   - Menggambar arsitektur sistem (DFD Level 0 & 1, ERD database, Flowchart proses klasifikasi SVM, dan komponen backend-frontend).
   - Membuat rencana implementasi proyek yang dibagi ke dalam beberapa fase pengerjaan mandiri.

5. **Inisialisasi Repositori**:
   - Menyiapkan struktur direktori proyek, termasuk folder `docs/` untuk menyimpan log harian pengembangan agar mempermudah penulisan Bab IV Skripsi.

---

## Keputusan Perancangan

| Aspek Keputusan | Opsi Terpilih | Justifikasi Akademis / Teknis |
|-----------|------|--------|
| **Teknologi Web** | Flask + SQLAlchemy + Bootstrap 5 | Flask sangat ringan, mudah diintegrasikan dengan model machine learning berbasis Python, cocok untuk proyek skala skripsi. |
| **Sistem Database** | SQLite | Bersifat portabel (single-file database), tanpa konfigurasi rumit, sehingga mudah dideploy saat demo sidang skripsi. |
| **Platform Eksperimen ML** | Kaggle Notebook | Menyediakan resource komputasi cloud gratis dan memudahkan pencatatan histori versi kode program. |
| **Ekspor Model** | joblib (.pkl) | Library standar pada ekosistem Python untuk menyimpan model scikit-learn dengan efisien. |
| **Strategi Dataset** | Dataset sintetis → retraining dengan data riil | Memungkinkan pengembangan kode program web dan modeling berjalan paralel selagi menunggu data riil selesai divalidasi. |
| **Struktur Dokumen** | Folder `docs/` per fase | Mempermudah penelusuran histori pengembangan saat penyusunan laporan skripsi. |

---

## Kendala & Solusi

| Kendala Teknis | Solusi |
|---------|--------|
| File PDF proposal skripsi korup saat diekstrak langsung | Menggunakan library Python `pdfminer.six` untuk mengekstrak isi teks penuh secara terstruktur. |
| Ketiadaan dataset publik spesifik PKH | Merancang script pembuat dataset sintetis berdasarkan sebaran kriteria yang diperoleh dari studi literatur penelitian sejenis. |
| Masalah pembacaan encoding teks proposal | Melakukan konversi ekspor teks ke encoding UTF-8 untuk menghindari hilangnya karakter saat dibaca parser program. |

---

## Rencana Tindak Lanjut

1. Menyelesaikan dokumen rancangan sistem dan merapikan diagram alur untuk draf bimbingan dosen.
2. Menghubungi pihak pendamping PKH Kecamatan Kasimbar untuk memproses pengambilan data riil.
3. Membuat script pembuat data sintetis untuk pengujian awal model.
4. Memulai eksperimen pembuatan model SVM pertama (baseline model) di Kaggle Notebook.

---

## Output Progres

- ✅ Dokumen spesifikasi kebutuhan sistem selesai disusun
- ✅ Diagram arsitektur sistem (DFD, ERD, Flowchart) siap
- ✅ Timeline rencana pengerjaan mandiri tersusun
- ✅ Struktur repositori dan folder `docs/` terinisialisasi
- ⏳ Eksperimen data sintetis dan modeling SVM (Tahap Selanjutnya)
- ⏳ Pengembangan aplikasi Flask (Tahap Selanjutnya)

---

## Retrospektif (Ditambahkan 3 Juli 2026)

Setelah melakukan audit pada 3 Juli 2026, beberapa keputusan awal ternyata **tidak sesuai** dengan kondisi riil dan **perlu direvisi**:

1. **Encoding otomatis (LabelEncoder)** — Awalnya saya menggunakan LabelEncoder karena belum memiliki dokumen resmi dari Tim PKH. Setelah mendapatkan dokumen resmi dari Pak Zainal (Ketua Tim SDM PKH Sulteng) pada 3 Juli, encoding diubah menjadi ordinal manual 1-5 sesuai indikator resmi karena encoding otomatis ternyata **tidak sesuai** dengan bobot kelayakan.
2. **StandardScaler** — Awalnya saya memilih ini karena merupakan standar dalam pipeline scikit-learn. Namun, setelah mendapat **revisi dari Pak Yazdi**, saya mengubahnya ke MinMaxScaler yang lebih cocok untuk data berjenis ordinal agar rentang nilai kriteria biner dan ordinal tetap konsisten.
3. **Atribut penghasilan sebagai angka rupiah** — Awalnya mengikuti format nominal rupiah pada dataset sintetis. Setelah dicocokkan dengan dokumen resmi, kriteria ini diubah menjadi kategori Desil (5 tingkatan) karena input rupiah mentah ternyata **tidak cocok** untuk model ini.
4. **Kolom anak_usia_dini, anak_sekolah, lansia sebagai integer** — Awalnya menyimpan kuantitas (jumlah anak/lansia). Ternyata dokumen resmi hanya menanyakan status biner "Ada atau Tidak", sehingga implementasi awal database **tidak sesuai** dan harus diubah menjadi biner.

Seluruh detail perubahan tersebut dibahas pada laporan gap analisis di [sesi-2026-07-03-audit-gap-analisis.md](../04-integrasi/sesi-2026-07-03-audit-gap-analisis.md).
