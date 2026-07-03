# Log Harian 02: Pelatihan Model SVM di Kaggle Notebook
**Tanggal:** 1 Juli 2026
**Durasi:** ~2 jam

---

## Kegiatan yang Dilakukan

1. **Pembuatan Lingkungan Eksperimen di Kaggle** — Menyusun script Python untuk eksperimen training menggunakan Kaggle Notebook:
   - Judul Notebook: `svm-pkh-klasifikasi`
   - Versi 1: Terjadi kendala kecil pada presedensi operator boolean (telah diperbaiki dengan menambahkan tanda kurung pada proses indeks data).
   - Versi 2: ✅ Sukses — seluruh blok kode berhasil dieksekusi tanpa error.
   - URL Notebook: `https://www.kaggle.com/code/fadhilahlamangkona/svm-pkh-klasifikasi`

2. **Perancangan Dataset Sintetis (1000 Sampel)**:
   - Menggunakan 8 atribut/fitur masukan sesuai dengan proposal skripsi.
   - Melakukan pelabelan awal berbasis aturan (*rule-based*) ditambah dengan noise Gaussian agar sebaran data menyerupai karakteristik data riil lapangan.
   - Distribusi kelas target seimbang: 513 Layak dan 487 Tidak Layak.

3. **Pelatihan & Evaluasi Awal**:
   - Menguji performa 4 kernel SVM: Linear, RBF, Polynomial, dan Sigmoid.
   - Menggunakan metode GridSearchCV untuk mencari kombinasi parameter terbaik untuk kernel RBF (nilai C dan gamma).
   - Menghasilkan Confusion Matrix dan Classification Report untuk analisis performa.

4. **Penyimpanan Output Eksperimen**:
   - Menyimpan model hasil training ke file serialisasi `.pkl` → `web/models/svm_pkh_pipeline.pkl`
   - Menyimpan visualisasi Confusion Matrix → `web/static/img/confusion_matrix.png`
   - Menyimpan hasil analisis data awal (EDA) → `web/static/img/eda_visualizations.png`

---

## Hasil Pelatihan Model (Baseline)

### Perbandingan Kinerja Kernel SVM

| Jenis Kernel | Akurasi | Presisi | Recall | F1-Score |
|--------|---------|---------|--------|----------|
| **Linear** | 0.8900 | 0.9263 | 0.8544 | 0.8889 |
| **RBF (Terpilih)** | 0.8900 | 0.9091 | 0.8738 | 0.8911 |
| **Polynomial** | 0.8400 | 0.9277 | 0.7476 | 0.8280 |
| **Sigmoid** | 0.8700 | 0.8812 | 0.8641 | 0.8725 |

### Hasil Tuning Hyperparameter (GridSearchCV)
- **Kombinasi Terbaik:** `{'C': 10, 'gamma': 0.1, 'kernel': 'rbf'}`
- **Nilai Cross-Validation (CV) Score:** 0.8900
- **Confusion Matrix:**
  - True Negative (TN): 87 | False Positive (FP): 10
  - False Negative (FN): 12 | True Positive (TP): 91

### Detail Classification Report
```
               precision    recall  f1-score   support

Tidak Layak       0.88      0.90      0.89        97
      Layak       0.90      0.88      0.89       103

   accuracy                           0.89       200
  macro avg       0.89      0.89      0.89       200
```

---

## Keputusan Eksperimen

| Pilihan Keputusan | Alasan Ilmiah / Praktis |
|-----------|--------|
| **Kernel Terpilih: RBF** | Meskipun memiliki tingkat akurasi yang sama dengan kernel Linear (89%), kernel RBF menghasilkan nilai F1-Score yang lebih tinggi (0.891 vs 0.889) serta nilai Recall yang lebih baik (0.873 vs 0.854). Hal ini meminimalkan tingkat *false negative* (kasus layak yang salah terprediksi sebagai tidak layak). |
| **Parameter C=10 dan gamma=0.1** | Berdasarkan hasil optimasi GridSearchCV. Nilai C=10 memberikan tingkat toleransi kesalahan klasifikasi yang seimbang (tidak overfit/underfit), dan gamma=0.1 membatasi pengaruh sampel dalam radius yang ideal untuk menangkap pola umum. |
| **Dataset Sintetis Rule-Based** | Digunakan sebagai langkah awal karena data riil dari dinas sosial masih dalam proses administrasi. Sebaran data diatur agar logis dan mencakup kriteria kelayakan dasar PKH. |
| **Stratified Data Splitting** | Membagi data train dan test dengan rasio seimbang guna menjamin keandalan pengujian model. |
| **Penyimpanan Pipeline Utuh** | Menyimpan seluruh langkah pemrosesan (LabelEncoder + StandardScaler + Model SVM) dalam satu file `.pkl` guna mempermudah integrasi backend pada aplikasi Flask. |

### Mengapa Memilih Kernel RBF?
- Kernel RBF (*Radial Basis Function*) mampu memetakan data masukan ke dalam dimensi ruang yang lebih tinggi secara fleksibel.
- Hubungan kriteria kelayakan PKH bersifat non-linear (interaksi antar kriteria cukup kompleks). Sebagai contoh, keluarga dengan penghasilan rendah namun memiliki aset tertentu memiliki bobot kelayakan yang berbeda dibandingkan keluarga berpenghasilan rendah tanpa aset. Kernel RBF sangat baik dalam memisahkan pola non-linear tersebut dibandingkan kernel Linear biasa.

### Fungsi Parameter C dan Gamma
- **Parameter C (Regularisasi):** Mengatur tingkat penalti terhadap kesalahan klasifikasi. Nilai C=10 dipilih karena berada di rentang menengah, memberikan toleransi yang cukup agar model memiliki kemampuan generalisasi yang baik terhadap data baru.
- **Parameter Gamma:** Menentukan seberapa jauh jangkauan pengaruh dari satu sampel latih. Nilai gamma=0.1 menandakan radius pengaruh yang cukup luas, membantu model berfokus pada tren sebaran data utama dan mengabaikan pencilan (*outliers*).

---

## Kendala & Solusi

| Kendala Kode | Solusi |
|---------|--------|
| Error presedensi operator logika pada penyusunan filter dataset sintetis | Menambahkan kurung pemisah pada syntax pemrograman Python agar operasi logika dikerjakan secara berurutan. |
| Perbedaan minor versi pustaka scikit-learn | Menyesuaikan versi pustaka di notebook Kaggle agar selaras dengan versi yang terpasang di server lokal web Flask. |

---

## Rencana Tindak Lanjut

1. Model prototype awal dengan akurasi 89% siap digunakan untuk pengujian integrasi web.
2. Mempersiapkan skrip retraining model untuk mempermudah proses ketika dataset riil diterima.
3. Mempelajari konsep matematis SVM, kernel RBF, serta parameter C dan Gamma sebagai bahan penyusunan materi Bab III Skripsi.

---

## Output Progres

- ✅ Kode eksperimen Kaggle Notebook versi 2 berjalan lancar
- ✅ Model SVM awal tersimpan dalam format `.pkl`
- ✅ File visualisasi Confusion Matrix dan EDA siap digunakan untuk lampiran skripsi
- ✅ Perbandingan performa kernel terdokumentasi dengan rapi
- ⏳ Integrasi model ke dalam backend Flask (Fase Pengembangan Web)

---

## Retrospektif (Ditambahkan 3 Juli 2026)

Hasil training di sesi ini masih valid sebagai **prototype**, namun ada beberapa hal konfigurasi awal yang ternyata **tidak sesuai** dan harus diperbaiki saat retraining dengan data riil:

1. **Encoding:** Penggunaan `LabelEncoder` otomatis ternyata **tidak sesuai** karena memberikan pemetaan alfabetis acak. Pemrosesan harus diganti ke ordinal encoding manual 1-5 berdasarkan indikator resmi PKH agar model belajar dengan benar.
2. **Penskalan Fitur (Scaler):** Penggunaan `StandardScaler` diubah ke `MinMaxScaler` berdasarkan **revisi dari Pak Yazdi**. MinMaxScaler lebih cocok untuk tipe data ordinal dan biner. Dampak perubahan scaler ini terhadap akurasi model riil belum bisa diprediksi sebelum training berjalan.
3. **Volume Dataset:** Dataset sintetis awal menggunakan 1000 sampel, sementara data riil yang akan didapat hanya sekitar 350 sampel. Untuk mencegah overfitting pada dataset yang lebih kecil, evaluasi k-fold akan ditingkatkan menjadi 10-fold.
4. **Format Model .pkl:** Model awal diekspor sebagai instance class kustom yang ternyata **tidak cocok** untuk di-load di Flask. Format harus diganti menjadi Python dictionary.
5. **Kategori Kriteria:** Pemodelan awal menggunakan 11 kategori pekerjaan dan 6 kategori aset. Jumlah ini **tidak sesuai** dengan dokumen resmi PKH yang menetapkan masing-masing hanya 5 kategori. Hal ini akan mengubah representasi sebaran data latih.

Angka akurasi baseline sebesar 89% kemungkinan akan bergeser saat retraining data riil dilakukan. Target minimal untuk model akhir tetap diatur $\ge 85\%$.
