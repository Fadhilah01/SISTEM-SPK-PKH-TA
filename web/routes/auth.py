"""Blueprint — Autentikasi Admin: login / logout / ganti password."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from models_db import User, db
from core.auth import csrf_required, login_required

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
@csrf_required
def login():
    """Halaman Login Admin."""
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session.permanent = True
            flash(f"Selamat datang kembali, {user.nama_lengkap}!", 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash("Username atau password salah.", 'danger')

    return render_template('login.html')


@auth_bp.route('/logout', methods=['POST'])
@csrf_required
def logout():
    """Proses Logout Admin."""
    session.pop('user_id', None)
    flash("Anda telah keluar dari sistem.", 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
@csrf_required
def change_password():
    """Halaman Ganti Password Admin."""
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        user = User.query.get(session['user_id'])
        if not user or not check_password_hash(user.password_hash, old_password):
            flash("Password lama salah.", 'danger')
            return redirect(url_for('auth.change_password'))

        if new_password != confirm_password:
            flash("Konfirmasi password baru tidak cocok.", 'danger')
            return redirect(url_for('auth.change_password'))

        if len(new_password) < 6:
            flash("Password baru minimal harus 6 karakter.", 'danger')
            return redirect(url_for('auth.change_password'))

        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        
        flash("Password Anda berhasil diperbarui.", 'success')
        return redirect(url_for('dashboard.index'))

    return render_template('change_password.html')

