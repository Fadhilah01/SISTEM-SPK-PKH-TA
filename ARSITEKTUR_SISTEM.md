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
│  │  │  (Encoder + Scaler + Feature Select)  │                │      │
│  │  └──────────────────────────────────────┘                │      │
│  └──────────────────────────────────────────────────────────┘      │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │              DATABASE (SQLite/PostgreSQL)                  │      │
│  │  ┌──────────┐ ┌──────────┐ ┌───────────────┐            │      │
│  │  │ Calon    │ │ Keputusan│ │ Prediksi Log  │            │      │
│  │  │ Penerima │ │          │ │               │            │      │
│  │  └──────────┘ └──────────┘ └───────────────┘            │      │
│  └──────────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────┘
                            │
                            │ (Model Training via Kaggle)
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     KAGGLE NOTEBOOK (Python)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │ Dataset  │→ │Preprocess│→ │Train SVM │→ │Evaluate (Conf.   │  │
│  │          │  │(Encode,  │  │(Grid     │  │Matrix, Akurasi,  │  │
│  │          │  │Scale,    │  │Search CV)│  │Presisi, Recall)  │  │
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

## 2. Tech Stack

### Web Application
| Komponen | Teknologi | Alasan |
|----------|-----------|--------|
| **Framework** | Python Flask | Ringan, mudah integrasi ML model, client familiar Python ecosystem |
| **Database** | SQLite (dev) / PostgreSQL (prod) | SQLite untuk portabel, PostgreSQL untuk production |
| **ORM** | SQLAlchemy | Standar Python ORM |
| **Frontend** | Bootstrap 5 + Jinja2 | Responsif, skripsi-standard |
| **Template Engine** | Jinja2 | Default Flask |
| **ML Integration** | joblib + scikit-learn | Load model SVM .pkl langsung dari Python |
| **Charts** | Chart.js | Visualisasi hasil evaluasi |

### Machine Learning (Kaggle)
| Komponen | Teknologi |
|----------|-----------|
| **Platform** | Kaggle Notebook |
| **Runtime** | Python 3.x |
| **ML Library** | scikit-learn (SVC) |
| **Data Processing** | pandas, numpy |
| **Preprocessing** | Ordinal Encoding (manual mapping 1-5), MinMaxScaler (bukan StandardScaler) |
| **Evaluation** | accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report |

### Skema Encoding (Berdasarkan Dokumen Tim PKH Sulteng)
Preprocessing menggunakan **Ordinal Encoding** manual sesuai indikator resmi, bukan LabelEncoder otomatis:

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

Normalisasi menggunakan **Min-Max Normalization** (bukan StandardScaler) — sesuai dokumen revisi Pak Yazdi.

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

### DFD Level 1
```
                    ┌────────────────────┐
                    │   Pendamping PKH   │
                    └────────┬───────────┘
          Input Data Calon   │   Hasil Keputusan
                    ┌────────▼────────────────┐
                    │   1.0                   │
                    │   Input Data Calon      │
                    │   Penerima              │
                    └────────┬────────────────┘
                             │ Data Calon
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

## 4. Entity Relationship Diagram (ERD)

```
┌──────────────────────┐
│   Calon Penerima     │
├──────────────────────┤
│ PK id_calon (int)    │──────────┐
│    nama (string)     │          │
│    alamat (text)     │          │
│    penghasilan (int) │          │
│    penghasilan_skor │          │
│    (int, 1-5)        │          │
│    pekerjaan_skor    │          │
│    (int, 1-5)        │          │
│    aset_skor         │          │
│    (int, 1-5)        │          │
│    ibu_hamil (bool)  │          │
│    anak_usia_dini    │          │
│    (bool)            │          │
│    anak_sekolah (bool)│         │
│    disabilitas (bool)│          │
│    lansia (bool)     │          │
│    created_at        │          │
└──────────────────────┘          │
                                  │
┌──────────────────────┐          │
│   Hasil Keputusan    │          │
├──────────────────────┤          │
│ PK id_keputusan(int) │<─────────┘
│ FK id_calon (int)    │
│    hasil_prediksi    │
│    (bool)            │
│    label_prediksi    │
│    (string)          │
│    probabilitas(float)│
│    tanggal_prediksi  │
│    (datetime)        │
│    oleh (string)     │
└──────────────────────┘
```

## 5. Flowchart Sistem

```
                   ┌─────────────┐
                   │    START    │
                   └──────┬──────┘
                          │
                          ▼
              ┌───────────────────────┐
              │ Pendamping input data  │
              │ calon penerima         │
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
              │ Preprocessing Data    │
              │ - Encode kategorikal  │
              │ - Normalisasi numerik │
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
              │    - Encoding kategori   │
              │    - Normalisasi         │
              │    - Train/Test Split    │
              │      (80/20)             │
              └──────────┬───────────────┘
                         │
                         ▼
              ┌──────────────────────────┐
              │ 3. Train SVM Model       │
              │    - Coba kernel: linear │
              │      RBF, polynomial     │
              │    - GridSearchCV utk    │
              │      parameter terbaik   │
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
              │    + Pipeline lengkap    │
              └──────────┬───────────────┘
                         │
                         ▼
              ┌──────────────────────────┐
              │ 6. Download model ke     │
              │    local → Integrasi ke  │
              │    Flask web app         │
              └──────────────────────────┘
```
