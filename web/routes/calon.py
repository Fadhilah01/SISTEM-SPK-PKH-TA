"""Blueprint — CRUD Calon Penerima + Prediksi SVM + Bulk Import/Export."""
from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file
from models_db import db, CalonPenerima, HasilKeputusan
from core.auth import login_required, csrf_required
from core.constants import PENGHASILAN_MAPPING, PEKERJAAN_MAPPING, ASET_MAPPING, KOMPONEN_SOSIAL, LABEL_SINGKAT
from core.scoring import compute_scores, predict_single, create_hasil_keputusan
from core.predictor import predictor, model_loaded
from core.data_io import import_from_file, export_data, generate_template, get_column_options

calon_bp = Blueprint('calon', __name__)


@calon_bp.route('/calon')
@login_required
def daftar_calon():
    """Daftar semua calon penerima dengan pencarian, filter, dan paginasi."""
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', '', type=str)
    date_from = request.args.get('date_from', '', type=str)
    date_to = request.args.get('date_to', '', type=str)
    hasil_filter = request.args.get('hasil_filter', '', type=str)

    query = CalonPenerima.query

    # Filter pencarian nama/alamat
    if q:
        query = query.filter(
            (CalonPenerima.nama.like(f"%{q}%"))
            | (CalonPenerima.alamat.like(f"%{q}%"))
        )

    # Filter tanggal input
    if date_from:
        try:
            dt_from = datetime.strptime(date_from, '%Y-%m-%d').replace(tzinfo=timezone.utc)
            query = query.filter(CalonPenerima.created_at >= dt_from)
        except (ValueError, TypeError):
            pass

    if date_to:
        try:
            dt_to = datetime.strptime(date_to, '%Y-%m-%d').replace(
                hour=23, minute=59, second=59, tzinfo=timezone.utc
            )
            query = query.filter(CalonPenerima.created_at <= dt_to)
        except (ValueError, TypeError):
            pass

    # Filter hasil prediksi — perlu join ke HasilKeputusan
    if hasil_filter:
        if hasil_filter == 'layak':
            query = query.join(HasilKeputusan).filter(HasilKeputusan.hasil_prediksi == True)
        elif hasil_filter == 'tidak_layak':
            query = query.join(HasilKeputusan).filter(HasilKeputusan.hasil_prediksi == False)

    pagination = query.order_by(
        CalonPenerima.id.asc()
    ).paginate(page=page, per_page=10, error_out=False)
    calon_list = pagination.items

    # Map hasil untuk quick view
    hasil_map = {}
    for h in HasilKeputusan.query.all():
        hasil_map[h.id_calon] = h

    return render_template('calon/list.html',
                           calon_list=calon_list,
                           hasil_map=hasil_map,
                           pagination=pagination,
                           q=q,
                           date_from=date_from,
                           date_to=date_to,
                           hasil_filter=hasil_filter,
                           penghasilan_skor=PENGHASILAN_MAPPING,
                           pekerjaan_skor=PEKERJAAN_MAPPING,
                           aset_skor=ASET_MAPPING,
                           label_singkat=LABEL_SINGKAT)


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
    return render_template('calon/form.html',
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

    return render_template('calon/form.html',
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


# ─── BULK IMPORT ───


@calon_bp.route('/calon/import', methods=['GET', 'POST'])
@csrf_required
@login_required
def import_calon():
    """Import bulk dari file Excel/CSV."""
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or file.filename == '':
            flash('Silakan pilih file Excel atau CSV untuk di-upload.', 'danger')
            return redirect(url_for('calon.import_calon'))

        allowed = ('.xlsx', '.xls', '.csv')
        if not file.filename.lower().endswith(allowed):
            flash(f'Format file tidak didukung. Gunakan: {", ".join(allowed)}', 'danger')
            return redirect(url_for('calon.import_calon'))

        try:
            hasil = import_from_file(file, predictor)
            if hasil['success'] > 0:
                flash(
                    f"✅ Import berhasil: {hasil['success']} data tersimpan "
                    f"dan diprediksi otomatis.",
                    'success'
                )
            if hasil['failed'] > 0:
                # Tampilkan maks 5 error pertama
                err_preview = hasil['errors'][:5]
                for err in err_preview:
                    flash(f'⚠️ {err}', 'warning')
                if len(hasil['errors']) > 5:
                    flash(f'... dan {len(hasil["errors"]) - 5} error lainnya. Perbaiki data dan coba lagi.', 'warning')

            if hasil['success'] == 0 and hasil['failed'] == 0:
                flash('File kosong atau tidak ada data yang diproses.', 'info')

        except Exception as e:
            flash(f'Error saat memproses file: {str(e)}', 'danger')

        return redirect(url_for('calon.daftar_calon'))

    return render_template('calon/import.html')


@calon_bp.route('/calon/import/template')
@login_required
def download_template():
    """Download template Excel untuk import bulk."""
    buf = generate_template()
    return send_file(
        buf,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='template_import_pkh.xlsx',
    )


# ─── BULK EXPORT ───


@calon_bp.route('/calon/export', methods=['GET', 'POST'])
@login_required
@csrf_required
def export_calon():
    """Export data ke Excel/CSV dengan filter dinamis."""
    if request.method == 'POST':
        format_type = request.form.get('format', 'excel')
        date_from = request.form.get('date_from', '')
        date_to = request.form.get('date_to', '')
        hasil_filter = request.form.get('hasil_filter', '')
        q = request.form.get('q', '')
        selected_columns = request.form.getlist('columns')

        # Kirim semua kolom jika tidak ada yang dipilih
        if not selected_columns:
            selected_columns = [
                'id', 'nama', 'alamat', 'penghasilan', 'pekerjaan',
                'kepemilikan_aset', 'ibu_hamil', 'anak_usia_dini',
                'anak_sekolah', 'disabilitas', 'lansia',
                'skor_penghasilan', 'skor_pekerjaan', 'skor_kepemilikan_aset',
                'skor_ibu_hamil', 'skor_anak_usia_dini', 'skor_anak_sekolah',
                'skor_disabilitas', 'skor_lansia',
                'hasil_prediksi', 'probabilitas', 'tanggal_input',
                'tanggal_prediksi', 'oleh',
            ]

        filters = {
            'date_from': date_from,
            'date_to': date_to,
            'hasil': hasil_filter,
            'q': q,
            'columns': selected_columns,
        }

        try:
            buf, filename, mime_type = export_data(format_type=format_type, filters=filters)
            return send_file(
                buf,
                mimetype=mime_type,
                as_attachment=True,
                download_name=filename,
            )
        except Exception as e:
            flash(f'Error saat export: {str(e)}', 'danger')
            return redirect(url_for('calon.export_calon'))

    # GET — tampilkan form filter
    column_options = get_column_options()
    return render_template('calon/export.html',
                           column_options=column_options)


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
