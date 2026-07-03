# Log Harian 04: Audit & Gap Analisis — Model vs Dokumen Resmi PKH
**Tanggal:** 3 Juli 2026
**Durasi:** ~2 jam

---

## Kegiatan yang Dilakukan

Setelah menerima dokumen rujukan resmi mengenai indikator penilaian kelayakan PKH dari Ketua Tim SDM PKH Provinsi Sulawesi Tengah (Bapak Zainal), yaitu:
- `Penentuan Kriteria.txt` — memuat 8 kriteria kelayakan beserta bobot penilaian resminya.
- `Penentuan Indikator Kriteria.txt` — memuat detail sub-kriteria beserta skema penilaian ordinal skala 1-5.

Saya melakukan audit menyeluruh terhadap seluruh codebase untuk mengecek apakah model SVM, web SPK, dan database yang sudah dibuat sesuai dengan dokumen resmi tersebut.

Hasilnya: ditemukan **5 gap kritis** (ketidaksesuaian) yang harus diperbaiki sebelum sistem bisa digunakan.

---

## Temuan Gap

### Gap 1: Encoding Tidak Sesuai Dokumen Resmi

| Aspek | Kondisi Saat Ini (Notebook + Web) | Seharusnya (Dokumen Resmi) |
|-------|-----------------------------------|----------------------------|
| **Penghasilan** | Input angka Rupiah mentah (float) | **Ordinal 1-5** berdasarkan kategori Desil |
| **Pekerjaan** | LabelEncoder otomatis (mapping alfabetis acak) | **Ordinal 1-5** (Tidak Bekerja=5, Pekerja Bebas=4, Petani/Nelayan=3, Wiraswasta=2, PNS/Pegawai Tetap=1) |
| **Kepemilikan Aset** | LabelEncoder otomatis (mapping alfabetis acak) | **Ordinal 1-5** (Tidak Memiliki Aset=5, Motor Harga Rendah=4, Motor Harga Tinggi=3, Mobil/Tanah=2, Mobil dan Tanah=1) |

**Kenapa ini masalah?**
LabelEncoder otomatis memberikan angka berurutan berdasarkan alfabet, bukan berdasarkan tingkat kerentanan/kelayakan. Misalnya, "Buruh" bisa di-encode menjadi 0 dan "PNS" menjadi 7. Hal ini **tidak sesuai** karena model SVM tidak bisa membaca hubungan urutan kelayakan secara logis (seharusnya kategori yang lebih miskin/rentan memiliki bobot nilai numerik yang lebih tinggi).

Dengan encoding ordinal manual 1-5 dari dokumen resmi, sebaran angka memiliki makna: skor 5 = paling layak (paling miskin), skor 1 = paling tidak layak. Ini jauh lebih sesuai untuk SVM karena model dapat memahami bahwa jarak antara "Tidak Bekerja" (skor 5) dan "PNS" (skor 1) itu jauh, sedangkan jarak "Tidak Bekerja" dan "Pekerja Bebas" (skor 4) itu dekat.

### Gap 2: Normalisasi (Scaler) Tidak Sesuai

| Kondisi Saat Ini | Seharusnya |
|-------------------|------------|
| `StandardScaler` (z-score normalization) | **`MinMaxScaler`** (Min-Max normalization 0-1) |

**Kenapa ini masalah?**
StandardScaler mengubah sebaran data menjadi distribusi z-score dengan mean=0 dan std=1. Ini cocok untuk data yang berdistribusi normal, namun kurang sesuai untuk data kriteria PKH yang bertipe ordinal skala 1-5 dan biner (0/1). MinMaxScaler jauh lebih cocok karena menjaga rentang data tetap berada di antara 0 dan 1 tanpa mengubah karakteristik sebaran data asli.

Selain itu, **revisi dari Pak Yazdi Pusadan** secara spesifik meminta penggunaan Min-Max Normalization untuk menormalisasi data ordinal. Oleh karena itu, penggunaan StandardScaler pada implementasi awal **tidak sesuai** dan harus diganti.

### Gap 3: Kategori Form Web Tidak Cocok

Kategori pilihan pada form input web saat ini **tidak sesuai** dengan kategori resmi dari dinas sosial:

**Pekerjaan — saat ini di web:**
`Tidak Bekerja, Buruh, Petani, Nelayan, Pedagang Kecil, IRT, PNS, Karyawan Swasta, Lainnya`

**Pekerjaan — seharusnya (dokumen resmi):**
`Tidak Bekerja (skor 5), Pekerja Bebas (skor 4), Petani/Nelayan (skor 3), Wiraswasta (skor 2), PNS/Pegawai Tetap (skor 1)`

**Kepemilikan Aset — saat ini di web:**
`Tidak Punya, Rumah Sangat Sederhana, Rumah Sederhana, Lahan Terbatas, Lainnya`

**Kepemilikan Aset — seharusnya (dokumen resmi):**
`Tidak Memiliki Aset (skor 5), Motor harga jual rendah (skor 4), Motor harga jual tinggi (skor 3), Mobil atau Tanah/Kebun (skor 2), Mobil dan Tanah/Kebun (skor 1)`

**Penghasilan — saat ini di web:**
Input nominal Rupiah (field number)

**Penghasilan — seharusnya (dokumen resmi):**
Dropdown 5 kategori Desil:
- Desil 1: < Rp.500.000 (skor 5)
- Desil 2: Rp.600.000 – Rp.700.000 (skor 4)
- Desil 3: Rp.800.000 – Rp.900.000 (skor 3)
- Desil 4: Rp.1.000.000 – Rp.1.200.000 (skor 2)
- Desil 5: Rp.1.300.000 – Rp.1.500.000 (skor 1)

### Gap 4: Format Pipeline .pkl Tidak Konsisten

Notebook Kaggle mengekspor model sebagai **instance class `SVMPipeline`** (objek Python lengkap). Namun, modul `svm_predictor.py` di web mengharapkan **dictionary** dengan key data.

**Kenapa ini masalah?**
Perbedaan format serialisasi ini membuat modul web Flask mengalami error saat memuat model. Karena web mengharapkan tipe data dictionary Python, format pemodelan kustom pada notebook awal **tidak cocok** dan harus diselaraskan. Diputuskan untuk menggunakan format dictionary karena lebih stabil dan mudah diintegrasikan dengan backend web.

### Gap 5: Tipe Data Kolom Sosial di Database

| Kolom | Tipe di DB Saat Ini | Seharusnya (Dokumen Resmi) |
|-------|---------------------|----------------------------|
| `ibu_hamil` | Boolean | Biner 0/1 — ✅ sudah benar |
| `anak_usia_dini` | Integer (jumlah anak) | **Biner 0/1** (Ada/Tidak Ada) |
| `anak_sekolah` | Integer (jumlah anak) | **Biner 0/1** (Ada/Tidak Ada) |
| `disabilitas` | Boolean | Biner 0/1 — ✅ sudah benar |
| `lansia` | Integer (jumlah lansia) | **Biner 0/1** (Ada/Tidak Ada) |

**Kenapa ini masalah?**
Dokumen resmi kriteria kelayakan hanya menanyakan status keberadaan komponen sosial ("Ada atau Tidak Ada"), bukan kuantitas jumlah jiwa anak atau lansia. Oleh karena itu, tipe data integer untuk kolom `anak_usia_dini`, `anak_sekolah`, dan `lansia` pada rancangan awal database **tidak sesuai** dan harus diubah menjadi tipe biner.

---

## Keputusan Perbaikan

| Keputusan | Justifikasi / Alasan |
|-----------|--------|
| **Semua gap harus diperbaiki sebelum retraining** | Model SVM yang dilatih dengan skema encoding yang salah akan menghasilkan pola klasifikasi yang salah. Jadi kode pemrosesan harus diperbaiki terlebih dahulu. |
| **Penerapan perbaikan dilakukan saat dataset riil siap** | Menggabungkan proses pembaruan skema database, form input web, dan skrip preprocessing pada notebook agar integrasi berjalan selaras dalam satu fase pengerjaan. |
| **Menggunakan format dictionary pada file `.pkl`** | Format ini lebih sederhana, meminimalkan ketergantungan kode backend terhadap definisi kelas objek eksternal, dan mudah didebug. |
| **Mengubah input form web menjadi pilihan dropdown kategori** | Sesuai dokumen resmi dinas sosial, membatasi input pengguna untuk menghindari kesalahan pengisian data (*human error*). |

---

## Dampak pada Komponen Sistem (Yang Harus Diubah)

1. **Notebook Kaggle:**
   - Ganti `LabelEncoder` otomatis dengan pemetaan ordinal manual (skala 1-5).
   - Ganti `StandardScaler` dengan `MinMaxScaler`.
   - Sesuaikan kategori pekerjaan dan aset menjadi 5 kriteria resmi.
   - Konversi isian nominal penghasilan menjadi skor desil 1-5.
   - Ekspor model dalam format Python dictionary, bukan class kustom.

2. **Modul Prediktor (`svm_predictor.py`):**
   - Hapus pemrosesan `LabelEncoder` karena input web sudah langsung berupa nilai skor.
   - Sesuaikan pemuatan model pipeline dengan tipe dictionary.

3. **Skema Database (`models_db.py`):**
   - Mengubah kolom `anak_usia_dini`, `anak_sekolah`, dan `lansia` dari Integer menjadi Boolean.
   - Menambahkan kolom pencatatan nilai skor untuk mempermudah perhitungan dan dokumentasi.

4. **Controller Utama (`app.py`):**
   - Memperbarui fungsi form data agar menerima input skor ordinal.
   - Memperbarui daftar isian dropdown pekerjaan dan kepemilikan aset.

5. **Antarmuka Formulir (`calon_form.html`):**
   - Isian penghasilan diubah menjadi dropdown desil.
   - Isian pekerjaan dan aset diubah menjadi dropdown 5 kategori resmi.
   - Isian komponen sosial diubah menjadi pilihan checkbox biner.

---

## Kendala & Solusi Migrasi

| Potensi Kendala | Rencana Mitigasi |
|---------|--------|
| Model prototype sintetis lama dilatih dengan encoding yang salah | Model sintetis lama disimpan sebagai dokumen pembanding awal. Model akhir akan dilatih ulang menggunakan data riil lapangan dengan skema baru. |
| Ketidakcocokan struktur data database lama | Melakukan reset database lokal (`spk_pkh.db`) sebelum menginput data riil lapangan (database belum masuk tahap produksi). |
| Notebook versi lama masih menggunakan `LabelEncoder` | Memperbarui kode notebook ke versi terbaru saat melakukan retraining. |

---

## Perubahan dari Rencana Perancangan Awal

Rencana Awal (Prototype):
- Proses encoding menggunakan `LabelEncoder` otomatis.
- Metode normalisasi menggunakan `StandardScaler`.
- Input data berupa nilai numerik mentah (nominal rupiah, jumlah anak).

Rencana Baru (Penyelarasan Instrumen Resmi):
- Proses encoding menggunakan ordinal encoding manual (1-5).
- Metode normalisasi menggunakan `MinMaxScaler`.
- Input data diselaraskan dengan dropdown kategori resmi dan checkbox biner.

**Justifikasi Perubahan:** Langkah penyesuaian ini menjamin program SPK yang dikembangkan memiliki tingkat validitas akademis dan kegunaan praktis yang tinggi karena memodelkan aturan keputusan yang berlaku riil pada instansi dinas sosial setempat.

---

## Justifikasi Metodologis (Materi Pendukung Laporan & Sidang)

### Pertanyaan Antisipatif Penguji: 
*“Mengapa terjadi perubahan skema pra-pemrosesan data (encoding dan penskalan) pada model SVM Anda?”*

### Jawaban Justifikasi:
> "Pada awal pengembangan sistem (fase perancangan), saya menggunakan `LabelEncoder` otomatis dan `StandardScaler` untuk kebutuhan pengujian prototype model menggunakan dataset sintetis awal. Namun, setelah berkoordinasi langsung dengan Ketua Tim SDM PKH Provinsi Sulawesi Tengah dan memperoleh dokumen instrumen penilaian resmi (berdasarkan Keputusan Dirjen Linjamsos No. 9/3/HK.01.1/2025), saya memutuskan melakukan penyesuaian skema pra-pemrosesan data.
> 
> Penggunaan `LabelEncoder` otomatis digantikan dengan ordinal encoding manual skala 1-5 agar model SVM dapat mengenakili tingkat kepentingan kriteria secara logis (misalnya, nilai kriteria pekerjaan 'Tidak Bekerja' dipetakan ke skor 5 sebagai prioritas tertinggi penerima bantuan, dan 'PNS' ke skor 1). 
> 
> Selain itu, penskalan data diubah dari `StandardScaler` menjadi `MinMaxScaler` atas saran dari dosen pembimbing (Bapak Yazdi Pusadan) agar seluruh rentang data ordinal (skala 1-5) dan biner (0/1) berada pada rentang nilai seragam 0 hingga 1 tanpa mengubah karakteristik sebaran data aslinya. Penyesuaian ini menjamin model SVM memproses data secara objektif sesuai aturan penilaian dinas sosial."

---

## Output Progres

- ✅ Evaluasi menyeluruh terhadap kode program selesai dilakukan
- ✅ 5 poin perbedaan kritis berhasil teridentifikasi dan terdokumentasi
- ✅ Rencana pembaruan kode untuk tiap file pemrograman telah dipetakan
- ✅ Rancangan argumentasi akademis untuk sesi sidang skripsi disiapkan
- ⏳ Penerapan pembaruan kode pemrograman dan retraining model menggunakan dataset riil
