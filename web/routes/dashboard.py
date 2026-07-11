"""Blueprint — Dashboard utama (ringkasan data & hasil)."""
from flask import Blueprint, render_template
from models_db import CalonPenerima, HasilKeputusan
from core.auth import login_required
from core.predictor import predictor, model_loaded

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
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

    # Distribusi calon per desa untuk visualisasi (Dinamis dari database)
    from sqlalchemy import func
    from models_db import db
    
    stats_query = (
        db.session.query(
            func.coalesce(CalonPenerima.desa_kelurahan, CalonPenerima.alamat).label('desa_name'),
            func.count(CalonPenerima.id).label('total')
        )
        .group_by('desa_name')
        .order_by(func.count(CalonPenerima.id).desc())
        .all()
    )

    desa_stats = {}
    for name, count in stats_query:
        clean_name = str(name or 'Lainnya').strip().title()
        # Hapus prefix "Desa " untuk mempercantik label grafik
        if clean_name.upper().startswith("DESA "):
            clean_name = clean_name[5:]
        # Gabungkan jika ada yang duplikat setelah dibersihkan
        desa_stats[clean_name] = desa_stats.get(clean_name, 0) + count

    return render_template('dashboard.html',
                           total_calon=total_calon,
                           total_layak=total_layak,
                           total_tidak=total_tidak,
                           recent=recent,
                           desa_stats=desa_stats,
                           model_loaded=model_loaded)

