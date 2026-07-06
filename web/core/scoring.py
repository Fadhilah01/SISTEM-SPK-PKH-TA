"""
Fungsi-fungsi scoring dan prediksi terpusat.

Tujuan:
  - Menghindari duplikasi logika konversi skor di route handlers.
  - Menyediakan satu titik perubahan jika format input berubah.
"""
from core.constants import PENGHASILAN_MAPPING, PEKERJAAN_MAPPING, ASET_MAPPING, KOMPONEN_SOSIAL


def compute_scores(penghasilan, pekerjaan, aset, **komponen_sosial):
    """
    Convert form inputs to ordinal scores for SVM.

    Parameters
    ----------
    penghasilan : str — kategori Desil (salah satu kunci PENGHASILAN_MAPPING)
    pekerjaan : str   — kategori pekerjaan (salah satu kunci PEKERJAAN_MAPPING)
    aset : str        — kategori kepemilikan aset (salah satu kunci ASET_MAPPING)
    **komponen_sosial : dict[str, bool] — field Boolean komponen keluarga

    Returns
    -------
    dict[str, int] — semua field skor_* siap pakai untuk DB & prediksi
    """
    skor = {
        'skor_penghasilan': PENGHASILAN_MAPPING[penghasilan],
        'skor_pekerjaan': PEKERJAAN_MAPPING[pekerjaan],
        'skor_kepemilikan_aset': ASET_MAPPING[aset],
    }
    for key in KOMPONEN_SOSIAL:
        skor[f'skor_{key}'] = 1 if komponen_sosial.get(key) else 0
    return skor


def predict_single(predictor, calon):
    """
    Helper — prediksi satu calon tanpa mengulang 8 parameter.

    Parameters
    ----------
    predictor : SVMPredictor | None
    calon : CalonPenerima — instance model dengan field skor_*

    Returns
    -------
    dict {'label', 'probabilitas', 'confidence_pct'} | None
    """
    if not predictor:
        return None
    return predictor.predict(
        penghasilan_skor=calon.skor_penghasilan,
        pekerjaan_skor=calon.skor_pekerjaan,
        aset_skor=calon.skor_kepemilikan_aset,
        ibu_hamil=calon.ibu_hamil,
        anak_usia_dini=calon.anak_usia_dini,
        anak_sekolah=calon.anak_sekolah,
        disabilitas=calon.disabilitas,
        lansia=calon.lansia,
    )


def create_hasil_keputusan(calon_id, result, oleh='Sistem'):
    """
    Factory — buat dictionary untuk konstruktor HasilKeputusan.

    Parameters
    ----------
    calon_id : int
    result : dict — output dari predict_single()
    oleh : str — user id / 'Sistem'

    Returns
    -------
    dict — siap di-unpack ke HasilKeputusan(**dict)
    """
    return {
        'id_calon': calon_id,
        'hasil_prediksi': result['label'] == 'Layak',
        'label_prediksi': result['label'],
        'probabilitas': result['probabilitas'],
        'oleh': oleh,
    }
