# Log Harian 09: Integrasi Pencarian Wilayah Autocomplete (Internal API) dan Visualisasi Sebaran Desa Dinamis
**Tanggal:** 7 Juli 2026
**Durasi:** ~5 jam

---

## Kegiatan yang Dilakukan

Untuk mempermudah pendataan calon penerima bantuan PKH dan menghindari kesalahan penulisan alamat secara manual (teks bebas) yang menyebabkan inkonsistensi data, saya mengimplementasikan sistem pencarian wilayah bertingkat berbasis data resmi BPS/Kemendagri:

1. **Integrasi Data Wilayah Administratif Sulawesi Tengah:**
   * Mengompilasi data referensi resmi BPS/Kemendagri sebanyak **89.554 entitas wilayah** se-Indonesia (flat array) dan menyimpannya secara lokal di dalam file JSON `web/static/data/daerah_indonesia.json`. Hal ini penting untuk performa agar website tidak bergantung pada API eksternal pihak ketiga.
   * Membuat endpoint API internal `GET /api/daerah?q=...&level=...&parent=...` pada berkas `routes/calon.py` untuk melayani pencarian wilayah secara cepat dengan teknik *lazy loading* dan *in-memory cache*.
   * Mengatasi masalah kemiripan nama desa (misalnya nama desa sama namun berbeda kecamatan) dengan menyusun dan mengirimkan string nama lengkap terstruktur (`fullname`) secara dinamis (contoh: "KASIMBAR PALAPI, KASIMBAR, PARIGI MOUTONG, SULAWESI TENGAH") agar admin dapat membedakannya dengan mudah di menu autocomplete.

2. **Pembaruan Skema Basis Data:**
   * Menambahkan 4 kolom baru bertipe nullable pada model `CalonPenerima` di berkas `models_db.py`: `provinsi`, `kabupaten`, `kecamatan`, dan `desa_kelurahan`.
   * Kolom alamat asli tetap dipertahankan untuk menampung detail lokasi yang lebih spesifik (seperti nomor RT/RW, nomor rumah, atau nama jalan).

3. **Autocomplete UI & Form Calon Penerima:**
   * Memodifikasi formulir tambah/edit calon di `form.html` dengan menyisipkan input pencarian autocomplete berbasis JavaScript (`calon.js`).
   * Ketika admin mengetik nama desa (min. 2 karakter), saran wilayah bertingkat akan muncul. Setelah diklik, sistem akan otomatis mendistribusikan data ke 4 input tersembunyi (*hidden fields*) untuk disimpan saat form di-submit.
   * Pada tabel daftar calon (`list.html`), saya menambahkan kolom **Wilayah** yang menampilkan badge compact bertuliskan nama Desa dan Kecamatan calon penerima dengan tooltip wilayah lengkap.

4. **Visualisasi Grafik Sebaran Desa secara Dinamis:**
   * Memperbarui visualisasi diagram batang sebaran calon di dashboard (`dashboard.py`, `dashboard.html`, dan `dashboard.js`).
   * Menghapus pencarian substring 3 desa yang sebelumnya di-hardcode. Grafik sekarang secara otomatis mengagregasikan data calon per desa menggunakan kueri `group_by` dari database SQLite dan memetakan hasilnya secara dinamis ke Chart.js. Desa dengan jumlah calon sedikit atau tanpa wilayah terinci akan dikelompokkan ke label **"Lainnya"** agar tampilan visualisasi tetap rapi.

5. **Optimalisasi Modul Impor & Ekspor Data (Spreadsheet):**
   * Menambahkan 4 kolom wilayah baru pada template excel impor, file hasil ekspor, dan pilihan kolom checkbox di `data_io.py`.
   * Menjamin toleransi edge case data impor: kolom wilayah bersifat opsional. Jika admin mengimpor data menggunakan file Excel/CSV lama (hanya berisi kolom `alamat`), proses impor tetap berhasil 100% tanpa error, dan menyimpan wilayah sebagai `None` di database dengan alamat lengkap yang tetap utuh.

---

## Hasil Pengujian & Verifikasi

* **Pencarian Autocomplete:** Pengujian pencarian desa sukses memunculkan saran lengkap bertingkat beserta kodenya. Proses pemilihan berhasil mengisi 4 hidden inputs dan memperbarui teks input utama.
* **Pengujian Impor Data:** Berhasil mengimpor berkas Excel kuno tanpa memicu error, membuktikan proteksi penanganan edge case dan kegagalan format bekerja secara penuh.
* **Agregasi Grafik Dinamis:** Grafik di dashboard berhasil membaca dan menggambarkan data desa baru secara dinamis.
* **Unit Testing:** Menulis berkas pengujian otomatis di `scratch/test_features.py` dan seluruh 4 unit test dinyatakan lulus (**OK**).

---

## Output Sesi

- **Data Wilayah Lokal:**  Sukses mengompilasi 89.554 daerah administratif Indonesia.
- **Pencarian Bertingkat:**  Aman dari redundansi nama berkat resolusi `fullname` hierarki.
- **Agregasi Dashboard:**  100% dinamis tanpa hardcode nama desa.
- **Impor & Ekspor Robust:**  Bisa menangani data tanpa kolom wilayah.
