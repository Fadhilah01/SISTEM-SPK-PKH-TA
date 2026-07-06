# Log Harian 08: Implementasi Ganti Password dan Multi-Admin Role-Based Access Control (RBAC)
**Tanggal:** 6 Juli 2026
**Durasi:** ~4 jam

---

## Kegiatan yang Dilakukan

Untuk mematangkan manajemen administrasi sistem serta memperkuat aspek keamanan akses pengguna, saya mengimplementasikan dua fitur utama terkait pengelolaan otorisasi:

1. **Fitur Mandiri Ganti Password Admin:**
   * Membuat halaman khusus `/change-password` di rute autentikasi (`routes/auth.py`).
   * Menambahkan form input untuk menginput Password Lama, Password Baru, dan Konfirmasi Password Baru.
   * Melakukan validasi kesesuaian password lama melalui verifikasi hash (`check_password_hash`) dan mencocokkan konfirmasi password baru di sisi server sebelum memperbarui hash kata sandi pada basis data SQLite.
   * Fitur ini dilindungi oleh dekorator `@login_required` dan proteksi CSRF `@csrf_required`.

2. **Sistem Multi-Admin dengan Otorisasi Hak Akses (Role-Based Access Control - RBAC):**
   * Menambahkan kolom `role` pada skema tabel `users` di berkas `models_db.py` untuk mengidentifikasi tingkat wewenang akun (`superadmin` dan `admin`).
   * Membangun decorator otorisasi `@superadmin_required` di modul `core/auth.py` guna membatasi akses pada rute-rute sensitif.
   * Memecah fungsionalitas manajemen pengguna admin ke Blueprint khusus (`routes/admin.py`) dengan *URL Prefix* `/admin`. Rute ini sepenuhnya terisolasi dan hanya dapat diakses oleh administrator bertipe `superadmin`.
   * **Fitur CRUD Admin (Khusus Superadmin):**
     * **Melihat Daftar Admin (`/admin/users`):** Menampilkan tabel yang mencantumkan nama lengkap, username, role, dan tanggal terdaftar.
     * **Menambah Admin Baru (`/admin/users/tambah`):** Form pendaftaran akun admin baru lengkap dengan pilihan dropdown hak akses (Superadmin/Admin biasa).
     * **Menghapus Admin (`/admin/users/<id>/hapus`):** Tombol aksi POST untuk menghapus akses admin. Dilengkapi dengan logika validasi khusus agar Superadmin tidak dapat menghapus akunnya sendiri secara tidak sengaja demi mencegah penguncian sistem (*lock-out*).

3. **Penyesuaian Antarmuka Sidebar Dinamis:**
   * Di dalam file template utama `base.html`, menu navigasi sidebar akan mendeteksi peran akun yang sedang aktif. 
   * Menu "Manajemen Admin" hanya akan dirender dan ditampilkan secara visual apabila `current_user.role == 'superadmin'`.
   * Menambahkan tombol pintasan "Ganti Password" di bagian footer sidebar bagi semua pengguna aktif untuk memudahkan penyesuaian kredensial secara berkala.

4. **Database Migration & Seeding:**
   * Menghapus secara fisik database `spk_pkh.db` yang lama untuk menerapkan struktur kolom `role` yang baru.
   * Memperbarui fungsi inisialisasi `init_db()` agar secara otomatis menghasilkan dua tipe akun bawaan dengan enkripsi hash kata sandi:
     * Akun **Superadmin**: username `admin` (password: `admin123`, role: `superadmin`).
     * Akun **Admin Pendamping**: username `user1` (password: `user1123`, role: `admin`).

---

## Hasil Pengujian & Verifikasi

* **Ganti Password:** Akun `user1` sukses melakukan penggantian kata sandi dari `user1123` menjadi `user1234`. Login kembali menggunakan kredensial lama ditolak secara aman, sementara kredensial baru diterima.
* **Uji Coba RBAC:** Akun `user1` (Admin) tidak dapat melihat opsi "Manajemen Admin" di sidebar. Tembakan url langsung ke `/admin/users` dialihkan secara paksa ke beranda dengan pesan peringatan bahwasanya akses ditolak.
* **Manajemen CRUD Admin:** Akun `admin` (Superadmin) sukses mengakses `/admin/users`, mendaftarkan admin baru, dan menghapus admin pendukung tambahan. Logika pencegahan hapus diri sendiri bekerja normal dengan menampilkan status "Aktif (Anda)" tanpa tombol aksi hapus.

---

## Output Sesi

- **Skema RBAC:** ✅ Sukses membagi peran pengguna menjadi `superadmin` dan `admin`.
- **Ganti Password:** ✅ Berhasil diperbarui dan terproteksi enkripsi hash PBKDF2.
- **Form CRUD Admin:** ✅ Tabel manajemen admin dinamis dan aman dari kerentanan CSRF.
