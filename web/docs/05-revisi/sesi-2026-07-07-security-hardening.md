# Sesi 12: Security Hardening — Pencegahan Cyber Crime pada Sistem SPK PKH
**Tanggal:** 7 Juli 2026
**Fokus:** Audit keamanan menyeluruh dan implementasi 10 lapisan proteksi

---

## Yang Dikerjakan

Setelah menyelesaikan seluruh fitur fungsional sistem, saya melakukan audit keamanan menyeluruh terhadap aplikasi web SPK PKH untuk memastikan kesiapan sistem sebelum digunakan oleh Dinas Sosial. Audit ini bertujuan untuk melindungi data calon penerima PKH (data sensitif warga) dari berbagai serangan siber yang umum terjadi.

### Temuan Audit
Ditemukan **10 kerentanan keamanan** yang terbagi dalam 3 tingkat keparahan:

| Level | Jumlah | Contoh |
|-------|--------|--------|
| **HIGH** | 3 | Brute force login, debug mode aktif, password default |
| **MEDIUM** | 5 | Tidak ada CSP/XSS header, SECRET_KEY hardcoded, session tanpa batas waktu |
| **LOW** | 2 | Validasi file upload hanya ekstensi, tidak ada validasi panjang input |

### 10 Perbaikan yang Dilakukan

1. **Rate Limiting Login (HIGH)**
   - Menggunakan Flask-Limiter, membatasi percobaan login maksimal 5 kali per menit per IP
   - Pelacakan gagal login via session — setelah 10 kali gagal, akun dikunci sementara
   - Mencegah serangan brute force

2. **Nonaktifkan Debug Mode (HIGH)**
   - Debug mode dimatikan agar error stack trace tidak bocor ke pengguna
   - Ditambahkan logging ke file untuk troubleshooting

3. **Force Password Change (HIGH)**
   - Akun default admin baru otomatis diminta mengganti password saat login pertama
   - Kolom `must_change_password` di database untuk melacak status
   - Redirect otomatis ke halaman ganti password jika belum diubah

4. **Perbaikan XSS (MEDIUM)**
   - Sanitasi input HTML pada form nama dan alamat (hapus tag berbahaya)
   - Escape output user pada JavaScript flash messages
   - Validasi tipe alert Bootstrap yang diizinkan

5. **Security Headers (MEDIUM)**
   - Content-Security-Policy: membatasi sumber daya yang bisa di-load
   - X-Frame-Options: DENY (cegah clickjacking)
   - X-Content-Type-Options: nosniff
   - Strict-Transport-Security, Referrer-Policy, Permissions-Policy
   - Cross-Origin-Opener-Policy: same-origin

6. **Perbaikan SECRET_KEY (MEDIUM)**
   - Tidak lagi menggunakan string hardcoded
   - Prioritaskan environment variable, fallback ke key acak yang digenerate tiap restart

7. **Session Security (MEDIUM)**
   - Session cookie: HTTPOnly, SameSite=Lax
   - Session expire otomatis setelah 4 jam tidak aktif
   - Prevent session hijacking via JavaScript

8. **Password Policy (MEDIUM)**
   - Minimum password dinaikkan dari 6 menjadi **8 karakter**
   - Wajib mengandung minimal 1 huruf dan 1 angka
   - Password baru tidak boleh sama dengan yang lama
   - Berlaku untuk ganti password dan pembuatan akun admin baru

9. **Validasi File Upload (LOW)**
   - Validasi ekstensi file (hanya .xlsx, .xls, .csv)
   - Validasi MIME type dari header Content-Type
   - Validasi magic bytes untuk file Excel (.xlsx harus PKZIP, .xls harus OLE2)
   - Mencegah upload file berbahaya yang di-rename

10. **Validasi Panjang Input (LOW)**
    - Nama: maksimal 100 karakter
    - Alamat: maksimal 255 karakter
    - Sanitasi HTML untuk cegah XSS pada input teks

---

## Keputusan yang Diambil

1. **Flask-Limiter 4.x dengan storage memory** — untuk aplikasi single-instance ini, in-memory storage cukup karena data rate limit akan di-reset saat server restart. Jika nanti deploy dengan multiple workers, perlu Redis.

2. **Security Headers via middleware after_request** — tidak menggunakan Flask-Talisman agar tetap ringan dan compatible.

3. **Sanitasi HTML via regex (bukan library)** — untuk scope aplikasi ini (hanya 2 field teks: nama dan alamat), regex cukup memadai. Tidak perlu beautifulsoup atau bleach.

4. **force_password_change terintegrasi di login_required** — bukan decorator terpisah, agar konsisten dan tidak ada route yang terlewat.

---

## Kendala & Solusi

**Kendala:** Flask-Limiter tidak compatible dengan Blueprint secara default pada beberapa versi.
**Solusi:** Membuat shared `limiter` instance di `core/limiter.py` dan menginisialisasinya di `app.py` sebelum register blueprint.

**Kendala:** Loop redirect pada change_password karena decorator login_required mendeteksi must_change_password dan langsung redirect kembali ke change_password.
**Solusi:** Menambahkan pengecualian endpoint `auth.change_password` di decorator `login_required` — jika user sudah di halaman change_password, tidak dicek lagi.

---

## Perubahan dari Rencana Awal

Tidak ada. Semua 10 task sesuai rencana.

---

## Output Sesi

Semua 10 perbaikan keamanan telah diimplementasikan:
- ✅ Rate Limiting pada endpoint login
- ✅ Debug mode dinonaktifkan, logging diaktifkan
- ✅ Force password change untuk akun baru/default
- ✅ XSS prevention pada input teks dan JavaScript
- ✅ Security headers untuk proteksi klikjack, XSS, dll
- ✅ Secret key tidak lagi hardcoded
- ✅ Session security (HTTPOnly, SameSite, timeout 4 jam)
- ✅ Password policy ditingkatkan (8+ karakter, huruf+angka)
- ✅ File upload validation (ekstensi, MIME, magic bytes)
- ✅ Input length validation + sanitasi HTML

## File-file yang Dimodifikasi
| File | Perubahan |
|------|-----------|
| `app.py` | Debug=False, logging, init limiter, init security headers |
| `config.py` | SECRET_KEY dinamis, session config, rate limit config |
| `requirements.txt` | Tambah flask-limiter |
| `models_db.py` | Tambah field `must_change_password` |
| `core/auth.py` | Tambah `validate_password_strength`, `force_password_check` di login_required |
| `core/security.py` | BARU — middleware security headers + file upload validation + sanitasi |
| `core/limiter.py` | BARU — shared Limiter instance |
| `routes/auth.py` | Rate limit, force password change, password policy |
| `routes/admin.py` | Password policy di tambah user |
| `routes/calon.py` | File upload MIME validation, input length + sanitasi |
| `static/js/import.js` | XSS prevention via escaped HTML |
| `templates/auth/change_password.html` | Force change notice + password policy info |
