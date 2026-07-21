# R1 — Laporan Akhir Implementasi
## SPK Kelayakan Calon Penerima Bantuan PKH — SVM

> **Dokumen R1:** Status final setelah seluruh tahap pengembangan selesai.
> Semua checklist di bawah telah terpenuhi.

---

## 1. Timeline Implementasi — Status Final

| Fase | Tanggal | Status | Keterangan |
|------|---------|--------|------------|
| **0. Pra-Pengembangan** | 1 Juli 2026 | ✅ **Selesai** | PRD, arsitektur, rencana |
| **1. Training Model SVM (Prototype)** | 1 Juli 2026 | ✅ **Selesai** | Data sintetis, akurasi 89% |
| **2. Pembuatan Web SPK** | 2 Juli 2026 | ✅ **Selesai** | CRUD, dashboard, prediksi |
| **3. Audit & Gap Analisis** | 3 Juli 2026 | ✅ **Selesai** | 5 gap kritis teridentifikasi |
| **4. Perbaikan & Retrain** | 4-7 Juli 2026 | ✅ **Selesai** | Semua komponen termasuk retrain dataset real |
| **5. Dokumentasi Laporan** | 5-7 Juli 2026 | ✅ **Selesai** | Log sesi 1-15 + dokumen final R1 |
| **6. Buffer & Revisi** | 7 Juli 2026 | ✅ **Selesai** | Validasi akhir, tidak ada revisi kritis |

---

## 2. Detail Per Fase

### Fase 0: Pra-Pengembangan ✅
**Output:**
- ✅ PRD (`PRD_SPK_PKH.md`)
- ✅ Arsitektur Sistem (`ARSITEKTUR_SISTEM.md`)
- ✅ Rencana Implementasi (file ini)
- ✅ Memory files (konteks proyek)
- ✅ Struktur folder docs/

### Fase 1: Training Model SVM — Prototype ✅
**Output:**
- ✅ Notebook Kaggle versi 2 (data sintetis)
- ✅ Perbandingan 4 kernel SVM
- ✅ GridSearchCV → C=10, gamma=0.1, kernel=RBF
- ✅ Akurasi 89%, Presisi 90%, Recall 88%
- ✅ Model pipeline .pkl tersimpan

### Fase 2: Pembuatan Web SPK ✅
**Output:**
- ✅ Flask app lengkap dengan Blueprints
- ✅ Database SQLite (3 tabel: User, CalonPenerima, HasilKeputusan)
- ✅ CRUD lengkap + prediksi otomatis
- ✅ Dashboard dengan statistik + Pie/Doughnut Chart kelayakan (Chart.js)
- ✅ Halaman About (penjelasan model untuk sidang)

### Fase 3: Audit & Gap Analisis ✅
**Output:**
- ✅ 5 gap kritis teridentifikasi
- ✅ Seluruh gap telah di-resolve di sisi web
- ✅ Dokumentasi lengkap

### Fase 4: Perbaikan & Retrain ✅ **SELESAI**

#### 4.1 Update Notebook Kaggle (v3 — Dataset Real)
- [x] **Dataset real** — 318 data dari 3 desa (Posona, Kasimbar Palapi, Posona Atas)
- [x] **Ganti LabelEncoder** → mapping ordinal manual 1-5 (dokumen resmi PKH)
- [x] **Ganti StandardScaler** → MinMaxScaler
- [x] **Update kategori** sesuai 5 kategori resmi (Pekerjaan, Aset, Penghasilan)
- [x] **Export sebagai dictionary** (bukan class SVMPipeline)
- [x] **Tambah ROC Curve + AUC Score** (AUC = 0.9954)
- [x] **GridSearchCV ulang** → C=10, gamma=0.01, kernel=RBF terbaik
- [x] **Download .pkl baru** → `web/models/svm_pkh_pipeline.pkl`

#### 4.2 Update Web SPK ✅
- [x] `models_db.py` — kolom skor ordinal, boolean, tambah tabel User
- [x] `svm_predictor.py` — load dictionary, MinMaxScaler, tanpa LabelEncoder
- [x] `app.py` — decorator login, Blueprints, CSRF
- [x] `calon_form.html` — dropdown 5 kategori resmi, checkbox boolean
- [x] Template `login.html`, `change_password.html`
- [x] Mock model → dictionary format
- [x] Blueprints modular (auth, dashboard, calon, about, admin)
- [x] CSRF protection + error handlers (403, 404, 500)
- [x] Ganti password + RBAC multi-role
- [x] Import Excel/CSV + validasi per baris + batch prediksi + duplikasi NIK check
- [x] Export Excel/CSV dengan filter dinamis (25 kolom termasuk NIK)
- [x] Template Excel untuk panduan import (dilengkapi kolom NIK)
- [x] Autocomplete wilayah (database 89k+)
- [x] Grafik dashboard Pie/Doughnut kelayakan (Chart.js) (Grafik interaktif wilayah/tren/komparasi dihapus atas permintaan klien)
- [x] Security hardening 10 lapisan
- [x] **Alias kolom CSV** — dukungan import CSV raw dari lapangan (ASET→kepemilikan_aset, HAMIL→ibu_hamil, AUD→anak_usia_dini, dsb)
- [x] **Integrasi Kolom NIK** — Penambahan kolom `nik` ke database, auto-migrasi data lama, validasi NIK 16 digit, pencegahan duplikat NIK, pencarian listing calon berdasarkan NIK, dan pembuatan file test data baru yang dilengkapi NIK.

#### 4.3 Verifikasi ✅
- [x] **Tes prediksi end-to-end** — Layak/Tidak Layak berfungsi benar
- [x] **Model real vs label asli** — 98.44% akurasi pada test set
- [x] **Import CSV raw** — file asli dari pendamping (POSONA.csv, dll) bisa di-upload
- [x] **Export** — Excel/CSV dengan seluruh filter berfungsi
- [x] **Dashboard** — render data real untuk proporsi kelayakan (grafik wilayah/tren/komparasi dihapus)

### Fase 5: Dokumentasi Skripsi ✅
- [x] Kompilasi Bab IV (Hasil & Pembahasan) dari docs/
- [x] Screenshot antarmuka sistem (dapat diambil dari web)
- [x] Tabel evaluasi model (98.44% akurasi, 97.5% presisi, 100% recall, 0.9873 F1, 0.9954 AUC)
- [x] Confusion Matrix final (39 TP, 24 TN, 1 FP, 0 FN)
- [x] Penjelasan preprocessing + encoding ordinal
- [x] Diagram (DFD, ERD, Flowchart) — tersedia di `ARSITEKTUR_SISTEM.md`
- [x] **Dokumen R1** — ringkasan final (`PRD_R1.md`, `RENCANA_IMPLEMENTASI_R1.md`)

### Fase 6: Buffer & Revisi ✅
- [x] Validasi akhir seluruh komponen
- [x] Perbaikan minor (column alias CSV raw)
- [x] Finalisasi semua dokumen

### Fase 7: Perangkingan Confidence Score ✅
- [x] Rute `@calon_bp.route('/perangkingan')` — Backend sorting descending `HasilKeputusan.probabilitas`
- [x] Template `templates/calon/ranking.html` — Bento stat cards, badge peringkat medali, progress bar confidence
- [x] Navigasi Sidebar `base.html` — Menu 'Perangkingan' dengan ikon `bi-trophy`
- [x] Dokumentasi Sesi 22 Juli 2026 (`sesi-2026-07-22-fitur-perangkingan-confidence.md`)

---

## 3. Status Resolusi 5 Gap Kritis (Final)

| # | Gap | Severity | Status Resolusi |
|---|-----|----------|-----------------|
| 1 | Encoding LabelEncoder → Ordinal 1-5 | **Kritis** | ✅ **Selesai** — Notebook v3 pakai ordinal manual, web pakai constants mapping |
| 2 | StandardScaler → MinMaxScaler | **Kritis** | ✅ **Selesai** — Scaler di model & web sudah MinMaxScaler |
| 3 | Kategori form web tidak cocok resmi | **Kritis** | ✅ **Selesai** — Dropdown sesuai dokumen PKH |
| 4 | Format .pkl class vs dictionary | **Tinggi** | ✅ **Selesai** — Predictor load dictionary |
| 5 | anak_usia_dini dkk harus biner | **Sedang** | ✅ **Selesai** — Boolean di DB & form |

---

## 4. Ringkasan Hasil Model

| Metrik | Prototype (Sintetis) | Final (Real 318 data) | Peningkatan |
|--------|---------------------|----------------------|-------------|
| Akurasi | 89% | **98.44%** | +9.44% |
| Presisi | 90% | **97.50%** | +7.50% |
| Recall | 88% | **100%** | +12% |
| F1 | 0.89 | **0.9873** | +0.0973 |
| AUC | — | **0.9954** | — |

**Parameter Final:** SVM RBF | C=10 | gamma=0.01 | class_weight=balanced

---

*Dokumen R1 — 7 Juli 2026*
