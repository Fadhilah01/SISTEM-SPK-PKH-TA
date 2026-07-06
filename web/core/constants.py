"""
Mapping nilai ordinal untuk kriteria SPK PKH.
Skema sesuai dokumen resmi dari Tim PKH (Kemensos).

Setiap kriteria dipetakan ke skor 1-5, di mana:
  5 = paling berhak (kondisi paling rentan)
  1 = paling tidak berhak (kondisi paling mampu)
"""

# ─── Penghasilan per Bulan (Desil Kesejahteraan) ───
PENGHASILAN_MAPPING = {
    'Desil 1 (< Rp.500.000)': 5,
    'Desil 2 (Rp.600.000 - Rp.700.000)': 4,
    'Desil 3 (Rp.800.000 - Rp.900.000)': 3,
    'Desil 4 (Rp.1.000.000 - Rp.1.200.000)': 2,
    'Desil 5 (Rp.1.300.000 - Rp.1.500.000)': 1,
}

# ─── Jenis Pekerjaan Kepala Keluarga ───
PEKERJAAN_MAPPING = {
    'Tidak Bekerja': 5,
    'Pekerja Bebas': 4,
    'Petani/Nelayan': 3,
    'Wiraswasta': 2,
    'PNS/Pegawai Tetap': 1,
}

# ─── Kepemilikan Aset ───
ASET_MAPPING = {
    'Tidak Memiliki Aset': 5,
    'Memiliki Motor (harga jual rendah)': 4,
    'Memiliki Motor (harga jual tinggi)': 3,
    'Memiliki Mobil atau Tanah/Kebun': 2,
    'Memiliki Mobil dan Tanah/Kebun': 1,
}

# ─── Label Singkat untuk UI Tabel ───
# Mapping dari teks panjang (key) ke label compact untuk badge di tabel data calon.
LABEL_SINGKAT = {
    # Penghasilan
    'Desil 1 (< Rp.500.000)': 'Desil 1',
    'Desil 2 (Rp.600.000 - Rp.700.000)': 'Desil 2',
    'Desil 3 (Rp.800.000 - Rp.900.000)': 'Desil 3',
    'Desil 4 (Rp.1.000.000 - Rp.1.200.000)': 'Desil 4',
    'Desil 5 (Rp.1.300.000 - Rp.1.500.000)': 'Desil 5',
    # Pekerjaan
    'Tidak Bekerja': 'Tdk Bekerja',
    'Pekerja Bebas': 'Pekerja Bebas',
    'Petani/Nelayan': 'Petani/Nelayan',
    'Wiraswasta': 'Wiraswasta',
    'PNS/Pegawai Tetap': 'PNS',
    # Aset
    'Tidak Memiliki Aset': 'Tdk Punya',
    'Memiliki Motor (harga jual rendah)': 'Motor Rendah',
    'Memiliki Motor (harga jual tinggi)': 'Motor Tinggi',
    'Memiliki Mobil atau Tanah/Kebun': 'Mobil/Tanah',
    'Memiliki Mobil dan Tanah/Kebun': 'Mobil+Tanah',
}

# ─── Komponen Sosial (Boolean) ───
# Daftar field boolean untuk komponen keluarga.
# Digunakan oleh scoring.py untuk iterasi otomatis.
KOMPONEN_SOSIAL = [
    'ibu_hamil',
    'anak_usia_dini',
    'anak_sekolah',
    'disabilitas',
    'lansia',
]
