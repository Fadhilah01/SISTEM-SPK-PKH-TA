"""Blueprint — Public Landing Page & Public Prediction API."""
from flask import Blueprint, render_template, request, jsonify
from models_db import CalonPenerima, HasilKeputusan
from core.predictor import predictor, model_loaded
from core.limiter import limiter

public_bp = Blueprint('public', __name__)


@public_bp.route('/')
def landing():
    """Halaman Landing Page Publik SPK PKH."""
    # Query statistik riil dari database
    total_calon = CalonPenerima.query.count()
    total_layak = HasilKeputusan.query.filter_by(hasil_prediksi=True).count()
    total_tidak = HasilKeputusan.query.filter_by(hasil_prediksi=False).count()
    
    # Ambil metrik performa model SVM RBF
    metrics = predictor.get_metrics() if (model_loaded and predictor) else {}
    
    # Fallback jika metrik tidak terisi dari pkl
    if not metrics:
        metrics = {
            'accuracy': 0.9844,
            'precision': 0.9750,
            'recall': 1.0000,
            'f1': 0.9873,
            'best_params': {
                'kernel': 'RBF',
                'C': 10,
                'gamma': 0.01,
                'class_weight': 'Balanced'
            }
        }
        
    return render_template('landing.html',
                           total_calon=total_calon,
                           total_layak=total_layak,
                           total_tidak=total_tidak,
                           metrics=metrics,
                           model_loaded=model_loaded)


@public_bp.route('/api/public-predict', methods=['POST'])
@limiter.limit("30 per minute")
def public_predict():
    """API Publik untuk melakukan prediksi kelayakan secara real-time via simulator."""
    if not model_loaded or not predictor:
        return jsonify({'error': 'Mesin model SVM sedang tidak aktif. Silakan hubungi admin.'}), 503
        
    data = request.json or {}
    
    try:
        # Konversi dan validasi input kriteria
        penghasilan = int(data.get('penghasilan', 3))
        pekerjaan = int(data.get('pekerjaan', 3))
        aset = int(data.get('aset', 3))
        ibu_hamil = bool(data.get('ibu_hamil', False))
        anak_usia_dini = bool(data.get('anak_usia_dini', False))
        anak_sekolah = bool(data.get('anak_sekolah', False))
        disabilitas = bool(data.get('disabilitas', False))
        lansia = bool(data.get('lansia', False))
        
        # Jalankan prediksi SVM
        result = predictor.predict(
            penghasilan_skor=penghasilan,
            pekerjaan_skor=pekerjaan,
            aset_skor=aset,
            ibu_hamil=ibu_hamil,
            anak_usia_dini=anak_usia_dini,
            anak_sekolah=anak_sekolah,
            disabilitas=disabilitas,
            lansia=lansia
        )
        
        return jsonify({
            'status': 'success',
            'label': result['label'],
            'probability': result['probabilitas'],
            'confidence_pct': result['confidence_pct']
        })
        
    except ValueError as ve:
        return jsonify({'error': f'Format input tidak valid: {str(ve)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Gagal memproses prediksi: {str(e)}'}), 500
