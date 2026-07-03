"""Flask App - SPK Kelayakan Calon Penerima Bantuan PKH."""
import os
import sys
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

# Tambah parent dir ke path agar import lokal work
sys.path.insert(0, os.path.dirname(__file__))

from config import Config
from models_db import db, CalonPenerima, HasilKeputusan
from svm_predictor import SVMPredictor

# Template filter untuk format Rupiah
def rupiah_format(value):
    if value is None:
        return "Rp 0"
    return f"Rp {value:,.0f}".replace(",", ".")

app = Flask(__name__)
app.config.from_object(Config)
app.jinja_env.filters['rupiah'] = rupiah_format
app.jinja_env.globals.update(zip=zip)

db.init_app(app)

# Inisialisasi model SVM (singleton)
try:
    predictor = SVMPredictor()
    model_loaded = True
except Exception as e:
    print(f"[WARNING] Gagal load model: {e}")
    predictor = None
    model_loaded = False


# ─────────────────── Routes ───────────────────

@app.route('/')
def dashboard():
    """Dashboard utama — ringkasan data dan hasil keputusan."""
    total_calon = CalonPenerima.query.count()
    total_layak = HasilKeputusan.query.filter_by(hasil_prediksi=True).count()
    total_tidak = HasilKeputusan.query.filter_by(hasil_prediksi=False).count()

    # 10 hasil terbaru
    recent = HasilKeputusan.query.order_by(
        HasilKeputusan.tanggal_prediksi.desc()
    ).limit(10).all()

    metrics = predictor.get_metrics() if predictor else {}

    return render_template('dashboard.html',
                           total_calon=total_calon,
                           total_layak=total_layak,
                           total_tidak=total_tidak,
                           recent=recent,
                           metrics=metrics,
                           model_loaded=model_loaded)


@app.route('/calon')
def daftar_calon():
    """Daftar semua calon penerima."""
    calon_list = CalonPenerima.query.order_by(CalonPenerima.created_at.desc()).all()

    # Map hasil untuk quick view
    hasil_map = {}
    for h in HasilKeputusan.query.all():
        hasil_map[h.id_calon] = h

    return render_template('calon.html', calon_list=calon_list, hasil_map=hasil_map)


@app.route('/calon/tambah', methods=['GET', 'POST'])
def tambah_calon():
    """Tambah calon penerima baru + langsung prediksi."""
    if request.method == 'POST':
        try:
            calon = CalonPenerima(
                nama=request.form['nama'],
                alamat=request.form['alamat'],
                penghasilan=float(request.form['penghasilan']),
                pekerjaan=request.form['pekerjaan'],
                kepemilikan_aset=request.form['kepemilikan_aset'],
                ibu_hamil=request.form.get('ibu_hamil') == 'on',
                anak_usia_dini=int(request.form.get('anak_usia_dini', 0)),
                anak_sekolah=int(request.form.get('anak_sekolah', 0)),
                disabilitas=request.form.get('disabilitas') == 'on',
                lansia=int(request.form.get('lansia', 0)),
            )
            db.session.add(calon)
            db.session.commit()

            # Prediksi dengan SVM
            if predictor:
                result = predictor.predict(
                    penghasilan=calon.penghasilan,
                    pekerjaan=calon.pekerjaan,
                    aset=calon.kepemilikan_aset,
                    ibu_hamil=calon.ibu_hamil,
                    anak_usia_dini=calon.anak_usia_dini,
                    anak_sekolah=calon.anak_sekolah,
                    disabilitas=calon.disabilitas,
                    lansia=calon.lansia,
                )
                keputusan = HasilKeputusan(
                    id_calon=calon.id,
                    hasil_prediksi=(result['label'] == 'Layak'),
                    label_prediksi=result['label'],
                    probabilitas=result['probabilitas'],
                )
                db.session.add(keputusan)
                db.session.commit()
                flash(f"Data berhasil disimpan. Hasil: {result['label']} "
                      f"(confidence: {result['confidence_pct']}%)", 'success')
            else:
                flash("Data disimpan (model belum di-load, prediksi belum jalan)", 'warning')

        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", 'danger')

        return redirect(url_for('dashboard'))

    # GET — tampilkan form
    return render_template('calon_form.html',
                           calon=None,
                           pekerjaan_list=[
                               'Tidak Bekerja', 'Buruh', 'Petani', 'Nelayan',
                               'Pedagang Kecil', 'IRT', 'PNS', 'Karyawan Swasta', 'Lainnya'
                           ],
                           aset_list=[
                               'Tidak Punya', 'Rumah Sangat Sederhana',
                               'Rumah Sederhana', 'Lahan Terbatas', 'Lainnya'
                           ])


@app.route('/calon/<int:id>/edit', methods=['GET', 'POST'])
def edit_calon(id):
    """Edit data calon penerima."""
    calon = CalonPenerima.query.get_or_404(id)

    if request.method == 'POST':
        try:
            calon.nama = request.form['nama']
            calon.alamat = request.form['alamat']
            calon.penghasilan = float(request.form['penghasilan'])
            calon.pekerjaan = request.form['pekerjaan']
            calon.kepemilikan_aset = request.form['kepemilikan_aset']
            calon.ibu_hamil = request.form.get('ibu_hamil') == 'on'
            calon.anak_usia_dini = int(request.form.get('anak_usia_dini', 0))
            calon.anak_sekolah = int(request.form.get('anak_sekolah', 0))
            calon.disabilitas = request.form.get('disabilitas') == 'on'
            calon.lansia = int(request.form.get('lansia', 0))
            db.session.commit()

            # Update hasil prediksi
            if predictor and calon.hasil:
                result = predictor.predict(
                    penghasilan=calon.penghasilan,
                    pekerjaan=calon.pekerjaan,
                    aset=calon.kepemilikan_aset,
                    ibu_hamil=calon.ibu_hamil,
                    anak_usia_dini=calon.anak_usia_dini,
                    anak_sekolah=calon.anak_sekolah,
                    disabilitas=calon.disabilitas,
                    lansia=calon.lansia,
                )
                calon.hasil.hasil_prediksi = (result['label'] == 'Layak')
                calon.hasil.label_prediksi = result['label']
                calon.hasil.probabilitas = result['probabilitas']
                db.session.commit()
                flash(f"Data diupdate. Hasil: {result['label']}", 'success')

        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", 'danger')

        return redirect(url_for('dashboard'))

    return render_template('calon_form.html',
                           calon=calon,
                           pekerjaan_list=[
                               'Tidak Bekerja', 'Buruh', 'Petani', 'Nelayan',
                               'Pedagang Kecil', 'IRT', 'PNS', 'Karyawan Swasta', 'Lainnya'
                           ],
                           aset_list=[
                               'Tidak Punya', 'Rumah Sangat Sederhana',
                               'Rumah Sederhana', 'Lahan Terbatas', 'Lainnya'
                           ])


@app.route('/calon/<int:id>/hapus', methods=['POST'])
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
    return redirect(url_for('daftar_calon'))


@app.route('/calon/<int:id>/prediksi-ulang', methods=['POST'])
def prediksi_ulang(id):
    """Prediksi ulang untuk satu calon."""
    calon = CalonPenerima.query.get_or_404(id)
    if not predictor:
        flash('Model tidak tersedia.', 'danger')
        return redirect(url_for('daftar_calon'))

    try:
        result = predictor.predict(
            penghasilan=calon.penghasilan,
            pekerjaan=calon.pekerjaan,
            aset=calon.kepemilikan_aset,
            ibu_hamil=calon.ibu_hamil,
            anak_usia_dini=calon.anak_usia_dini,
            anak_sekolah=calon.anak_sekolah,
            disabilitas=calon.disabilitas,
            lansia=calon.lansia,
        )

        if calon.hasil:
            calon.hasil.hasil_prediksi = (result['label'] == 'Layak')
            calon.hasil.label_prediksi = result['label']
            calon.hasil.probabilitas = result['probabilitas']
        else:
            keputusan = HasilKeputusan(
                id_calon=calon.id,
                hasil_prediksi=(result['label'] == 'Layak'),
                label_prediksi=result['label'],
                probabilitas=result['probabilitas'],
            )
            db.session.add(keputusan)
        db.session.commit()

        flash(f'Prediksi ulang berhasil: {result["label"]}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')

    return redirect(url_for('daftar_calon'))


@app.route('/about')
def about():
    """Informasi tentang sistem dan model."""
    metrics = predictor.get_metrics() if predictor else {}
    return render_template('about.html', metrics=metrics, model_loaded=model_loaded)


# ─────────────────── Inisialisasi DB ───────────────────

def init_db():
    """Buat tabel jika belum ada."""
    with app.app_context():
        db.create_all()
        print("[OK] Database siap.")


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
