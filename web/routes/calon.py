"""Blueprint — CRUD Calon Penerima + Prediksi SVM + Bulk Import/Export."""
from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file
from models_db import db, CalonPenerima, HasilKeputusan
from core.auth import login_required, csrf_required
from core.constants import PENGHASILAN_MAPPING, PEKERJAAN_MAPPING, ASET_MAPPING, KOMPONEN_SOSIAL, LABEL_SINGKAT
from core.security import validate_file_upload, validate_text_length, sanitize_html
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

    # Filter pencarian nama/alamat/nik
    if q:
        query = query.filter(
            (CalonPenerima.nama.like(f"%{q}%"))
            | (CalonPenerima.alamat.like(f"%{q}%"))
            | (CalonPenerima.nik.like(f"%{q}%"))
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
            nik = sanitize_html(request.form['nik'].strip())
            nama = sanitize_html(request.form['nama'].strip())
            alamat = sanitize_html(request.form['alamat'].strip())

            # Validasi NIK (16 digit angka)
            import re
            if not re.match(r'^\d{16}$', nik):
                flash("Error: NIK harus berupa 16 digit angka.", 'danger')
                return redirect(url_for('calon.tambah_calon'))

            # Cegah duplikasi NIK
            existing = CalonPenerima.query.filter_by(nik=nik).first()
            if existing:
                flash(f"Error: Calon dengan NIK {nik} sudah terdaftar (Nama: {existing.nama}).", 'danger')
                return redirect(url_for('calon.tambah_calon'))

            # Validasi panjang input
            valid, msg = validate_text_length(nama, 'Nama', 100)
            if not valid:
                flash(msg, 'danger')
                return redirect(url_for('calon.tambah_calon'))
            valid, msg = validate_text_length(alamat, 'Alamat', 255)
            if not valid:
                flash(msg, 'danger')
                return redirect(url_for('calon.tambah_calon'))

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
                nik=nik,
                nama=nama,
                alamat=alamat,
                provinsi=request.form.get('provinsi') or None,
                kabupaten=request.form.get('kabupaten') or None,
                kecamatan=request.form.get('kecamatan') or None,
                desa_kelurahan=request.form.get('desa_kelurahan') or None,
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

            # Sanitasi input teks
            nik = sanitize_html(request.form['nik'].strip())
            nama = sanitize_html(request.form['nama'].strip())
            alamat = sanitize_html(request.form['alamat'].strip())

            # Validasi NIK (16 digit angka)
            import re
            if not re.match(r'^\d{16}$', nik):
                flash("Error: NIK harus berupa 16 digit angka.", 'danger')
                return redirect(url_for('calon.edit_calon', id=id))

            # Cegah duplikasi NIK (kecuali data calon ini sendiri)
            existing = CalonPenerima.query.filter(CalonPenerima.nik == nik, CalonPenerima.id != id).first()
            if existing:
                flash(f"Error: Calon dengan NIK {nik} sudah terdaftar (Nama: {existing.nama}).", 'danger')
                return redirect(url_for('calon.edit_calon', id=id))

            # Validasi panjang input
            valid, msg = validate_text_length(nama, 'Nama', 100)
            if not valid:
                flash(msg, 'danger')
                return redirect(url_for('calon.edit_calon', id=id))
            valid, msg = validate_text_length(alamat, 'Alamat', 255)
            if not valid:
                flash(msg, 'danger')
                return redirect(url_for('calon.edit_calon', id=id))

            # Update field teks
            calon.nik = nik
            calon.nama = nama
            calon.alamat = alamat
            calon.provinsi = request.form.get('provinsi') or None
            calon.kabupaten = request.form.get('kabupaten') or None
            calon.kecamatan = request.form.get('kecamatan') or None
            calon.desa_kelurahan = request.form.get('desa_kelurahan') or None
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

        # Validasi file upload (ekstensi, MIME, magic bytes)
        is_valid, err_msg = validate_file_upload(file)
        if not is_valid:
            flash(err_msg, 'danger')
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
                'id', 'nama', 'nik', 'alamat', 'penghasilan', 'pekerjaan',
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


# ─── API INTERNAL WILAYAH ───

_regions_cache = None
_regions_by_code = None

def get_regions():
    global _regions_cache, _regions_by_code
    if _regions_cache is None:
        import json
        import os
        from flask import current_app
        # Path relatif ke root aplikasi Flask
        filepath = os.path.join(current_app.root_path, 'static', 'data', 'daerah_indonesia.json')
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                _regions_cache = json.load(f)
            _regions_by_code = {r['kode']: r for r in _regions_cache}
        else:
            _regions_cache = []
            _regions_by_code = {}
    return _regions_cache, _regions_by_code


@calon_bp.route('/api/daerah')
@login_required
def get_daerah():
    """Endpoint API Internal untuk Autocomplete daerah (Provinsi, Kabupaten, Kecamatan, Desa)."""
    from flask import jsonify
    q = request.args.get('q', '').strip().upper()
    level = request.args.get('level', '').strip()
    parent = request.args.get('parent', '').strip()

    regions, regions_by_code = get_regions()
    results = []

    # Pencarian flat O(n) case-insensitive includes
    for r in regions:
        # Filter level jika ada
        if level and r.get('level') != level:
            continue
        # Filter parent jika ada
        if parent and r.get('parent') != parent:
            continue
        # Filter search query jika ada
        if q and q not in r.get('nama', ''):
            continue

        # Susun nama lengkap bertingkat untuk memudahkan membedakan duplikat nama
        fullname_parts = [r['nama']]
        curr = r
        while curr.get('parent') and curr['parent'] in regions_by_code:
            curr = regions_by_code[curr['parent']]
            name = curr['nama']
            # Hapus prefix KABUPATEN atau KOTA agar tidak terlalu panjang
            if name.startswith("KABUPATEN "):
                name = name[10:]
            elif name.startswith("KOTA "):
                name = name[5:]
            fullname_parts.append(name)
        
        fullname = ", ".join(fullname_parts)

        results.append({
            'kode': r['kode'],
            'nama': r['nama'],
            'level': r['level'],
            'fullname': fullname
        })
        
        # Batasi maksimal 20 hasil demi performa (hanya jika ada query pencarian atau me-list desa)
        if (q or level == 'desa') and len(results) >= 20:
            break

    return jsonify(results)

