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


@dashboard_bp.route('/api/analytics')
@login_required
def get_analytics_data():
    """Endpoint API untuk mengambil data analitik visualisasi secara dinamis."""
    from flask import request, jsonify
    from sqlalchemy import func
    from models_db import db, CalonPenerima, HasilKeputusan
    from datetime import datetime

    # 1. Ambil parameter filter
    prov = request.args.get('provinsi', '').strip()
    kab = request.args.get('kabupaten', '').strip()
    kec = request.args.get('kecamatan', '').strip()
    desa = request.args.get('desa_kelurahan', '').strip()

    date_from_str = request.args.get('date_from', '').strip()
    date_to_str = request.args.get('date_to', '').strip()

    chart_type = request.args.get('type', 'wilayah').strip()  # wilayah, tren, komparasi

    # 2. Query dasar (join dengan HasilKeputusan untuk ambil hasil kelayakan)
    query = db.session.query(CalonPenerima).outerjoin(HasilKeputusan)

    # Terapkan filter wilayah dengan toleransi pencocokan prefix KABUPATEN / KOTA secara fleksibel
    if prov:
        clean_prov = prov.replace("PROVINSI ", "").strip().upper()
        query = query.filter(
            (func.upper(CalonPenerima.provinsi) == prov.upper()) |
            (func.upper(CalonPenerima.provinsi) == clean_prov) |
            (func.upper(CalonPenerima.provinsi).like(f"%{clean_prov}%"))
        )
    if kab:
        clean_kab = kab.replace("KABUPATEN ", "").replace("KOTA ", "").strip().upper()
        query = query.filter(
            (func.upper(CalonPenerima.kabupaten) == kab.upper()) |
            (func.upper(CalonPenerima.kabupaten) == clean_kab) |
            (func.upper(CalonPenerima.kabupaten).like(f"%{clean_kab}%"))
        )
    if kec:
        clean_kec = kec.replace("KECAMATAN ", "").strip().upper()
        query = query.filter(
            (func.upper(CalonPenerima.kecamatan) == kec.upper()) |
            (func.upper(CalonPenerima.kecamatan) == clean_kec) |
            (func.upper(CalonPenerima.kecamatan).like(f"%{clean_kec}%"))
        )
    if desa:
        clean_desa = desa.replace("DESA ", "").replace("KELURAHAN ", "").strip().upper()
        query = query.filter(
            (func.upper(CalonPenerima.desa_kelurahan) == desa.upper()) |
            (func.upper(CalonPenerima.desa_kelurahan) == clean_desa) |
            (func.upper(CalonPenerima.desa_kelurahan).like(f"%{clean_desa}%"))
        )

    # Terapkan filter tanggal global jika ada
    if date_from_str:
        try:
            dt_from = datetime.strptime(date_from_str, '%Y-%m-%d')
            query = query.filter(CalonPenerima.created_at >= dt_from)
        except ValueError:
            pass
    if date_to_str:
        try:
            dt_to = datetime.strptime(date_to_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query = query.filter(CalonPenerima.created_at <= dt_to)
        except ValueError:
            pass

    data_list = query.all()

    # 3. Proses berdasarkan tipe visualisasi yang diminta
    if chart_type == 'wilayah':
        # Drill-down wilayah bertingkat
        group_key = 'provinsi'
        if prov:
            group_key = 'kabupaten'
        if kab:
            group_key = 'kecamatan'
        if kec:
            group_key = 'desa_kelurahan'

        counts = {}
        for c in data_list:
            val = getattr(c, group_key) or 'Tidak Terinci'
            if group_key == 'kabupaten':
                if val.upper().startswith("KABUPATEN "):
                    val = val[10:]
                elif val.upper().startswith("KOTA "):
                    val = val[5:]
            counts[val] = counts.get(val, 0) + 1

        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        
        labels = []
        values = []
        other_sum = 0
        for i, (k, v) in enumerate(sorted_counts):
            if i < 7:  # Tampilkan 7 teratas, sisanya gabungkan ke 'Lainnya'
                labels.append(k.title())
                values.append(v)
            else:
                other_sum += v
        if other_sum > 0:
            labels.append("Lainnya")
            values.append(other_sum)

        return jsonify({
            'labels': labels,
            'values': values,
            'title': f'Sebaran Calon Berdasarkan {group_key.replace("_", " ").title()}'
        })

    elif chart_type == 'tren':
        scale = request.args.get('scale', 'month').strip()  # week, month, quarter, year

        tren_data = {}
        for c in data_list:
            if not c.created_at:
                continue
            dt = c.created_at

            if scale == 'year':
                key = dt.strftime('%Y')
            elif scale == 'quarter':
                q_num = (dt.month - 1) // 3 + 1
                key = f"Q{q_num} {dt.year}"
            elif scale == 'week':
                key = dt.strftime('%Y-W%W')
            else:  # month
                key = dt.strftime('%b %Y')

            tren_data[key] = tren_data.get(key, 0) + 1

        # Fungsi pengurutan kunci tren waktu agar kronologis
        def get_sort_key(k):
            if k.startswith("Q"):
                parts = k.split()
                if len(parts) == 2:
                    return int(parts[1]) * 10 + int(parts[0][1])
            try:
                return datetime.strptime(k, '%b %Y')
            except ValueError:
                pass
            if '-W' in k:
                parts = k.split('-W')
                if len(parts) == 2:
                    return int(parts[0]) * 100 + int(parts[1])
            return k

        sorted_keys = sorted(tren_data.keys(), key=get_sort_key)
        labels = sorted_keys
        values = [tren_data[k] for k in sorted_keys]

        return jsonify({
            'labels': labels,
            'values': values,
            'title': f'Tren Jumlah Registrasi Calon ({scale.title()})'
        })

    elif chart_type == 'komparasi':
        compare_mode = request.args.get('compare', 'period').strip()  # period, criteria

        if compare_mode == 'period':
            # Bandingkan dua rentang waktu
            pa_start_str = request.args.get('period_a_start', '').strip()
            pa_end_str = request.args.get('period_a_end', '').strip()
            pb_start_str = request.args.get('period_b_start', '').strip()
            pb_end_str = request.args.get('period_b_end', '').strip()

            pa_start = datetime.strptime(pa_start_str, '%Y-%m-%d') if pa_start_str else None
            pa_end = datetime.strptime(pa_end_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59) if pa_end_str else None
            pb_start = datetime.strptime(pb_start_str, '%Y-%m-%d') if pb_start_str else None
            pb_end = datetime.strptime(pb_end_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59) if pb_end_str else None

            stats_a = {'Layak': 0, 'Tidak Layak': 0}
            stats_b = {'Layak': 0, 'Tidak Layak': 0}

            for c in data_list:
                if not c.created_at:
                    continue
                is_layak = False
                if c.hasil and c.hasil.hasil_prediksi:
                    is_layak = True

                label = 'Layak' if is_layak else 'Tidak Layak'

                # Masuk periode A?
                in_a = True
                if pa_start and c.created_at < pa_start:
                    in_a = False
                if pa_end and c.created_at > pa_end:
                    in_a = False
                if in_a and (pa_start or pa_end):
                    stats_a[label] += 1

                # Masuk periode B?
                in_b = True
                if pb_start and c.created_at < pb_start:
                    in_b = False
                if pb_end and c.created_at > pb_end:
                    in_b = False
                if in_b and (pb_start or pb_end):
                    stats_b[label] += 1

            return jsonify({
                'labels': ['Layak', 'Tidak Layak'],
                'values_a': [stats_a['Layak'], stats_a['Tidak Layak']],
                'values_b': [stats_b['Layak'], stats_b['Tidak Layak']],
                'label_a': f"Periode A ({pa_start_str or 'Awal'} s.d {pa_end_str or 'Akhir'})",
                'label_b': f"Periode B ({pb_start_str or 'Awal'} s.d {pb_end_str or 'Akhir'})",
                'title': 'Perbandingan Kelayakan Calon Antar Periode'
            })

        else:  # criteria
            criteria_type = request.args.get('criteria_type', 'penghasilan').strip()  # penghasilan, pekerjaan, kepemilikan_aset

            counts = {}
            for c in data_list:
                val = getattr(c, criteria_type) or 'Tidak Terinci'
                counts[val] = counts.get(val, 0) + 1

            labels = list(counts.keys())
            values = list(counts.values())

            # Ganti dengan label singkat agar muat di chart
            from core.constants import LABEL_SINGKAT
            labels_singkat = [LABEL_SINGKAT.get(l, l) for l in labels]

            return jsonify({
                'labels': labels_singkat,
                'values': values,
                'title': f'Distribusi Calon Berdasarkan Kriteria {criteria_type.replace("_", " ").title()}'
            })
