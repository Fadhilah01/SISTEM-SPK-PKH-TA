# 📘 Panduan Cepat Setup & Menjalankan Website SPK-PKH SVM (Windows)

Panduan ini dibuat khusus untuk mempermudah setup aplikasi dari kondisi laptop **kosong melompong** (belum terinstall Python atau software pendukung lainnya). Ikuti langkah-langkah di bawah ini secara berurutan.

---

## 📋 Langkah-Langkah Setup

### 1. Download & Install Python (Wajib)
1. Buka browser dan download installer Python versi stabil (disarankan Python 3.11) melalui link langsung berikut:
   * **[Download Python 3.11.9 (Windows 64-bit)](https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe)**
2. Setelah selesai didownload, buka file installer tersebut (`python-3.11.9-amd64.exe`).
3. **⚠️ PENTING (JANGAN TERLEWAT):** Sebelum mengklik tombol install, pastikan centang kotak **"Add python.exe to PATH"** di bagian paling bawah jendela installer.
4. Klik **"Install Now"** (biasanya di bagian paling atas).
5. Tunggu proses instalasi hingga muncul tulisan *Setup was successful*, lalu klik **Close**.

---

### 2. Membuka Command Prompt (CMD) di Folder Proyek
1. Buka **File Explorer** di Windows Anda.
2. Cari dan masuk ke folder proyek hasil clone/ekstrak (folder `SISTEM-SPK-PKH-TA` atau tempat file `requirements.txt` berada).
3. Klik sekali pada **Address Bar** di bagian atas File Explorer (kolom panjang yang menampilkan lokasi folder saat ini, misalnya `D:\JOKI`).
4. Hapus seluruh isi tulisan di Address Bar tersebut, ketik **`cmd`**, lalu tekan **Enter** di keyboard.
5. Jendela hitam **Command Prompt (CMD)** akan terbuka secara otomatis langsung mengarah ke folder proyek Anda.

---

### 3. Membuat & Mengaktifkan Virtual Environment (Venv)
Virtual Environment digunakan agar library Python yang diinstall khusus untuk proyek ini tidak mengganggu program lainnya.
1. Di jendela CMD yang sudah terbuka, ketik perintah berikut lalu tekan **Enter**:
   ```bash
   python -m venv venv
   ```
   *Tunggu sekitar 10-15 detik hingga CMD kembali menampilkan baris perintah baru. Ini menandakan folder `venv` telah berhasil dibuat.*
2. Aktifkan virtual environment dengan mengetik perintah berikut lalu tekan **Enter**:
   ```bash
   venv\Scripts\activate
   ```
   *Jika berhasil, Anda akan melihat tanda `(venv)` muncul di sebelah paling kiri baris perintah CMD Anda, contohnya:*
   ```text
   (venv) D:\JOKI>
   ```

---

### 4. Menginstall Library Pendukung (Dependencies)
1. Pastikan tanda `(venv)` masih aktif di sebelah kiri baris perintah CMD.
2. Ketik perintah berikut untuk mendownload dan menginstall seluruh kebutuhan library (seperti Flask, Scikit-Learn, Pandas, dll) secara otomatis:
   ```bash
   pip install -r requirements.txt
   ```
   *Pastikan laptop terhubung ke internet. Proses download & instalasi membutuhkan waktu sekitar 1-3 menit tergantung kecepatan internet Anda.*

---

### 5. Menjalankan Website SPK-PKH
1. Pindah masuk ke dalam folder `web` dengan mengetik perintah berikut lalu tekan **Enter**:
   ```bash
   cd web
   ```
2. Jalankan server aplikasi Flask dengan perintah berikut lalu tekan **Enter**:
   ```bash
   python app.py
   ```
3. Jika berhasil dijalankan, server akan memproses database lokal dan memunculkan tulisan seperti ini:
   ```text
   [OK] Database siap.
   * Serving Flask app 'app'
   * Debug mode: off
   * Running on http://127.0.0.1:5000
   ```
   *⚠️ **Catatan Penting:** Jangan menutup jendela hitam CMD ini selama Anda menggunakan website. Jika CMD ditutup, website akan mati.*

---

### 6. Membuka Website di Browser
1. Buka browser di laptop Anda (Google Chrome, Microsoft Edge, Mozilla Firefox, dll).
2. Salin atau ketik alamat berikut di Address Bar browser Anda, lalu tekan **Enter**:
   **[http://127.0.0.1:5000](http://127.0.0.1:5000)** atau **[http://localhost:5000](http://localhost:5000)**
3. Anda akan langsung diarahkan ke halaman login website SPK-PKH.

---

## 🔑 Informasi Akun Login Bawaan

Aplikasi ini menggunakan **Role-Based Access Control (RBAC)** dengan dua level akun bawaan yang bisa langsung digunakan:

1. **Akun Superadmin (Akses Penuh / Dinas Sosial):**
   * **Username:** `admin`
   * **Password:** `admin123`
2. **Akun Admin Biasa (Pendamping PKH Lapangan):**
   * **Username:** `user1`
   * **Password:** `user1123`

> 🔒 **Info Keamanan:** Pada saat login pertama kali menggunakan akun default di atas, sistem akan **mewajibkan** Anda untuk mengganti password bawaan demi keamanan database. Silakan ganti dengan password baru Anda (minimal 8 karakter kombinasi huruf dan angka).

---

## 🛠️ Pemecahan Masalah (Troubleshooting) jika Terjadi Error

* **Error: "python is not recognized..." atau perintah python tidak dikenal**
  * *Penyebab:* Lupa mencentang "Add python.exe to PATH" saat menginstall Python di **Langkah 1**.
  * *Solusi:* Buka kembali file installer Python (`python-3.11.9-amd64.exe`), pilih opsi **Modify** atau lakukan **Uninstall** terlebih dahulu lalu jalankan ulang install baru, dan pastikan mencentang kotak **Add python.exe to PATH** sebelum klik install.

* **Error: Proses `pip install` berhenti atau banyak tulisan merah**
  * *Penyebab:* Koneksi internet tidak stabil atau terputus di tengah jalan.
  * *Solusi:* Pastikan laptop terhubung dengan koneksi internet yang lancar, lalu ketik dan jalankan kembali perintah `pip install -r requirements.txt`.

* **Bagaimana cara kerja database program ini di laptop saya?**
  * Program ini didesain otomatis mendeteksi konfigurasi. Jika dijalankan di laptop secara offline, program akan langsung membuat database lokal berbasis **SQLite** bernama `spk_pkh.db` di dalam folder `web/`.
  * **Cara Reset Database (jika ingin menghapus semua data uji coba agar bersih):** Matikan program (tekan `Ctrl + C` di CMD), cari dan hapus file `spk_pkh.db` yang ada di dalam folder `web`, lalu jalankan kembali perintah `python app.py`. Database baru yang kosong dengan akun bawaan akan otomatis terbentuk kembali.
