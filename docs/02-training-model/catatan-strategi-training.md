# Catatan Metodologi: Rencana Eksperimen SVM & Integrasi Dataset Riil
**Tanggal:** 2 Juli 2026

---

## 1. Komponen Evaluasi Model Saat Ini (Sesuai Kaidah Akademis)

Untuk memastikan pengujian model Support Vector Machine (SVM) memenuhi standar penulisan skripsi, komponen berikut telah diterapkan pada rancangan awal:
- **Pengujian 4 Kernel SVM:** Menguji kernel Linear, RBF, Polynomial, dan Sigmoid untuk melihat perbandingan performa masing-masing secara objektif.
- **K-Fold Cross-Validation (5-fold) & GridSearchCV:** Digunakan untuk mencari parameter optimal (seperti nilai C dan gamma) secara sistematis, menghindari tebakan manual.
- **Metrik Evaluasi Standar:** Menggunakan Confusion Matrix, Precision, Recall, dan F1-Score untuk mengukur kinerja klasifikasi secara menyeluruh.
- **Stratified Data Splitting:** Membagi dataset menjadi data training dan testing dengan mempertahankan proporsi kelas target (Layak/Tidak Layak) agar evaluasi tidak bias.
- **Pipeline Terintegrasi:** Proses preprocessing data dan pelatihan model digabungkan ke dalam satu pipeline utuh agar proses pengolahan data konsisten.

### Rencana Peningkatan Kualitas Analisis (Nilai Tambah Sidang)

| Peningkatan | Manfaat Analisis untuk Sidang |
|---|---|
| **Kurva ROC & AUC Score** | Menunjukkan kemampuan model dalam membedakan kelas kelayakan pada berbagai nilai ambang batas (threshold). |
| **Learning Curve** | Membuktikan secara visual bahwa model tidak mengalami overfitting dengan membandingkan training score dan cross-validation score. |
| **Permutation Feature Importance** | Menjelaskan kontribusi relatif dari masing-masing kriteria dalam penentuan keputusan kelayakan PKH. |
| **10-Fold Cross-Validation** | Membuat pengujian model lebih robust dan dapat dipercaya, terutama jika ukuran dataset riil terbatas. |
| **Statistik Deskriptif Kriteria** | Menyajikan rata-rata, standar deviasi, dan sebaran data untuk setiap fitur sebelum melangkah ke proses klasifikasi. |

### 🎯 Keputusan Eksperimen Awal
Peningkatan metrik di atas ditunda pengaplikasiannya karena alasan berikut:
- Eksperimen saat ini masih menggunakan dataset sintetis. Penambahan metrik visualisasi yang kompleks akan lebih representatif jika diterapkan langsung pada dataset riil.
- Proses modifikasi notebook akan dilakukan sekaligus saat dataset riil dari lapangan selesai dihimpun.
- Fokus jangka pendek dialihkan ke penyelesaian prototype aplikasi web SPK agar sistem integrasi dasar dapat diuji terlebih dahulu.

---

## 2. Strategi Integrasi Dataset Riil

### Situasi
Proses pengumpulan data riil penerima bantuan PKH di Kecamatan Kasimbar sedang dikoordinasikan dengan pendamping PKH setempat dan diperkirakan selesai dalam waktu dekat.

### Mekanisme Pelatihan Ulang (Retraining)
- Pelatihan ulang model akan dilakukan dari awal (*fit* ulang), bukan dengan melanjutkan model prototype.
- **Justifikasi Teoretis:** Algoritma SVM tidak mendukung pembelajaran inkremental (*incremental learning*) secara bawaan. Penambahan data baru akan mengubah posisi batas keputusan (*decision boundary*) dan *support vector* secara signifikan, sehingga model harus dilatih ulang dari awal.

### Kesesuaian Skema Data Riil
Struktur data riil yang diperoleh harus memiliki atribut dasar yang sama dengan rancangan awal untuk menjaga kompatibilitas pipeline pemrosesan:

| Kriteria | Tipe Data Awal | Deskripsi |
|---------|----------------------|---|
| penghasilan | Numerik (int/float) | Total pendapatan keluarga per bulan |
| pekerjaan | Kategorikal (string) | Kategori pekerjaan kepala keluarga |
| kepemilikan_aset | Kategorikal (string) | Kepemilikan aset berharga / tempat tinggal |
| ibu_hamil | Biner (0/1) | Status keberadaan ibu hamil dalam keluarga |
| anak_usia_dini | Numerik (int) | Jumlah anak usia balita |
| anak_sekolah | Numerik (int) | Jumlah anak usia sekolah (SD/SMP/SMA) |
| disabilitas | Biner (0/1) | Keberadaan anggota keluarga dengan disabilitas |
| lansia | Numerik (int) | Jumlah anggota keluarga kategori lansia |
| **label** | **Biner (0=Tidak Layak, 1=Layak)** | Keputusan kelayakan dari sistem PKH |

### Analisis Risiko & Mitigasi Integrasi

| Risiko Teknis | Mitigasi |
|---|---|
| Munculnya kategori pekerjaan baru pada data lapangan | Menambahkan fungsi pemetaan manual untuk mengelompokkan pekerjaan baru ke kategori yang sepadan. |
| Ketidakseimbangan kelas target (*class imbalance*) | Menerapkan parameter `class_weight='balanced'` pada fungsi klasifikasi SVM (SVC). |
| Data kosong (*missing values*) | Menggunakan imputasi nilai median/mean untuk menjaga kelengkapan baris data. |
| Format label tidak berupa biner (misal teks "Layak") | Melakukan pra-pemrosesan mapping nilai teks ke biner (1/0) sebelum training. |

---

## 3. Alur Kerja Integrasi Data Riil

```
1. Menerima file CSV dataset riil dari pendamping PKH.
2. Mengunggah file dataset tersebut ke lingkungan kerja Kaggle Notebook.
3. Memperbarui kode pembacaan data (mengubah generator sintetis menjadi pd.read_csv).
4. Menambahkan pembuatan kurva ROC dan visualisasi tambahan pada notebook.
5. Menjalankan ulang notebook eksperimen untuk melatih model baru.
6. Mengunduh file model hasil training (pipeline.pkl).
7. Mengganti file model lama di folder 'web/models/'.
8. Melakukan verifikasi dan uji coba fungsionalitas sistem web dengan model baru.
```

---

## ✅ Lampiran: Hasil Real Training (7 Juli 2026)

Alur kerja di atas telah selesai dijalankan pada 7 Juli 2026. Berikut hasil aktualnya:

### Dataset
- **Sumber:** Pendamping PKH 3 desa Kecamatan Kasimbar
- **File:** `dataset real/POSONA.csv` (165), `KASIMBAR-PALAPI.csv` (112), `POSONA-ATAS.csv` (41)
- **Total:** 318 data (Layak=196, Tidak Layak=122)

### Preprocessing
| Komponen | Rencana | Realisasi |
|----------|---------|-----------|
| Encoding | Ordinal manual 1-5 | ✅ Mapping dictionary sesuai dokumen PKH |
| Normalisasi | MinMaxScaler | ✅ feature_range=(0,1) |
| Split | 80/20 stratified | ✅ 254 train + 64 test |

### Performa 4 Kernel

| Kernel | Akurasi | Presisi | Recall | F1 |
|--------|---------|---------|--------|-----|
| RBF | **0.9844** | **0.9750** | **1.0000** | **0.9873** |
| Linear | 0.9844 | 0.9750 | 1.0000 | 0.9873 |
| Poly | 0.9844 | 0.9750 | 1.0000 | 0.9873 |
| Sigmoid | 0.5938 | 0.6667 | 0.6667 | 0.6667 |

### Parameter Terbaik (GridSearchCV)
- **Kernel:** RBF | **C:** 10 | **Gamma:** 0.01 | **class_weight:** balanced
- **CV Score:** 0.9882 | **AUC:** 0.9954

### Confusion Matrix (Test Set)
| | Pred Layak | Pred Tidak Layak |
|--|-----------|-----------------|
| Aktual Layak | 39 (TP) | 0 (FN) |
| Aktual Tidak Layak | 1 (FP) | 24 (TN) |

### Peningkatan dari Prototype

| Metrik | Prototype (Sintetis) | Final (Real) | Delta |
|--------|---------------------|-------------|-------|
| Akurasi | 89% | **98.44%** | +9.44% |
| Presisi | 90% | **97.50%** | +7.50% |
| Recall | 88% | **100%** | +12% |
| F1 | 0.89 | **0.9873** | +0.0973 |
| AUC | — | **0.9954** | — |

### Komponen Nilai Tambah untuk Sidang

| Peningkatan | Status | Catatan |
|-------------|--------|---------|
| **ROC Curve + AUC** | ✅ Terpasang | AUC = 0.9954 — hampir sempurna |
| **Confusion Matrix** | ✅ Terpasang | 39 TP, 24 TN, 1 FP, 0 FN |
| **class_weight=balanced** | ✅ Terpasang | Menangani imbalance (61.6% vs 38.4%) |
| **Learning Curve** | ⏳ Dilewati | Data 318 sudah cukup representatif, overfitting minimal (CV=0.9882 vs test=0.9844) |
| **Permutation Feature Importance** | ⏳ Dilewati | 8 fitur sudah jelas kontribusinya dari bobot resmi, tidak perlu analisis tambahan |

**Notebook final:** `svm-pkh-ta.ipynb`
**Model:** `web/models/svm_pkh_pipeline.pkl` (dictionary format, MinMaxScaler, SVM RBF C=10 gamma=0.01)
```

---

## Retrospektif (Ditambahkan 3 Juli 2026)

Setelah audit codebase pada 3 Juli 2026, strategi retraining model perlu diperbarui karena beberapa rancangan awal ternyata **tidak sesuai** dengan kriteria resmi dan **perlu direvisi**:

### Perubahan pada Alur Retraining:

1. **Skema Encoding** — Penggunaan `LabelEncoder` otomatis ternyata **tidak sesuai** karena mengurutkan kategori secara alfabetis acak, bukan berdasarkan bobot kelayakan. Ini diganti total dengan ordinal encoding manual (skala 1-5).
2. **Kategori Pekerjaan** — Kategori pekerjaan awal (11 pilihan) di web ternyata **tidak cocok** dengan instrumen resmi. Harus dikurangi menjadi 5 pilihan resmi saja (Tidak Bekerja, Pekerja Bebas, Petani/Nelayan, Wiraswasta, PNS/Pegawai Tetap). Jika data riil memiliki variasi lain di luar 5 ini, harus dipetakan secara manual ke salah satu dari kategori tersebut.
3. **Kategori Kepemilikan Aset** — Pilihan aset awal **tidak cocok** dengan instrumen resmi. Diubah menjadi 5 kategori resmi.
4. **Kriteria Penghasilan** — Input nominal rupiah mentah di model awal ternyata **tidak cocok** dan diubah menjadi skor Desil 1-5. Jika data riil yang diperoleh masih berupa rupiah, maka akan dikonversi menggunakan rentang nominal desil resmi.
5. **Komponen Sosial (anak_usia_dini, anak_sekolah, lansia)** — Menyimpan jumlah anak/lansia (integer) pada database awal ternyata **tidak sesuai**. Dokumen resmi hanya mensyaratkan status biner (Ada/Tidak), sehingga harus dikonversi menjadi biner (0/1).
6. **Format Model .pkl** — Mengekspor model sebagai objek class kustom ternyata **tidak sesuai** karena menyebabkan error saat dibaca oleh web Flask. Diputuskan diekspor dalam format dictionary Python standar.

### Skema Target Dataset Riil (Terbaru)

| Kriteria | Tipe Data yang Diharapkan | Konversi ke Skor / Nilai Biner |
|---------|---------------------------|-------------------|
| penghasilan | Rupiah atau Skor Desil | Nominal Rupiah dipetakan ke skor Desil 1-5 |
| pekerjaan | Kategorikal (string) | Dipetakan ke skor ordinal 1-5 |
| kepemilikan_aset | Kategorikal (string) | Dipetakan ke skor ordinal 1-5 |
| ibu_hamil | Biner (0/1) | Tetap biner |
| anak_usia_dini | Biner atau Numerik Jumlah | Jumlah > 0 dikonversi ke nilai 1 |
| anak_sekolah | Biner atau Numerik Jumlah | Jumlah > 0 dikonversi ke nilai 1 |
| disabilitas | Biner (0/1) | Tetap biner |
| lansia | Biner atau Numerik Jumlah | Jumlah > 0 dikonversi ke nilai 1 |
| **label** | **Biner (0=Tidak Layak, 1=Layak)** | Tetap biner |
