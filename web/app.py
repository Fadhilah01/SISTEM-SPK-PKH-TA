"""Flask App - SPK Kelayakan Calon Penerima Bantuan PKH."""
import os
import sys
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

# Tambah parent dir ke path agar import lokal work
sys.path.insert(0, os.path.dirname(__file__))

from config import Config
from models_db import db, CalonPenerima, HasilKeputusan, User
from svm_predictor import SVMPredictor

app = Flask(__name__)
app.config.from_object(Config)
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


# ─────────────────── Mappings & Utilities ───────────────────

PENGHASILAN_MAPPING = {
    'Desil 1 (< Rp.500.000)': 5,
    'Desil 2 (Rp.600.000 - Rp.700.000)': 4,
    'Desil 3 (Rp.800.000 - Rp.900.000)': 3,
    'Desil 4 (Rp.1.000.000 - Rp.1.200.000)': 2,
    'Desil 5 (Rp.1.300.000 - Rp.1.500.000)': 1
}

PEKERJAAN_MAPPING = {
    'Tidak Bekerja': 5,
    'Pekerja Bebas': 4,
    'Petani/Nelayan': 3,
    'Wiraswasta': 2,
    'PNS/Pegawai Tetap': 1
}

ASET_MAPPING = {
    'Tidak Memiliki Aset': 5,
    'Memiliki Motor (harga jual rendah)': 4,
    'Memiliki Motor (harga jual tinggi)': 3,
    'Memiliki Mobil atau Tanah/Kebun': 2,
    'Memiliki Mobil dan Tanah/Kebun': 1
}


def login_required(f):
    """Dekorator untuk memproteksi halaman yang membutuhkan login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu untuk mengakses sistem.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# Context processor untuk menyediakan data user login di semua template
@app.context_processor
def inject_user():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return dict(current_user=user)
    return dict(current_user=None)


# ─────────────────── Routes ───────────────────

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Halaman Login Admin."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session.permanent = True
            flash(f"Selamat datang kembali, {user.nama_lengkap}!", 'success')
            return redirect(url_for('dashboard'))
        else:
            flash("Username atau password salah.", 'danger')

    return render_template('login.html')


@app.route('/logout', methods=['POST'])
def logout():
    """Proses Logout Admin."""
    session.pop('user_id', None)
    flash("Anda telah keluar dari sistem.", 'success')
    return redirect(url_for('login'))


@app.route('/')
@login_required
def dashboard():
    """Dashboard utama — ringkasan data dan hasil keputusan."""
    total_calon = CalonPenerima.query.count()
    total_layak = HasilKeputusan.query.filter_by(hasil_prediksi=True).count()
    total_tidak = HasilKeputusan.query.filter_by(hasil_prediksi=False).count()

    # 10 hasil terbaru
    recent = HasilKeputusan.query.order_by(
        HasilKeputusan.tanggal_prediksi.desc()
    ).limit(10).all()

    # Distribusi calon per desa untuk visualisasi
    count_posona = CalonPenerima.query.filter(CalonPenerima.alamat.like('%Posona%')).filter(~CalonPenerima.alamat.like('%Posona Atas%')).count()
    count_posona_atas = CalonPenerima.query.filter(CalonPenerima.alamat.like('%Posona Atas%')).count()
    count_palapi = CalonPenerima.query.filter(CalonPenerima.alamat.like('%Kasimbar Palapi%')).count()
    
    desa_stats = {
        'Posona': count_posona,
        'Kasimbar Palapi': count_palapi,
        'Posona Atas': count_posona_atas
    }

    return render_template('dashboard.html',
                           total_calon=total_calon,
                           total_layak=total_layak,
                           total_tidak=total_tidak,
                           recent=recent,
                           desa_stats=desa_stats,
                           model_loaded=model_loaded)


@app.route('/calon')
@login_required
def daftar_calon():
    """Daftar semua calon penerima dengan pencarian dan paginasi."""
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', '', type=str)

    query = CalonPenerima.query
    if q:
        query = query.filter((CalonPenerima.nama.like(f"%{q}%")) | (CalonPenerima.alamat.like(f"%{q}%")))

    pagination = query.order_by(CalonPenerima.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
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


@app.route('/calon/tambah', methods=['GET', 'POST'])
@login_required
def tambah_calon():
    """Tambah calon penerima baru + langsung prediksi."""
    if request.method == 'POST':
        try:
            penghasilan_val = request.form['penghasilan']
            pekerjaan_val = request.form['pekerjaan']
            aset_val = request.form['kepemilikan_aset']

            # Map categories to scores
            skor_penghasilan = PENGHASILAN_MAPPING[penghasilan_val]
            skor_pekerjaan = PEKERJAAN_MAPPING[pekerjaan_val]
            skor_kepemilikan_aset = ASET_MAPPING[aset_val]

            ibu_hamil = request.form.get('ibu_hamil') == 'on'
            anak_usia_dini = request.form.get('anak_usia_dini') == 'on'
            anak_sekolah = request.form.get('anak_sekolah') == 'on'
            disabilitas = request.form.get('disabilitas') == 'on'
            lansia = request.form.get('lansia') == 'on'

            calon = CalonPenerima(
                nama=request.form['nama'],
                alamat=request.form['alamat'],
                penghasilan=penghasilan_val,
                pekerjaan=pekerjaan_val,
                kepemilikan_aset=aset_val,
                ibu_hamil=ibu_hamil,
                anak_usia_dini=anak_usia_dini,
                anak_sekolah=anak_sekolah,
                disabilitas=disabilitas,
                lansia=lansia,
                skor_penghasilan=skor_penghasilan,
                skor_pekerjaan=skor_pekerjaan,
                skor_kepemilikan_aset=skor_kepemilikan_aset,
                skor_ibu_hamil=1 if ibu_hamil else 0,
                skor_anak_usia_dini=1 if anak_usia_dini else 0,
                skor_anak_sekolah=1 if anak_sekolah else 0,
                skor_disabilitas=1 if disabilitas else 0,
                skor_lansia=1 if lansia else 0
            )
            db.session.add(calon)
            db.session.commit()

            # Prediksi dengan SVM
            if predictor:
                result = predictor.predict(
                    penghasilan_skor=calon.skor_penghasilan,
                    pekerjaan_skor=calon.skor_pekerjaan,
                    aset_skor=calon.skor_kepemilikan_aset,
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
                    oleh=session.get('user_id', 'Sistem')
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
                           penghasilan_list=list(PENGHASILAN_MAPPING.keys()),
                           pekerjaan_list=list(PEKERJAAN_MAPPING.keys()),
                           aset_list=list(ASET_MAPPING.keys()))


@app.route('/calon/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_calon(id):
    """Edit data calon penerima."""
    calon = CalonPenerima.query.get_or_404(id)

    if request.method == 'POST':
        try:
            penghasilan_val = request.form['penghasilan']
            pekerjaan_val = request.form['pekerjaan']
            aset_val = request.form['kepemilikan_aset']

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

            # Re-map scores
            calon.skor_penghasilan = PENGHASILAN_MAPPING[penghasilan_val]
            calon.skor_pekerjaan = PEKERJAAN_MAPPING[pekerjaan_val]
            calon.skor_kepemilikan_aset = ASET_MAPPING[aset_val]
            calon.skor_ibu_hamil = 1 if calon.ibu_hamil else 0
            calon.skor_anak_usia_dini = 1 if calon.anak_usia_dini else 0
            calon.skor_anak_sekolah = 1 if calon.anak_sekolah else 0
            calon.skor_disabilitas = 1 if calon.disabilitas else 0
            calon.skor_lansia = 1 if calon.lansia else 0

            db.session.commit()

            # Update hasil prediksi
            if predictor and calon.hasil:
                result = predictor.predict(
                    penghasilan_skor=calon.skor_penghasilan,
                    pekerjaan_skor=calon.skor_pekerjaan,
                    aset_skor=calon.skor_kepemilikan_aset,
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
                           penghasilan_list=list(PENGHASILAN_MAPPING.keys()),
                           pekerjaan_list=list(PEKERJAAN_MAPPING.keys()),
                           aset_list=list(ASET_MAPPING.keys()))


@app.route('/calon/<int:id>/hapus', methods=['POST'])
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
    return redirect(url_for('daftar_calon'))


@app.route('/calon/<int:id>/prediksi-ulang', methods=['POST'])
@login_required
def prediksi_ulang(id):
    """Prediksi ulang untuk satu calon."""
    calon = CalonPenerima.query.get_or_404(id)
    if not predictor:
        flash('Model tidak tersedia.', 'danger')
        return redirect(url_for('daftar_calon'))

    try:
        result = predictor.predict(
            penghasilan_skor=calon.skor_penghasilan,
            pekerjaan_skor=calon.skor_pekerjaan,
            aset_skor=calon.skor_kepemilikan_aset,
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
@login_required
def about():
    """Informasi tentang sistem dan model."""
    metrics = predictor.get_metrics() if predictor else {}
    return render_template('about.html', metrics=metrics, model_loaded=model_loaded)


# ─────────────────── Inisialisasi DB ───────────────────

def init_db():
    """Buat tabel jika belum ada dan seed data admin default."""
    with app.app_context():
        db.create_all()
        # Seed user admin default jika belum ada
        if User.query.filter_by(username='admin').first() is None:
            admin_user = User(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                nama_lengkap='Administrator Dinsos'
            )
            db.session.add(admin_user)
            db.session.commit()
            print("[OK] Admin user default berhasil dibuat: admin / admin123")
        print("[OK] Database siap.")


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
