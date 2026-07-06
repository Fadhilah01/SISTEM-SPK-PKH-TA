# R1 — Hasil Final SPK Kelayakan Calon Penerima Bantuan PKH
## Berbasis Algoritma Support Vector Machine (SVM)

> **Dokumen R1:** Ringkasan final setelah seluruh tahap pengembangan selesai.
> Dokumen ini adalah **pembaruan dari PRD_SPK_PKH.md** dengan data real dan hasil aktual.
> Gunakan untuk dokumentasi laporan skripsi (Bab IV).

---

## 1. Dataset Real

| Item | Detail |
|------|--------|
| **Sumber** | Pendamping PKH 3 desa Kecamatan Kasimbar |
| **Desa** | Posona (165), Kasimbar Palapi (112), Posona Atas (41) |
| **Total** | **318 data** |
| **Label** | Layak = 196 (61.6%), Tidak Layak = 122 (38.4%) |
| **Atribut** | 8 fitur (3 ordinal 1-5 + 5 biner) |

## 2. Preprocessing

| Komponen | Sebelum (Prototype) | Sesudah (Final) |
|----------|---------------------|-----------------|
| Encoding | LabelEncoder (otomatis) | Ordinal manual 1-5 (sesuai dokumen PKH) |
| Normalisasi | StandardScaler | MinMaxScaler (range 0-1) |
| Split data | 80/20 stratified | 80/20 stratified (254 train, 64 test) |

### Skema Encoding Ordinal

**Penghasilan (Bobot 25%):** Desil 1=5, Desil 2=4, Desil 3=3, Desil 4=2, Desil 5=1
**Pekerjaan (Bobot 20%):** Tidak Bekerja=5, Pekerja Bebas=4, Petani/Nelayan=3, Wiraswasta=2, PNS=1
**Kepemilikan Aset (Bobot 15%):** Tidak Punya=5, Motor Rendah=4, Motor Tinggi=3, Mobil/Tanah=2, Mobil+Tanah=1
**Komponen Sosial (masing-masing 5-10%):** Ada=1, Tidak=0

## 3. Performa Model SVM — Perbandingan Kernel

| Kernel | Akurasi | Presisi | Recall | F1 |
|--------|---------|---------|--------|-----|
| **RBF** | **0.9844** | **0.9750** | **1.0000** | **0.9873** |
| Linear | 0.9844 | 0.9750 | 1.0000 | 0.9873 |
| Poly | 0.9844 | 0.9750 | 1.0000 | 0.9873 |
| Sigmoid | 0.5938 | 0.6667 | 0.6667 | 0.6667 |

## 4. Parameter Terbaik (GridSearchCV)

| Parameter | Nilai |
|-----------|-------|
| Kernel | RBF |
| C | 10 |
| Gamma | 0.01 |
| Class Weight | Balanced |
| CV Score | 0.9882 |
| **AUC Score** | **0.9954** |

## 5. Confusion Matrix (Data Test — 64 sampel)

| | Prediksi Layak | Prediksi Tidak Layak |
|--|---------------|---------------------|
| **Aktual Layak** | 39 (TP) | 0 (FN) |
| **Aktual Tidak Layak** | 1 (FP) | 24 (TN) |

## 6. Metrik Evaluasi Final

| Metrik | Target | Hasil Final | Benchmark (Pak Yazdi) |
|--------|--------|-------------|----------------------|
| Akurasi | ≥ 85% | **98.44%** | 88.57% |
| Presisi | ≥ 85% | **97.50%** | 86.49% |
| Recall | ≥ 85% | **100%** | 91.43% |
| F1-Score | ≥ 85% | **0.9873** | 88.89% |
| AUC | — | **0.9954** | — |

## 7. Perbandingan Prototype vs Final

| Metrik | Prototype (Sintetis) | Final (Real 318 data) | Peningkatan |
|--------|---------------------|----------------------|-------------|
| Akurasi | 89% | 98.44% | +9.44% |
| Presisi | 90% | 97.50% | +7.50% |
| Recall | 88% | 100% | +12% |
| F1 | 0.89 | 0.9873 | +0.0973 |

## 8. Riwayat Perubahan Encoding & Normalisasi

| Fase | Encoding | Scaler | Dataset | Akurasi |
|------|----------|--------|---------|---------|
| v1 (Prototype) | LabelEncoder | StandardScaler | 200 sintetis | 89% |
| v2 (Gap Analisis) | — | — | — | — |
| **v3 (Final)** | **Ordinal 1-5 manual** | **MinMaxScaler** | **318 real** | **98.44%** |

## 9. Status Fitur Web

| Fitur | Status | Catatan |
|-------|--------|---------|
| CRUD Calon Penerima | ✅ | Form dropdown kategori resmi |
| Prediksi SVM otomatis | ✅ | Saat input/import/edit |
| Dashboard + Grafik | ✅ | Wilayah, Tren, Komparasi |
| Import Excel/CSV | ✅ | Validasi + batch prediksi |
| Export Excel/CSV | ✅ | Filter dinamis 24 kolom |
| Login & RBAC | ✅ | Superadmin/Admin |
| Security Hardening | ✅ | 10 lapisan proteksi |
| Autocomplete Wilayah | ✅ | Database 89k+ wilayah |
| Riwayat Keputusan | ✅ | Per calon + riwayat prediksi |

## 10. Catatan untuk Sidang

1. **Kenapa SVM?** — SVM unggul untuk klasifikasi biner dengan data berdimensi sedang (8 fitur). Kernel RBF mampu memetakan data non-linear ke dimensi lebih tinggi tanpa perlu eksplisit transformasi.

2. **Kenapa ordinal 1-5 bukan LabelEncoder?** — LabelEncoder memberikan kode acak (0,1,2...) tanpa makna urutan. Ordinal 1-5 mempertahankan urutan tingkat kelayakan (5=paling rentan, 1=paling mampu), sehingga SVM bisa belajar batas keputusan yang bermakna.

3. **Kenapa MinMaxScaler?** — Data ordinal 1-5 perlu di-scale ke 0-1 agar jarak antar skor proporsional. StandardScaler menghasilkan nilai negatif yang menghilangkan interpretasi ordinal.

4. **Recall 100%?** — Model tidak pernah salah menolak calon yang sebenarnya layak. Ini penting untuk program bansos: lebih baik satu calon tidak layak terdeteksi layak (FP) daripada calon layak tertolak (FN).

---

*Dokumen R1 — 7 Juli 2026*
