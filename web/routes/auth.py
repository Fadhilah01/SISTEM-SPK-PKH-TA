"""Blueprint — Autentikasi Admin: login / logout / ganti password."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from models_db import User, db
from core.auth import csrf_required, login_required, validate_password_strength
from core.limiter import limiter

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
@csrf_required
@limiter.limit("5 per minute")
def login():
    """Halaman Login Admin."""
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            # Reset login attempts on success
            session.pop('login_attempts', None)
            session['user_id'] = user.id
            session.permanent = True

            # Force password change jika masih default
            if user.must_change_password:
                flash('Silakan ganti password Anda sebelum melanjutkan.', 'warning')
                return redirect(url_for('auth.change_password', force=True))

            flash(f"Selamat datang kembali, {user.nama_lengkap}!", 'success')
            return redirect(url_for('dashboard.index'))
        else:
            # Track failed login attempts
            attempts = session.get('login_attempts', 0) + 1
            session['login_attempts'] = attempts

            if attempts >= 10:
                flash('Akun sementara dikunci karena terlalu banyak percobaan gagal. Silakan coba lagi nanti.', 'danger')
            else:
                flash("Username atau password salah.", 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout', methods=['POST'])
@csrf_required
def logout():
    """Proses Logout Admin."""
    session.pop('user_id', None)
    session.pop('login_attempts', None)
    flash("Anda telah keluar dari sistem.", 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
@csrf_required
def change_password():
    """Halaman Ganti Password Admin."""
    user = User.query.get(session['user_id'])
    is_force = request.args.get('force', False)

    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if not user or not check_password_hash(user.password_hash, old_password):
            flash("Password lama salah.", 'danger')
            return redirect(url_for('auth.change_password', force=is_force))

        if new_password != confirm_password:
            flash("Konfirmasi password baru tidak cocok.", 'danger')
            return redirect(url_for('auth.change_password', force=is_force))

        # Validasi kekuatan password
        is_valid, msg = validate_password_strength(new_password)
        if not is_valid:
            flash(msg, 'danger')
            return redirect(url_for('auth.change_password', force=is_force))

        # Jangan biarkan password sama dengan yang lama
        if check_password_hash(user.password_hash, new_password):
            flash("Password baru tidak boleh sama dengan password lama.", 'danger')
            return redirect(url_for('auth.change_password', force=is_force))

        user.password_hash = generate_password_hash(new_password)
        user.must_change_password = False
        db.session.commit()

        flash("Password Anda berhasil diperbarui.", 'success')
        return redirect(url_for('dashboard.index'))

    return render_template('auth/change_password.html', is_force=is_force)

