# Rencana Implementasi
## SPK Kelayakan Calon Penerima Bantuan PKH - SVM
### 1-7 Juli 2026

---

## Timeline Detail

### ✅ Fase 0: Pra-Pengembangan (1 Juli 2026 — Selesai)
| Kegiatan | Status |
|----------|--------|
| ✅ Baca dan analisis PDF skripsi | ✅ Selesai |
| ✅ Riset dataset di Kaggle | ✅ Selesai |
| ✅ Download dataset eksternal untuk training | ✅ Selesai |
| ✅ Dokumentasi konteks & memory | ✅ Selesai |
| ✅ PRD | ✅ Selesai |
| ✅ Arsitektur Sistem (DFD, ERD, Flowchart) | ✅ Selesai |
| ✅ Tech stack & framework | ✅ Selesai |
| ✅ Rencana implementasi ini | ✅ Selesai |

### 📋 Fase 1: Pembuatan Model SVM di Kaggle (1-2 Juli)
| Kegiatan | Status |
|----------|--------|
| Buat dataset sintetis/eksternal untuk training awal | ✅ Selesai |
| Buat Kaggle Notebook: Preprocessing + EDA | ✅ Selesai |
| Training SVM (GridSearch CV, multi kernel) | ✅ Selesai |
| Evaluasi (Confusion Matrix, Classification Report) | ✅ Selesai |
| Export model (.pkl pipeline) | ✅ Selesai |
| **⚠️ PERLU DIUPDATE:** Ganti encoding LabelEncoder → Ordinal Encoding (skema 1-5) + MinMaxScaler | **PENDING — nunggu dataset real** |
| **⚠️ PERLU DIUPDATE:** Tambah ROC Curve, Feature Importance, Learning Curve | **PENDING — nunggu dataset real** |

### 🌐 Fase 2: Pembuatan Web SPK (2-4 Juli)
| Kegiatan | Status |
|----------|--------|
| Inisialisasi Flask project + struktur folder | ✅ Selesai |
| Database model (SQLAlchemy) + Migrasi | ✅ Selesai |
| CRUD Calon Penerima (form + table) | ✅ Selesai |
| Integrasi model SVM (load .pkl → predict) | ✅ Selesai |
| Dashboard + Visualisasi hasil | ✅ Selesai |
| Export laporan (PDF/Excel) | ⏳ Belum |
| **⚠️ PERLU UPDATE:** Sesuaikan form input dengan skema encoding baru (ordinal 1-5, bukan raw) | **PENDING** |

### 🎨 Fase 3: Integrasi & Finalisasi (4-5 Juli)
| Kegiatan | Durasi |
|----------|--------|
| Testing end-to-end | 2 jam |
| Perbaikan UI/UX (Bootstrap refinement) | 2 jam |
| Dokumentasi (README, user guide) | 2 jam |
| **Total** | **~6 jam** |

### 📝 Fase 4: Dokumentasi Skripsi (5-6 Juli)
| Kegiatan | Durasi |
|----------|--------|
| Diagram Flowchart Tahapan | 1 jam |
| DFD Level 0 & 1 | 1 jam |
| ERD | 1 jam |
| Screenshot sistem | 1 jam |
| **Total** | **~4 jam** |

### 🛡️ Fase 5: Buffer & Revisi (6-7 Juli)
| Kegiatan | Durasi |
|----------|--------|
| Revisi sesuai feedback | 4 jam |
| Testing ulang | 2 jam |
| **Total** | **~6 jam** |

---

## Strategy Dataset

### ✅ Dataset Real — Konfirmasi dari Tim PKH Sulteng
- **Sumber:** Zainal, Ketua Tim SDM PKH Provinsi Sulawesi Tengah
- **Dasar hukum:** Keputusan Dirjen Linjamsos No. 9/3/HK.01.1/2025
- **Jumlah:** ±350 data (dengan status layak/tidak layak)
- **Kriteria & indikator:** SUDAH DITETAPKAN (lihat `Penentuan Kriteria.txt` dan `Penentuan Indikator Kriteria.txt`)
- **Skema encoding:** Ordinal (1-5) untuk penghasilan/pekerjaan/aset, Biner (0/1) untuk sisanya
- **Normalisasi:** Min-Max Normalization
- **Status:** Menunggu file CSV dari client

---

## Milestone & Pengiriman ke Client

| Milestone | Target | Output |
|-----------|--------|--------|
| M1: Progress report | 2 Juli siang | PRD + Arsitektur + Timeline (ini) |
| M2: Model SVM siap | 2 Juli malam | Kaggle Notebook + model .pkl |
| M3: Web SPK beta | 4 Juli | Web bisa diakses, fitur inti berfungsi |
| M4: Final | 5-7 Juli | Semua fitur + diagram + dokumentasi |

---

## Pembagian Pekerjaan

### Saya (Developer)
- ✅ Semua coding: model SVM di Kaggle + web Flask
- ✅ Arsitektur sistem
- ✅ Dokumentasi teknis

### Client (Fadhilah)
- ⏳ Dataset real dari pendamping PKH
- ✅ Konfirmasi approval rancangan
- ⏳ Persiapan untuk sidang

---

## Catatan Risiko

| Risiko | Mitigasi |
|--------|----------|
| Dataset real tidak datang | Pakai dataset sintetis untuk model awal, retrain saat data real ready |
| Client revisi besar | Unlimited revisi — dialokasikan buffer 2 hari |
| SVM kurang akurat | Coba kernel RBF + GridSearch, jika masih kurang akurasi tambah fitur |
| Kaggle session timeout | Simpan checkpoint, gunakan GPU session jika perlu |
