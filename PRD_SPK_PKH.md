
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
| Fitur | Deskripsi | Prioritas |
|-------|-----------|-----------|
| Manajemen Data Calon Penerima | CRUD data calon penerima bantuan | P0 |
| Klasifikasi SVM | Prediksi layak/tidak layak berdasarkan model SVM | P0 |
| Dashboard SPK | Tampilan hasil keputusan + ringkasan data | P0 |
| Riwayat Keputusan | History prediksi + detail input | P0 |
| Export Laporan | Export hasil keputusan (PDF/Excel) | P1 |

### 3.2 Fitur Tambahan
| Fitur | Deskripsi | Prioritas |
|-------|-----------|-----------|
| Manajemen Pengguna | Login multi-level (admin, pendamping) | P1 |
| Re-training Model | Update model jika dataset baru tersedia | P2 |

## 4. Pengguna Sistem

| Role | Deskripsi |
|------|-----------|
| **Admin/Pendamping PKH** | Mengelola data calon penerima, menjalankan klasifikasi, melihat hasil keputusan |

## 5. Alur Bisnis

```
1. Pendamping PKH mengumpulkan data calon penerima
2. Data dimasukkan ke sistem (form input)
3. Sistem memproses data melalui model SVM yang sudah dilatih
4. Sistem menampilkan status: LAYAK / TIDAK LAYAK
5. Pendamping PKH menggunakan hasil sebagai rekomendasi keputusan
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
| 4 | Desil 4 | ± Rp.600.000 – Rp.700.000 |
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

| Metrik | Target | Benchmark |
|--------|--------|-----------|
| Akurasi | ≥ 85% | Hasil uji Pak Yazdi: 88.57% |
| Presisi | ≥ 85% | Hasil uji Pak Yazdi: 86.49% |
| Recall | ≥ 85% | Hasil uji Pak Yazdi: 91.43% |
| F1-Score | ≥ 85% | Hasil uji Pak Yazdi: 88.89% |

## 8. Dataset & Skenario

- **Sumber data:** Pendamping PKH 3 desa (Posona, Kasimbar Palapi, Posona Atas)
- **Jumlah data:** ±350 data (sudah berstatus layak/tidak layak)
- **Pembagian:** 80% Training (280) | 20% Testing (70)
- **Preprocessing:** Encoding ordinal (1-5) → Min-Max Normalization → SVM
- **Revisi penguji (Pak Yazdi Pusadan):** SVM bukan metode SPK, tapi model klasifikasi yang *diintegrasikan* ke SPK
- **Catatan:** Format encoding menggunakan skala 1-5 (bukan LabelEncoder) seperti ditetapkan oleh Tim PKH Sulteng

## 9. Kendala & Asumsi

- Dataset real ±350 data dari pendamping PKH
- Model akan di-retrain saat dataset real tersedia (encoding sudah fix berdasarkan indikator resmi)
- Sistem berjalan di lingkungan lokal/web hosting sederhana
- Output klasifikasi: **Layak** atau **Tidak Layak** (binary, tidak ada kelas "Sedang")
- SVM tetap bisa mengklasifikasikan data di area perbatasan (margin decision)
