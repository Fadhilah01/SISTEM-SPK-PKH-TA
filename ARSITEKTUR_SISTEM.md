# Arsitektur Sistem & Tech Stack
## SPK Kelayakan Calon Penerima Bantuan PKH - SVM

---

## 1. Arsitektur Sistem Secara Umum

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USER (Pendamping PKH)                        │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    WEB APPLICATION (Flask)                          │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐     │
│  │   Flask      │  │   Jinja2     │  │   Bootstrap 5 UI      │     │
│  │   Routes     │  │   Templates  │  │   (Responsive)        │     │
│  └──────┬───────┘  └──────────────┘  └────────────────────────┘     │
│         │                                                           │
│         ▼                                                           │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │              SERVICE LAYER                                 │      │
│  │  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐    │      │
│  │  │ DataService  │  │  SVMPredictor│  │ ReportService│    │      │
│  │  └─────────────┘  └──────┬───────┘  └──────────────┘    │      │
│  └──────────────────────────┼───────────────────────────────┘      │
│                             │                                       │
│  ┌──────────────────────────▼───────────────────────────────┐      │
│  │              INFERENCE ENGINE                              │      │
│  │  ┌──────────────────────────────────────┐                │      │
│  │  │  Load Model (joblib) → SVM Classifier│                │      │
│  │  │  Preprocessing Pipeline               │                │      │
│  │  │  (MinMaxScaler → SVM Predict)         │                │      │
│  │  └──────────────────────────────────────┘                │      │
│  └──────────────────────────────────────────────────────────┘      │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │              DATABASE (SQLite)                             │      │
│  │  ┌──────────┐ ┌──────────┐                               │      │
│  │  │ Calon    │ │ Keputusan│                               │      │
│  │  │ Penerima │ │          │                               │      │
│  │  └──────────┘ └──────────┘                               │      │
│  └──────────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────┘
                            │
                            │ (Model Training via Kaggle)
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     KAGGLE NOTEBOOK (Python)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │ Dataset  │→ │Preprocess│→ │Train SVM │→ │Evaluate (Conf.   │  │
│  │          │  │(Ordinal  │  │(Grid     │  │Matrix, Akurasi,  │  │
│  │          │  │Encode,   │  │Search CV)│  │Presisi, Recall)  │  │
│  │          │  │MinMax    │  │          │  │                  │  │
│  │          │  │Scale,    │  │          │  │                  │  │
│  │          │  │Split)    │  │          │  │                  │  │
│  └──────────┘  └──────────┘  └──────────┘  └────────┬─────────┘  │
│                                                      │             │
│                                                      ▼             │
│                                            ┌──────────────────┐  │
│                                            │ Export Model     │  │
│                                            │ (joblib .pkl)    │  │
│                                            └──────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### Penjelasan Arsitektur

Sistem ini terdiri dari dua komponen utama yang saling terhubung:

1. **Kaggle Notebook** — tempat model SVM dilatih. Di sini saya melakukan preprocessing data (encoding ordinal, normalisasi Min-Max), training model dengan GridSearchCV, evaluasi performa, dan mengekspor model dalam format `.pkl`.

2. **Web Application Flask** — tempat model digunakan untuk prediksi. Arsitektur web dirancang secara modular menggunakan pola **Application Factory** dan **Flask Blueprints** untuk memisahkan domain fungsionalitas secara clean, serta diperkuat oleh **Proteksi CSRF Kustom** untuk menangkal serangan Cross-Site Request Forgery.

Kedua komponen terhubung melalui file `.pkl` — model yang sudah dilatih di Kaggle diunduh dan diletakkan di folder `web/models/` untuk digunakan oleh Flask.

### Pembagian Modul (Blueprints)
- **auth_bp** (`routes/auth.py`): Mengatur proses login & logout admin pendamping.
- **dashboard_bp** (`routes/dashboard.py`): Mengatur ringkasan statistik di beranda, serta menyediakan endpoint API `/api/analytics` untuk visualisasi grafik analitis interaktif (drill-down wilayah bertingkat, tren temporal, komparasi periode/kriteria).
- **calon_bp** (`routes/calon.py`): Mengatur manajemen CRUD data calon penerima serta pemicuan klasifikasi ulang SVM.
- **about_bp** (`routes/about.py`): Mengatur detail metrik evaluasi model SVM, visualisasi confusion matrix, dan modul FAQ.

### Keamanan Web & Proteksi CSRF
Sistem mengimplementasikan pengaman serangan CSRF kustom. Token acak 32-byte dihasilkan secara kriptografis via modul `secrets` Python dan disimpan dalam session user. Setiap request bermetode `POST` (seperti form submit data, hapus data, login, dan logout) wajib menyertakan token tersembunyi `_csrf_token` yang akan divalidasi oleh dekorator `@csrf_required` di backend. Jika token tidak valid atau hilang, server akan otomatis menolak request dan mengembalikan status **403 Forbidden**.

## 2. Tech Stack

### Web Application
| Komponen | Teknologi | Alasan |
|----------|-----------|--------|
| **Framework** | Python Flask | Ringan, mudah integrasi ML model, Python ecosystem |
| **Database** | SQLite | Portabel, zero config, cocok untuk skala kecil |
| **ORM** | SQLAlchemy | Standar Python ORM, abstraksi query database |
| **Frontend** | Bootstrap 5 + Jinja2 | Responsif, komponen siap pakai |
| **Template Engine** | Jinja2 | Default Flask, mendukung inheritance template |
| **ML Integration** | joblib + scikit-learn | Load model SVM .pkl langsung dari Python |
| **Charts** | Chart.js | Visualisasi hasil evaluasi di browser |

### Machine Learning (Kaggle)
| Komponen | Teknologi |
|----------|-----------|
| **Platform** | Kaggle Notebook |
| **Runtime** | Python 3.x |
| **ML Library** | scikit-learn (SVC) |
| **Data Processing** | pandas, numpy |
| **Preprocessing** | Ordinal Encoding manual (mapping dictionary 1-5), MinMaxScaler |
| **Evaluation** | accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report |

### Skema Encoding (Berdasarkan Dokumen Tim PKH Sulteng)

Preprocessing menggunakan **Ordinal Encoding** manual sesuai indikator resmi, bukan LabelEncoder otomatis. Alasan utamanya: ordinal encoding mempertahankan **urutan tingkat kelayakan** — skor 5 berarti paling layak (paling miskin/rentan), skor 1 berarti paling tidak layak. SVM bisa memahami bahwa jarak antara skor 5 dan 1 itu jauh, sedangkan jarak antara 5 dan 4 itu dekat.

| Fitur | Skema Encoding | Rentang |
|-------|---------------|---------|
| Penghasilan | Desil → 1-5 (semakin tinggi skor = semakin miskin) | 1-5 |
| Pekerjaan | PNS=1 s.d Tidak Bekerja=5 | 1-5 |
| Kepemilikan Aset | Mobil+Tanah=1 s.d Tidak Punya=5 | 1-5 |
| Ibu Hamil | Tidak=0, Ada=1 | 0-1 |
| Anak Usia Dini | Tidak=0, Ada=1 | 0-1 |
| Anak Sekolah | Tidak=0, Ada=1 | 0-1 |
| Disabilitas | Tidak=0, Ada=1 | 0-1 |
| Lansia | Tidak=0, Ada=1 | 0-1 |

Normalisasi menggunakan **Min-Max Normalization** (bukan StandardScaler) — menjaga rentang data antara 0 dan 1 tanpa mengubah distribusi, lebih cocok untuk data ordinal.

> **Catatan Historis:** Pada prototype awal (data sintetis), saya menggunakan LabelEncoder dan StandardScaler. Setelah menerima dokumen resmi dari Tim PKH Sulteng pada 3 Juli 2026, skema encoding diubah menjadi ordinal manual 1-5 dan normalisasi diubah ke MinMaxScaler. Lihat `docs/04-integrasi/sesi-2026-07-03-audit-gap-analisis.md` untuk detail gap analisis.

### Format Pipeline .pkl

Model diekspor dalam format **dictionary** (bukan class) agar mudah di-load di web tanpa perlu definisi class terpisah:

```python
pipeline = {
    'model': best_svm,           # SVM classifier (scikit-learn SVC)
    'scaler': scaler,            # MinMaxScaler (fitted)
    'feature_cols': [...],       # List nama fitur
    'results': {                 # Metrik evaluasi
        'accuracy': ...,
        'precision': ...,
        'recall': ...,
        'f1': ...,
        'best_params': {...}
    }
}
```

> **Catatan Historis:** Prototype awal menyimpan class `SVMPipeline` sebagai .pkl. Format ini diubah ke dictionary karena lebih sederhana dan tidak bergantung pada definisi class.

### Tools Development
| Tool | Kegunaan |
|------|----------|
| VS Code | IDE |
| Git | Version control |
| Kaggle | Model training |

## 3. Data Flow Diagram (DFD)

### DFD Level 0 (Context Diagram)
```
                    ┌────────────────────┐
                    │   Pendamping PKH   │
                    └────────┬───────────┘
                             │
                 ┌───────────▼────────────────┐
                 │                             │
                 │   SPK Kelayakan PKH         │
                 │   (SVM)                     │
                 │                             │
                 └───────────┬────────────────┘
                             │
                    ┌────────▼───────────┐
                    │   Model SVM       │
                    │   (Kaggle)        │
                    └────────────────────┘
```

**Penjelasan:** Pendamping PKH berinteraksi dengan sistem SPK melalui web. Sistem menggunakan model SVM yang sudah dilatih di Kaggle untuk mengklasifikasikan data. Pendamping memasukkan data calon penerima dan menerima hasil klasifikasi.

### DFD Level 1
```
                    ┌────────────────────┐
                    │   Pendamping PKH   │
                    └────────┬───────────┘
          Input Data Calon   │   Hasil Keputusan
                    ┌────────▼────────────────┐
                    │   1.0                   │
                    │   Input Data Calon      │
                    │   Penerima (Kategori)   │
                    └────────┬────────────────┘
                             │ Data Calon (skor ordinal)
                             ▼
                    ┌────────────────┐
                    │  Database      │
                    │  Calon         │
                    └────────┬───────┘
                             │ Data Calon
                             ▼
                    ┌─────────────────────────┐
                    │   2.0                   │
                    │   Preprocessing &       │
                    │   Klasifikasi SVM       │
                    │   (MinMax → Predict)    │
                    └────────┬────────────────┘
                             │ Hasil Prediksi
                             ▼
                    ┌──────────────────────────┐
                    │   3.0                    │
                    │   Tampilkan Hasil        │
                    │   Keputusan              │
                    └────────┬─────────────────┘
                             │
                    ┌────────▼───────────┐
                    │   Pendamping PKH   │
                    └────────────────────┘
```

**Penjelasan:** Data calon penerima dimasukkan dalam bentuk kategori (dropdown), sistem mengkonversi ke skor ordinal, menyimpan ke database, lalu memproses melalui MinMaxScaler dan model SVM untuk menghasilkan klasifikasi Layak/Tidak Layak.

## 4. Entity Relationship Diagram (ERD)

```
┌────────────────────────┐
│         User           │
├────────────────────────┤
│ PK id (int)            │
│    username (string)   │
│    password_hash       │
│    (string)            │
│    nama_lengkap        │
│    (string)            │
│    role (string)       │
│    created_at          │
│    (datetime)          │
└────────────────────────┘

┌────────────────────────┐
│     Calon Penerima     │
├────────────────────────┤
│ PK id (int)            │──────────┐
│    nama (string)       │          │
│    alamat (text)       │          │
│    provinsi (string)   │          │
│    kabupaten (string)  │          │
│    kecamatan (string)  │          │
│    desa_kelurahan      │          │
│    (string)            │          │
│    penghasilan (string)│          │
│    pekerjaan (string)  │          │
│    kepemilikan_aset    │          │
│    (string)            │          │
│    ibu_hamil (bool)    │          │
│    anak_usia_dini(bool)│          │
│    anak_sekolah (bool) │          │
│    disabilitas (bool)  │          │
│    lansia (bool)       │          │
│    skor_penghasilan    │          │
│    (int, 1-5)          │          │
│    skor_pekerjaan      │          │
│    (int, 1-5)          │          │
│    skor_kepemilikan_aset          │
│    (int, 1-5)          │          │
│    skor_ibu_hamil(int) │          │
│    skor_anak_usia_dini            │
│    (int, 0/1)          │          │
│    skor_anak_sekolah   │          │
│    (int, 0/1)          │          │
│    skor_disabilitas(int)          │
│    skor_lansia (int)   │          │
│    created_at          │          │
└────────────────────────┘          │
                                    │
┌────────────────────────┐          │
│    Hasil Keputusan     │          │
├────────────────────────┤          │
│ PK id (int)            │◄─────────┘
│ FK id_calon (int)      │
│    hasil_prediksi      │
│    (bool)              │
│    label_prediksi      │
│    (string)            │
│    probabilitas(float) │
│    tanggal_prediksi    │
│    (datetime)          │
│    oleh (string)       │
└────────────────────────┘
```

**Penjelasan:** Tabel `User` menyimpan data autentikasi admin. Tabel `Calon Penerima` menyimpan data masukan teks kategori beserta nilai skor hasil pemetaan (skor 1-5 untuk kriteria ordinal, 0/1 untuk biner) secara terpisah. Tabel `Hasil Keputusan` menyimpan hasil output prediksi SVM dan terhubung one-to-one dengan tabel `Calon Penerima`. Kolom `oleh` pada `Hasil Keputusan` mencatat ID pengguna yang melakukan proses input data tersebut.

> **Catatan Historis:** ERD awal menyimpan penghasilan sebagai float (rupiah) dan anak_usia_dini, anak_sekolah, lansia sebagai integer (jumlah). Setelah menerima dokumen resmi PKH, semua diubah menjadi skor ordinal/biner sesuai indikator resmi.

## 5. Flowchart Sistem

```
                   ┌─────────────┐
                   │    START    │
                   └──────┬──────┘
                          │
                          ▼
              ┌───────────────────────┐
              │ Pendamping pilih      │
              │ kategori dari dropdown│
              │ (penghasilan, kerja,  │
              │  aset, komponen sosial)│
              └──────────┬────────────┘
                         │
                         ▼
              ┌───────────────────────┐
              │ Sistem konversi       │
              │ kategori → skor      │
              │ ordinal (1-5 / 0-1)  │
              └──────────┬────────────┘
                         │
                         ▼
              ┌───────────────────────┐
              │ Validasi & Simpan     │
              │ ke Database           │
              └──────────┬────────────┘
                         │
                         ▼
              ┌───────────────────────┐
              │ Normalisasi (MinMax)  │
              │ → Skala 0 sampai 1   │
              └──────────┬────────────┘
                         │
                         ▼
              ┌───────────────────────┐
              │ Load Model SVM (.pkl) │
              └──────────┬────────────┘
                         │
                         ▼
              ┌───────────────────────┐
              │ Prediksi dengan SVM   │
              └──────────┬────────────┘
                         │
                         ▼
              ┌───────────────────────┐
              │   Hasil:              │
              │ Layak / Tidak Layak   │
              │ + Probabilitas (%)    │
              └──────────┬────────────┘
                         │
                         ▼
              ┌───────────────────────┐
              │ Simpan Hasil ke DB    │
              │ Tampilkan ke User     │
              └──────────┬────────────┘
                         │
                         ▼
                    ┌─────────┐
                    │  END    │
                    └─────────┘
```

## 6. Alur Training Model di Kaggle

```
                    ┌──────────────┐
                    │ Upload Dataset│
                    │ ke Kaggle    │
                    └──────┬───────┘
                           │
                           ▼
              ┌──────────────────────────┐
              │ 1. Load Dataset (pandas) │
              └──────────┬───────────────┘
                         │
                         ▼
              ┌──────────────────────────┐
              │ 2. Data Preprocessing    │
              │    - Handle missing vals │
              │    - Ordinal Encoding    │
              │      (mapping manual     │
              │       1-5 sesuai         │
              │       dokumen resmi)     │
              │    - MinMax Normalisasi  │
              │    - Train/Test Split    │
              │      (80/20, stratified) │
              └──────────┬───────────────┘
                         │
                         ▼
              ┌──────────────────────────┐
              │ 3. Train SVM Model       │
              │    - Coba kernel: linear │
              │      RBF, polynomial     │
              │    - GridSearchCV utk    │
              │      parameter terbaik   │
              │      (C, gamma)          │
              └──────────┬───────────────┘
                         │
                         ▼
              ┌──────────────────────────┐
              │ 4. Evaluasi Model        │
              │    - Confusion Matrix    │
              │    - Akurasi, Presisi,   │
              │      Recall, F1-Score    │
              └──────────┬───────────────┘
                         │
                         ▼
              ┌──────────────────────────┐
              │ 5. Export Model (.pkl)   │
              │    - Dictionary format   │
              │    - model + scaler +    │
              │      feature_cols +      │
              │      results             │
              └──────────┬───────────────┘
                         │
                         ▼
              ┌──────────────────────────┐
              │ 6. Download model ke     │
              │    local → Integrasi ke  │
              │    Flask web app         │
              └──────────────────────────┘
```
