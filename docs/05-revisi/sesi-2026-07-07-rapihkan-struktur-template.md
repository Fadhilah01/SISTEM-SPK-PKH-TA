# Sesi 11 — Perapihan Struktur Folder Template Web (7 Juli 2026)

## Yang Dikerjakan

Pada sesi ini saya merapihkan struktur folder `templates/` pada aplikasi web Sipekaha agar lebih konsisten dan mudah dikelola. Sebelumnya, template yang berkaitan dengan modul admin sudah memiliki folder sendiri (`admin/`), namun template untuk modul lainnya masih tersimpan langsung di root folder `templates/` sehingga terlihat tidak rapi dan menyulitkan pencarian file.

### Perubahan Struktur Folder

**Sebelum:**
```
templates/
├── calon.html              ← campur aduk di root
├── calon_form.html
├── calon_import.html
├── calon_export.html
├── login.html
├── change_password.html
├── _flash.html             ← partial, tanpa folder khusus
├── admin/                  ← satu-satunya yang sudah rapi
└── errors/
```

**Sesudah:**
```
templates/
├── partials/
│   └── _flash.html
├── admin/
│   ├── user_detail.html
│   ├── user_form.html
│   └── users.html
├── auth/
│   ├── login.html
│   └── change_password.html
├── calon/
│   ├── list.html           ← ex calon.html
│   ├── form.html           ← ex calon_form.html
│   ├── import.html         ← ex calon_import.html
│   └── export.html         ← ex calon_export.html
├── errors/
│   ├── 403.html
│   ├── 404.html
│   └── 500.html
├── base.html
├── dashboard.html
└── about.html
```

### Dasar Pemikiran

1. **Konsistensi** — Semua modul sekarang punya folder sendiri, sama seperti modul Admin yang sudah rapi sebelumnya.
2. **Skalabilitas** — Jika di masa depan ada modul baru (misalnya laporan, pengaturan desa), tinggal tambah folder baru tanpa mengotori root.
3. **Partial/Fragment** — File `_flash.html` yang bersifat partial dipindahkan ke folder `partials/` agar jelas bahwa file ini bukan halaman utuh, melainkan komponen yang di-include ke template lain.

### Update Kode yang Dilakukan

1. **routes/auth.py** — Path `render_template` disesuaikan:
   - `login.html` → `auth/login.html`
   - `change_password.html` → `auth/change_password.html`

2. **routes/calon.py** — Path `render_template` disesuaikan:
   - `calon.html` → `calon/list.html`
   - `calon_form.html` → `calon/form.html`
   - `calon_import.html` → `calon/import.html`
   - `calon_export.html` → `calon/export.html`

3. **templates/base.html** — Path `include` disesuaikan:
   - `'_flash.html'` → `'partials/_flash.html'`

4. **templates/partials/_flash.html** — Komentar internal diupdate sesuai path baru

### Verifikasi

Setelah perubahan, saya menjalankan aplikasi dan menguji semua route yang menggunakan template yang dipindahkan. Hasilnya:
- ✅ Dashboard: 200 OK
- ✅ Data Calon (list): 200 OK
- ✅ Tambah Calon (form): 200 OK
- ✅ Export Data: 200 OK
- ✅ Halaman About: 200 OK
- ✅ Login: 200 OK

Tidak ada error `TemplateNotFound` atau `UndefinedError`.

## Keputusan yang Diambil

- **Nama file**: Saya mempertahankan nama file asli (hanya memindahkan ke folder). Tidak mengganti nama file ke bentuk plural (misalnya `calon_list.html`) agar URL helper yang sudah ada tetap sederhana.
- **dashboard.html** dan **about.html** tetap di root karena hanya satu file per modul — tidak perlu folder khusus untuk satu file.

## Kendala & Solusi

Tidak ada kendala berarti. Perubahan hanya bersifat mekanis (mindah file + update path).

## Perubahan dari Rencana Awal

Tidak ada — ini adalah perbaikan organisasi kode murni.

## Output Sesi

1. Struktur folder `templates/` lebih rapi dan konsisten
2. Semua route berfungsi normal tanpa error template
