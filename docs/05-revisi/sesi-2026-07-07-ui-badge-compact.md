# Sesi 11 — UI Badge Compact pada Tabel Data Calon (7 Juli 2026)

## Yang Dikerjakan

Redesain tampilan 3 kolom (Penghasilan, Pekerjaan, Kepemilikan Aset) di tabel data calon dari teks raw panjang menjadi badge compact yang lebih ringkas dan estetik.

### Sebelum:
- Kolom Penghasilan: `"Desil 1 (< Rp.500.000)"` — teks panjang memenuhi sel tabel
- Kolom Pekerjaan: `"Tidak Bekerja"`, `"PNS/Pegawai Tetap"` — tidak konsisten panjangnya
- Kolom Aset: `"Memiliki Mobil atau Tanah/Kebun"` — terlalu panjang, bikin tabel overflow

### Sesudah:
- Setiap nilai ditampilkan sebagai badge compact (label 2-3 kata) dengan icon Bootstrap
- Warna badge bervariasi berdasarkan skor (severity):
  - **Skor 5** (paling rentan): Background hitam, teks putih — paling kontras
  - **Skor 4** (rentan): Background abu gelap, teks putih
  - **Skor 3** (sedang): Background surface, border abu
  - **Skor 2** (mampu): Background surface hover, teks muted
  - **Skor 1** (paling mampu): Transparan, border tipis
- Tooltip (`title` attribute) tetap menampilkan teks lengkap saat hover

## Keputusan yang Diambil

| Keputusan | Alasan |
|-----------|--------|
| Mapping label singkat di `constants.py` (bukan filter Jinja2) | Label bisa dipakai ulang oleh halaman lain (export, detail) |
| Severity coloring berdasarkan skor (1-5) | User langsung paham tingkat kerentanan dari warna |
| Warna monokrom sesuai tema CSS | Tidak perlu palet warna baru, konsisten dengan desain existing |
| `title` attribute untuk teks lengkap | Informasi detail tetap tersedia tanpa mengorbankan estetika |

## Output Sesi

1. **File diubah:** `core/constants.py` — Tambah dictionary `LABEL_SINGKAT` (15 mapping)
2. **File diubah:** `static/css/style.css` — Tambah 6 class `.badge-cat*` (base + 5 severity)
3. **File diubah:** `routes/calon.py` — Pass `penghasilan_skor`, `pekerjaan_skor`, `aset_skor`, `label_singkat` ke template
4. **File diubah:** `templates/calon/list.html` — Ganti 3 `<td>` jadi badge compact, ganti header "Aset" jadi "Kep. Aset"
