# SPK Kelayakan Calon Penerima Bantuan PKH

Sistem Pendukung Keputusan berbasis web yang mengimplementasikan algoritma **Support Vector Machine (SVM)** untuk mengklasifikasikan kelayakan calon penerima bantuan Program Keluarga Harapan (PKH) di Kecamatan Kasimbar, Sulawesi Tengah.

## Dataset

- **Sumber:** Pendamping PKH 3 desa Kecamatan Kasimbar
- **Desa:** Posona (165 data), Kasimbar Palapi (112 data), Posona Atas (41 data)
- **Total:** 318 data dengan label Layak (196) dan Tidak Layak (122)
- **Atribut:** 8 fitor (3 ordinal 1-5 + 5 biner)

## Preprocessing

| Komponen | Metode |
|----------|--------|
| Encoding | Ordinal manual 1-5 (dokumen resmi PKH) |
| Normalisasi | MinMaxScaler (range 0-1) |
| Split data | 80/20 stratified (254 train, 64 test) |

## Hasil Model

Parameter terbaik dari GridSearchCV: kernel RBF, C=10, gamma=0.01, class_weight=balanced.

| Metrik | Hasil |
|--------|-------|
| Akurasi | 98.44% |
| Presisi | 97.50% |
| Recall | 100% |
| F1-Score | 0.9873 |
| AUC | 0.9954 |

### Confusion Matrix (Test Set)

| | Prediksi Layak | Prediksi Tidak Layak |
|--|---------------|---------------------|
| Aktual Layak | 39 (TP) | 0 (FN) |
| Aktual Tidak Layak | 1 (FP) | 24 (TN) |

## Fitur Sistem

- **Manajemen Data Calon:** CRUD data calon penerima dengan form dropdown kategori resmi
- **Klasifikasi SVM:** Prediksi otomatis saat input, edit, atau import data
- **Dashboard:** Visualisasi interaktif (Chart.js) -- sebaran wilayah, tren waktu, komparasi periode
- **Import/Export:** Import massal Excel/CSV dengan validasi per baris, export dengan filter dinamis (24 kolom)
- **Autentikasi:** Login dengan session, RBAC multi-role (Superadmin/Admin), ganti password, force password change
- **Wilayah:** Autocomplete wilayah bertingkat (Provinsi hingga Desa) dengan database 89k+ data
- **Keamanan:** CSRF protection, rate limit login, security headers, XSS prevention, validasi file upload

## Tech Stack

- **Backend:** Python Flask, SQLAlchemy, SQLite
- **Machine Learning:** scikit-learn (SVM), joblib, MinMaxScaler
- **Frontend:** Bootstrap 5, Chart.js, vanilla JavaScript
- **Training Environment:** Kaggle Notebook

## Struktur Proyek

```
D:\JOKI\
├── PRD_SPK_PKH.md          -- Product Requirements Document
├── PRD_R1.md               -- Ringkasan final hasil
├── RENCANA_IMPLEMENTASI.md -- Timeline dan milestones
├── RENCANA_IMPLEMENTASI_R1.md -- Checklist final semua fase
├── ARSITEKTUR_SISTEM.md    -- DFD, ERD, Flowchart, Tech Stack
├── Penentuan Kriteria.txt  -- Dokumen resmi dari Tim PKH
├── Penentuan Indikator Kriteria.txt -- Skema encoding resmi
├── svm-pkh-ta.ipynb        -- Notebook training final (v3)
├── dataset real/           -- Dataset CSV dari pendamping PKH
├── docs/                   -- Dokumentasi per sesi kerja
│   ├── 01-pra-pengembangan/
│   ├── 02-training-model/
│   ├── 03-pembuatan-web/
│   ├── 04-integrasi/
│   └── 05-revisi/
├── web/                    -- Source code Flask app
│   ├── app.py              -- Entry point
│   ├── config.py           -- Konfigurasi
│   ├── models_db.py        -- SQLAlchemy models
│   ├── svm_predictor.py    -- SVM inference service
│   ├── core/               -- Business logic
│   │   ├── constants.py    -- Mapping ordinal 1-5
│   │   ├── scoring.py      -- Konversi skor
│   │   ├── predictor.py    -- Singleton predictor
│   │   ├── data_io.py      -- Import/Export service
│   │   ├── auth.py         -- Autentikasi
│   │   ├── security.py     -- Security headers
│   │   ├── limiter.py      -- Rate limiting
│   │   └── error_handlers.py
│   ├── routes/             -- Flask Blueprints
│   ├── templates/          -- Jinja2 templates
│   ├── static/             -- CSS, JS, images
│   └── models/             -- Model .pkl
└── memory/                 -- Konteks internal (gitignored)
```

## Instalasi dan Menjalankan

1. Clone repositori.
2. Install dependensi:
   ```
   cd web
   pip install -r requirements.txt
   ```
3. Jalankan aplikasi:
   ```
   cd web
   python app.py
   ```
4. Buka `http://localhost:5000` di browser.
5. Login dengan akun default: `admin` / `admin123`.

> Akun default akan meminta ganti password pada login pertama.

## Dokumentasi Sidang

Dokumen `PRD_R1.md` berisi ringkasan final yang mencakup:
- Perbandingan prototype vs hasil real
- Penjelasan perubahan encoding dan normalisasi
- Confusion matrix dan metrik evaluasi
- Catatan untuk menjawab pertanyaan penguji
