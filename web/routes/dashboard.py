"""Blueprint — Dashboard utama (ringkasan data & hasil)."""
from flask import Blueprint, render_template
from models_db import CalonPenerima, HasilKeputusan
from core.auth import login_required
from core.predictor import predictor, model_loaded

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    """Dashboard utama — ringkasan data dan hasil keputusan."""
    total_calon = CalonPenerima.query.count()
    total_layak = HasilKeputusan.query.filter_by(hasil_prediksi=True).count()
    total_tidak = HasilKeputusan.query.filter_by(hasil_prediksi=False).count()

    # 10 hasil terbaru
    recent = HasilKeputusan.query.order_by(
        HasilKeputusan.tanggal_prediksi.desc()
    ).limit(10).all()

    # Distribusi calon per desa untuk visualisasi
    count_posona = (
        CalonPenerima.query
        .filter(CalonPenerima.alamat.like('%Posona%'))
        .filter(~CalonPenerima.alamat.like('%Posona Atas%'))
        .count()
    )
    count_posona_atas = CalonPenerima.query.filter(
        CalonPenerima.alamat.like('%Posona Atas%')
    ).count()
    count_palapi = CalonPenerima.query.filter(
        CalonPenerima.alamat.like('%Kasimbar Palapi%')
    ).count()

    desa_stats = {
        'Posona': count_posona,
        'Kasimbar Palapi': count_palapi,
        'Posona Atas': count_posona_atas,
    }

    return render_template('dashboard.html',
                           total_calon=total_calon,
                           total_layak=total_layak,
                           total_tidak=total_tidak,
                           recent=recent,
                           desa_stats=desa_stats,
                           model_loaded=model_loaded)
