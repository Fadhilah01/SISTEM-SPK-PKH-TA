# Log Sesi: Penambahan Modul Perangkingan Confidence Score SVM

**Tanggal:** 22 Juli 2026  
**Topik:** Fitur Perangkingan Kriteria Penerima Bantuan PKH Berdasarkan *Confidence Score* (Probabilitas SVM)  
**Pengaju Revisi:** Dosen Penguji Skripsi / Klien Fadhilah Lamangkona  

---

## 1. Latar Belakang & Landasan Ilmiah

Dalam sistem pendukung keputusan (SPK) berbasis algoritma *Support Vector Machine* (SVM) dengan *Radial Basis Function* (RBF) kernel, model tidak hanya menghasilkan biner klasifikasi $y \in \{0, 1\}$ (Layak atau Tidak Layak), melainkan juga menghasilkan nilai margin keputusan posterior (*Decision Function Margin*) yang ditransformasikan menjadi probabilitas kontinu $P(y=1|\mathbf{x}) \in [0, 1]$ melalui estimasi probabilitas (*Platt Scaling*).

Dosen penguji meminta agar sistem menyajikan fitur **Perangkingan (Ranking)** untuk memeringkat calon penerima bantuan. Hal ini bertujuan agar dinas sosial dapat menentukan **skala prioritas alokasi bantuan kuota terbatas** — yaitu dengan mendahulukan keluarga penerima manfaat yang memiliki tingkat keyakinan (*confidence score*) tertinggi dari model.

---

## 2. Perubahan Sistem Web SPK

1. **Menu Navigasi Sidebar:**
   - Menambahkan menu baru **"Perangkingan"** dengan ikon `bi-sort-numeric-down` di bawah menu manajemen calon pada seluruh halaman terproteksi.
2. **Endpoint Backend & Detail Calon (`/perangkingan` & `/calon/<id>/detail`):**
   - Menggabungkan data `CalonPenerima` dan `HasilKeputusan` via SQLAlchemy join query untuk perangkingan (`ORDER BY probabilitas DESC`).
   - Rute `/calon/<int:id>/detail` menyajikan profil lengkap calon, koordinat wilayah, detail 8 parameter kemiskinan, dan rincian keputusan/probabilitas model SVM.
   - Mengintegrasikan interaksi klik pada nama calon di daftar calon, dashboard, dan tabel perangkingan untuk memicu penampilan modal/halaman detail secara mulus.
3. **Antarmuka Pengguna (`templates/calon/ranking.html` & `templates/calon/detail.html`):**
   - Menampilkan *Bento Stat Cards* statistik perangkingan.
   - Desain penomoran peringkat yang formal dan flat (misal `Prioritas 1`, `Prioritas 2`, dst.) menggantikan representasi visual podium/trofi yang terkesan kurang akademis.
   - Bilah kemajuan (*progress bar*) visual untuk merepresentasikan persentase *confidence score* (keyakinan prediksi).

---

## 3. Panduan Penjelasan Saat Sidang Skripsi

Jika dosen penguji menanyakan mengenai mekanisme perangkingan ini saat ujian sidang, mahasiswa dapat memberikan jawaban akademis sebagai berikut:

> *"Sistem ini memanfaatkan nilai probabilitas keluaran dari model SVM RBF (melalui penaksiran probabilitas Platt Scaling). Meskipun hasil keputusan akhir berbentuk biner (Layak/Tidak Layak), nilai probabilitas merepresentasikan tingkat kepastian model terhadap pemenuhan kriteria bantuan. Pada menu Perangkingan, calon penerima diurutkan secara hierarkis berdasarkan nilai probabilitas tersebut dari yang tertinggi, sehingga jika kuota kuota bantuan sosial di lapangan terbatas, dinas sosial dapat dengan objektif memprioritaskan keluarga yang berada di peringkat paling atas."*
