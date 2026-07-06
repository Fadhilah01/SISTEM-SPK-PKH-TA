# Rencana Implementasi
## SPK Kelayakan Calon Penerima Bantuan PKH — SVM

---

## 1. Timeline Implementasi

| Fase | Tanggal | Status | Keterangan |
|------|---------|--------|------------|
| **0. Pra-Pengembangan** | 1 Juli 2026 | ✅ Selesai | PRD, arsitektur, rencana |
| **1. Training Model SVM** | 1 Juli 2026 | ✅ Selesai (prototype) | Data sintetis, akurasi 89% |
| **2. Pembuatan Web SPK** | 2 Juli 2026 | ✅ Selesai | CRUD, dashboard, prediksi |
| **3. Audit & Gap Analisis** | 3 Juli 2026 | ✅ Selesai | 5 gap kritis teridentifikasi |
| **4. Perbaikan & Retrain** | 4-6 Juli 2026 | ⏳ Sebagian Selesai | Refactoring Web & Login Selesai. Retrain menunggu CSV |
| **5. Dokumentasi Laporan** | 5-6 Juli 2026 | ⏳ | Bab IV dicicil (Log harian sesi 5 terbit) |
| **6. Buffer & Revisi** | 6-7 Juli 2026 | ⏳ | |

---

## 2. Detail Per Fase

### Fase 0: Pra-Pengembangan ✅
**Output:**
- ✅ PRD (`PRD_SPK_PKH.md`)
- ✅ Arsitektur Sistem (`ARSITEKTUR_SISTEM.md`)
- ✅ Rencana Implementasi (file ini)
- ✅ Memory files (konteks proyek)
- ✅ Struktur folder docs/

### Fase 1: Training Model SVM ✅ (Prototype)
**Output:**
- ✅ Notebook Kaggle versi 2 (https://www.kaggle.com/code/aamirulmaulana/svm-pkh-klasifikasi)
- ✅ Perbandingan 4 kernel SVM (linear, RBF, poly, sigmoid)
- ✅ GridSearchCV → parameter terbaik (C=10, gamma=0.1, kernel=RBF)
- ✅ Akurasi 89%, Presisi 90%, Recall 88%
- ✅ Model pipeline .pkl tersimpan
- ✅ Confusion Matrix + EDA visualisasi

**Catatan:** Model ini masih menggunakan data sintetis dan encoding LabelEncoder + StandardScaler. Akan di-retrain di Fase 4 dengan encoding ordinal 1-5 + MinMaxScaler sesuai dokumen resmi PKH.

### Fase 2: Pembuatan Web SPK ✅
**Output:**
- ✅ Flask app (5 halaman HTML, 7 routes)
- ✅ Database SQLite (2 tabel: CalonPenerima, HasilKeputusan)
- ✅ CRUD lengkap (tambah, edit, hapus, lihat)
- ✅ Prediksi otomatis saat input data
- ✅ Dashboard dengan statistik + hasil terbaru
- ✅ Halaman About (penjelasan model untuk sidang)

**Catatan:** Form input dan database schema masih menggunakan format lama. Akan diupdate di Fase 4 sesuai kategori resmi PKH.

### Fase 3: Audit & Gap Analisis ✅
**Output:**
- ✅ Audit menyeluruh terhadap seluruh codebase
- ✅ 5 gap kritis teridentifikasi (lihat detail di bawah)
- ✅ Rencana perbaikan untuk setiap komponen
- ✅ Dokumentasi lengkap (`docs/04-integrasi/sesi-2026-07-03-audit-gap-analisis.md`)

### Fase 4: Perbaikan & Retrain ⏳
**Trigger:** Dataset real CSV dari pendamping PKH

**Langkah-langkah:**

#### 4.1 Update Notebook Kaggle (versi 3) (⏳ Menunggu Dataset)
- [ ] Ganti dataset sintetis → `pd.read_csv()` dataset real
- [ ] Ganti LabelEncoder → mapping ordinal manual 1-5
- [ ] Ganti StandardScaler → MinMaxScaler
- [ ] Update kategori pekerjaan: `Tidak Bekerja(5), Pekerja Bebas(4), Petani/Nelayan(3), Wiraswasta(2), PNS/Pegawai Tetap(1)`
- [ ] Update kategori aset: `Tidak Punya(5), Motor rendah(4), Motor tinggi(3), Mobil/Tanah(2), Mobil+Tanah(1)`
- [ ] Update penghasilan jadi skor desil 1-5
- [ ] Export sebagai dictionary (bukan class)
- [ ] Tambah ROC Curve + AUC Score (improvement untuk sidang)
- [ ] Jalankan GridSearchCV ulang
- [ ] Download .pkl baru

#### 4.2 Update Web SPK (✅ Selesai)
- [x] Update `models_db.py` — kolom skor ordinal, kolom sosial jadi biner, tambah tabel `User`
- [x] Update `svm_predictor.py` — load format dictionary baru, hapus LabelEncoder logic, pakai normalisasi MinMaxScaler manual
- [x] Update `app.py` — terima skor kategori dari form, dekorator `@login_required`, rute login/logout
- [x] Update `calon_form.html` — dropdown 5 kategori resmi untuk penghasilan/pekerjaan/aset, checkbox biner untuk komponen sosial
- [x] Tambah template `login.html` untuk keamanan akses admin
- [x] Generate mock model pipeline `.pkl` tiruan untuk verifikasi fungsionalitas
- [x] Reset database (menghapus data dummy model lama)
- [x] Test prediksi end-to-end (Dodi - Hasil: Layak, confidence 97.8%)
- [x] Refaktorisasi modular dengan Flask Blueprints (auth, dashboard, calon, tentang)
- [x] Implementasi sistem proteksi serangan CSRF kustom
- [x] Pembuatan penangan error terpusat (403, 404, 500)

#### 4.3 Verifikasi (⏳ Menunggu Model Final)
- [ ] Tes 5-10 kasus prediksi manual dengan model final
- [ ] Bandingkan hasil prediksi model final dengan label asli dataset
- [ ] Screenshot semua halaman untuk dokumentasi laporan Bab IV


### Fase 5: Dokumentasi Skripsi ⏳
- [ ] Kompilasi Bab IV (Hasil & Pembahasan) dari docs/
- [ ] Screenshot antarmuka sistem
- [ ] Tabel hasil evaluasi model (akurasi, presisi, recall)
- [ ] Confusion Matrix final
- [ ] Penjelasan preprocessing + encoding
- [ ] Diagram-diagram (DFD, ERD, Flowchart) — sudah tersedia di `ARSITEKTUR_SISTEM.md`

### Fase 6: Buffer & Revisi ⏳
- [ ] Revisi berdasarkan feedback client
- [ ] Perbaikan bug (jika ada)
- [ ] Finalisasi semua dokumen

---

## 3. Daftar Gap Kritis (dari Fase 3)

| No | Gap | Komponen Terdampak | Status |
|----|-----|--------------------|--------|
| 1 | Encoding LabelEncoder → harus Ordinal 1-5 | Notebook, svm_predictor.py | ⏳ Fix di Fase 4 |
| 2 | StandardScaler → harus MinMaxScaler | Notebook, svm_predictor.py | ⏳ Fix di Fase 4 |
| 3 | Kategori form web tidak cocok dengan resmi | app.py, calon_form.html | ⏳ Fix di Fase 4 |
| 4 | Format .pkl class vs dictionary | Notebook, svm_predictor.py | ⏳ Fix di Fase 4 |
| 5 | anak_usia_dini, anak_sekolah, lansia harus biner | models_db.py, calon_form.html | ⏳ Fix di Fase 4 |

---

## 4. Risiko & Mitigasi

| Risiko | Dampak | Mitigasi |
|--------|--------|----------|
| Dataset real terlambat datang | Timeline mundur | Prototype sintetis sudah ready — tinggal retrain |
| Akurasi model < 85% dengan data real | Tidak memenuhi target | Coba kernel lain, tuning parameter, cek data quality |
| Format dataset real berbeda dari yang diharapkan | Perlu preprocessing tambahan | Mapping manual ke format ordinal 1-5 |
| Kategori baru di data real yang tidak terduga | LabelEncoder gagal (sudah dihapus) | Ordinal encoding manual — kategori fix 5 pilihan |
| Versi scikit-learn berbeda antara Kaggle dan lokal | Warning/error saat load .pkl | Pastikan versi sama, atau retrain di versi lokal |

---

## 5. Catatan Penting

1. **Semua gap harus diperbaiki bersamaan** — tidak bisa parsial karena model harus di-retrain dari awal
2. **Dataset real adalah trigger utama** — begitu CSV datang, Fase 4 langsung dijalankan
3. **Model sintetis tetap disimpan** sebagai referensi dan fallback
4. **Dokumentasi selalu update** — setiap perubahan dicatat di docs/
