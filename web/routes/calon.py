"""Blueprint — CRUD Calon Penerima + Prediksi SVM."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models_db import db, CalonPenerima, HasilKeputusan
from core.auth import login_required, csrf_required
from core.constants import PENGHASILAN_MAPPING, PEKERJAAN_MAPPING, ASET_MAPPING
from core.scoring import compute_scores, predict_single, create_hasil_keputusan
from core.predictor import predictor, model_loaded

calon_bp = Blueprint('calon', __name__)


@calon_bp.route('/calon')
@login_required
def daftar_calon():
    """Daftar semua calon penerima dengan pencarian dan paginasi."""
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', '', type=str)

    query = CalonPenerima.query
    if q:
        query = query.filter(
            (CalonPenerima.nama.like(f"%{q}%"))
            | (CalonPenerima.alamat.like(f"%{q}%"))
        )

    pagination = query.order_by(
        CalonPenerima.created_at.desc()
    ).paginate(page=page, per_page=10, error_out=False)
    calon_list = pagination.items

    # Map hasil untuk quick view
    hasil_map = {}
    for h in HasilKeputusan.query.all():
        hasil_map[h.id_calon] = h

    return render_template('calon.html',
                           calon_list=calon_list,
                           hasil_map=hasil_map,
                           pagination=pagination,
                           q=q)


@calon_bp.route('/calon/tambah', methods=['GET', 'POST'])
@csrf_required
@login_required
def tambah_calon():
    """Tambah calon penerima baru + langsung prediksi."""
    if request.method == 'POST':
        try:
            penghasilan_val = request.form['penghasilan']
            pekerjaan_val = request.form['pekerjaan']
            aset_val = request.form['kepemilikan_aset']

            # ---- Hitung skor via fungsi terpusat ----
            skor = compute_scores(
                penghasilan_val, pekerjaan_val, aset_val,
                ibu_hamil=request.form.get('ibu_hamil') == 'on',
                anak_usia_dini=request.form.get('anak_usia_dini') == 'on',
                anak_sekolah=request.form.get('anak_sekolah') == 'on',
                disabilitas=request.form.get('disabilitas') == 'on',
                lansia=request.form.get('lansia') == 'on',
            )

            calon = CalonPenerima(
                nama=request.form['nama'],
                alamat=request.form['alamat'],
                penghasilan=penghasilan_val,
                pekerjaan=pekerjaan_val,
                kepemilikan_aset=aset_val,
                ibu_hamil=request.form.get('ibu_hamil') == 'on',
                anak_usia_dini=request.form.get('anak_usia_dini') == 'on',
                anak_sekolah=request.form.get('anak_sekolah') == 'on',
                disabilitas=request.form.get('disabilitas') == 'on',
                lansia=request.form.get('lansia') == 'on',
                **skor,  # semua field skor_* dari compute_scores
            )
            db.session.add(calon)
            db.session.commit()

            # ---- Prediksi via helper terpusat ----
            if predictor:
                result = predict_single(predictor, calon)
                if result:
                    keputusan_data = create_hasil_keputusan(
                        calon.id, result,
                        oleh=session.get('user_id', 'Sistem')
                    )
                    db.session.add(HasilKeputusan(**keputusan_data))
                    db.session.commit()
                    flash(
                        f"Data berhasil disimpan. Hasil: {result['label']} "
                        f"(confidence: {result['confidence_pct']}%)",
                        'success'
                    )
            else:
                flash("Data disimpan (model belum di-load, prediksi belum jalan)", 'warning')

        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", 'danger')

        return redirect(url_for('dashboard.index'))

    # GET — tampilkan form
    return render_template('calon_form.html',
                           calon=None,
                           penghasilan_list=list(PENGHASILAN_MAPPING.keys()),
                           pekerjaan_list=list(PEKERJAAN_MAPPING.keys()),
                           aset_list=list(ASET_MAPPING.keys()))


@calon_bp.route('/calon/<int:id>/edit', methods=['GET', 'POST'])
@csrf_required
@login_required
def edit_calon(id):
    """Edit data calon penerima."""
    calon = CalonPenerima.query.get_or_404(id)

    if request.method == 'POST':
        try:
            penghasilan_val = request.form['penghasilan']
            pekerjaan_val = request.form['pekerjaan']
            aset_val = request.form['kepemilikan_aset']

            # Update field teks
            calon.nama = request.form['nama']
            calon.alamat = request.form['alamat']
            calon.penghasilan = penghasilan_val
            calon.pekerjaan = pekerjaan_val
            calon.kepemilikan_aset = aset_val
            calon.ibu_hamil = request.form.get('ibu_hamil') == 'on'
            calon.anak_usia_dini = request.form.get('anak_usia_dini') == 'on'
            calon.anak_sekolah = request.form.get('anak_sekolah') == 'on'
            calon.disabilitas = request.form.get('disabilitas') == 'on'
            calon.lansia = request.form.get('lansia') == 'on'

            # ---- Hitung skor via fungsi terpusat ----
            skor = compute_scores(
                penghasilan_val, pekerjaan_val, aset_val,
                ibu_hamil=calon.ibu_hamil,
                anak_usia_dini=calon.anak_usia_dini,
                anak_sekolah=calon.anak_sekolah,
                disabilitas=calon.disabilitas,
                lansia=calon.lansia,
            )
            for key, val in skor.items():
                setattr(calon, key, val)

            db.session.commit()

            # ---- Update hasil prediksi ----
            if predictor and calon.hasil:
                result = predict_single(predictor, calon)
                if result:
                    calon.hasil.hasil_prediksi = (result['label'] == 'Layak')
                    calon.hasil.label_prediksi = result['label']
                    calon.hasil.probabilitas = result['probabilitas']
                    db.session.commit()
                    flash(f"Data diupdate. Hasil: {result['label']}", 'success')
            else:
                flash("Data berhasil diupdate.", 'success')

        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", 'danger')

        return redirect(url_for('dashboard.index'))

    return render_template('calon_form.html',
                           calon=calon,
                           penghasilan_list=list(PENGHASILAN_MAPPING.keys()),
                           pekerjaan_list=list(PEKERJAAN_MAPPING.keys()),
                           aset_list=list(ASET_MAPPING.keys()))


@calon_bp.route('/calon/<int:id>/hapus', methods=['POST'])
@csrf_required
@login_required
def hapus_calon(id):
    """Hapus data calon + hasil keputusan."""
    calon = CalonPenerima.query.get_or_404(id)
    try:
        if calon.hasil:
            db.session.delete(calon.hasil)
        db.session.delete(calon)
        db.session.commit()
        flash('Data berhasil dihapus.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('calon.daftar_calon'))


@calon_bp.route('/calon/<int:id>/prediksi-ulang', methods=['POST'])
@csrf_required
@login_required
def prediksi_ulang(id):
    """Prediksi ulang untuk satu calon."""
    calon = CalonPenerima.query.get_or_404(id)
    if not predictor:
        flash('Model tidak tersedia.', 'danger')
        return redirect(url_for('calon.daftar_calon'))

    try:
        result = predict_single(predictor, calon)
        if not result:
            flash('Prediksi gagal.', 'danger')
            return redirect(url_for('calon.daftar_calon'))

        if calon.hasil:
            calon.hasil.hasil_prediksi = (result['label'] == 'Layak')
            calon.hasil.label_prediksi = result['label']
            calon.hasil.probabilitas = result['probabilitas']
        else:
            keputusan_data = create_hasil_keputusan(calon.id, result)
            db.session.add(HasilKeputusan(**keputusan_data))
        db.session.commit()

        flash(f'Prediksi ulang berhasil: {result["label"]}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')

    return redirect(url_for('calon.daftar_calon'))
