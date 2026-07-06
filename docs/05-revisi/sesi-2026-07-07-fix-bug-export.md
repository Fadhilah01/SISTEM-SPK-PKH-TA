# Sesi 10 — Debug & Fix Bug Export Data (7 Juli 2026)

## Yang Dikerjakan

Debug dan perbaikan 3 bug kritis pada fitur export data calon PKH yang menyebabkan:
- Export tidak pernah berhasil (stuck loading terus)
- Tombol download tetap dalam keadaan "Memproses Export..." setelah halaman di-refresh
- Tombol "Batal" langsung redirect ke halaman data, bukan membatalkan loading

## Root Cause

### Bug 1: Tombol Submit di-Disable di Event Click → Browser Batalkan Submission

Di `export.js`, event handler `click` pada tombol **btnExport** menjalankan kode:

```javascript
btn.addEventListener('click', function (e) {
    // ...validasi...
    this.disabled = true;  // ⚠️ INI PENYEBAB BUG
    this.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Memproses Export...';
});
```

**Mengapa ini masalah:** Di browser modern (Chromium), ketika tombol `<button type="submit">` di-disable di dalam listener event `click`, browser **membatalkan** proses form submission. Form tidak akan pernah mengirim request POST ke server.

Akibatnya:
1. Route `/calon/export` endpoint POST tidak pernah dipanggil
2. Tidak ada file yang diproses atau di-download
3. Tombol tetap dalam keadaan disabled dengan teks "Memproses Export..."
4. Log hanya menunjukkan request GET sebelumnya, tanpa ada POST

### Bug 2: State Tidak Pernah di-Reset

Karena form tidak pernah ter-submit, JavaScript tidak pernah mengalami page reload atau response handling. Tombol submit tetap disabled selamanya sampai user melakukan refresh manual.

### Bug 3: Tombol "Batal" adalah `<a>` Bukan `<button>`

Di `calon_export.html`, tombol Batal adalah:

```html
<a href="{{ url_for('calon.daftar_calon') }}" class="btn btn-secondary px-4">Batal</a>
```

Ini selalu redirect ke halaman data calon, tidak peduli apakah sedang ada proses loading export. Tidak ada cara untuk "membatalkan" overlay loading — satu-satunya cara adalah refresh halaman.

## Solusi

### Untuk Bug 1 & 2: Loading Overlay + Event Submit

Mekanisme diubah total:

| Sebelum | Sesudah |
|---------|---------|
| Event `click` pada tombol submit | Event `submit` pada `<form>` |
| Tombol di-disabled | Tombol **tidak di-disabled** (tetap aktif, browser bisa submit form) |
| Spinner di dalam tombol | **Overlay** fixed full-screen dengan spinner |
| Tidak ada feedback visual setelah submit | Overlay "Sedang memproses export..." muncul saat file di-generate |

**Kenapa overlay lebih baik:**
- Browser bisa tetap melakukan form submission karena tombol tidak pernah di-disable
- User mendapat feedback visual bahwa proses sedang berjalan
- File download akan trigger browser download dialog, overlay bisa ditutup setelah download selesai
- Fallback: overlay auto-hide setelah 15 detik

### Untuk Bug 3: handleCancel() + Button

Tombol Batal diubah dari `<a>` link menjadi `<button type="button">` dengan fungsi JavaScript:

- Jika overlay loading sedang tampil → **tutup overlay saja** (batal melihat status, tidak batal download)
- Jika tidak ada overlay → **redirect ke halaman data calon** (perilaku default)

## Perubahan dari Rencana Awal

Tidak ada — ini adalah perbaikan bug dari implementasi sesi sebelumnya.

## Output Sesi

1. **File diubah:** `static/js/export.js` — Perbaikan mekanisme submit, ganti disable button dengan loading overlay, tambah fungsi handleCancel()
2. **File diubah:** `templates/calon_export.html` — Tombol Batal dari `<a>` jadi `<button>`

### Ringkasan Bug

| # | Bug | Status | Fix |
|---|-----|--------|-----|
| 1 | Disable tombol submit di event click mencegah form submission | ✅ Fixed | Ganti ke loading overlay |
| 2 | Tombol tetap "Memproses Export..." selamanya | ✅ Fixed | Overlay auto-hide 15 detik |
| 3 | Tombol Batal redirect langsung bukan batalkan loading | ✅ Fixed | handleCancel() cek overlay dulu |
