"""Blueprint — Autentikasi Admin: login / logout."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
from models_db import User
from core.auth import csrf_required

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
