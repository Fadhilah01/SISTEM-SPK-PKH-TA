"""
Decorators dan context processors untuk autentikasi & CSRF.

Dipisahkan dari app.py agar bisa diimpor oleh semua blueprint
tanpa circular import.
"""
import secrets
from functools import wraps
from flask import session, flash, redirect, url_for, request, abort
from models_db import User


# ─── Autentikasi ───


def login_required(f):
    """Dekorator — redirect ke login jika belum autentikasi."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu untuk mengakses sistem.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def superadmin_required(f):
    """Dekorator — hanya izinkan user dengan role 'superadmin'."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu untuk mengakses sistem.', 'warning')
            return redirect(url_for('auth.login'))
        user = User.query.get(session['user_id'])
        if not user or user.role != 'superadmin':
            flash('Anda tidak memiliki hak akses untuk halaman ini.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function


def inject_user():
    """Context processor — sediakan current_user di semua template."""
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return dict(current_user=user)
    return dict(current_user=None)


# ─── CSRF Protection (manual, tanpa flask-wtf) ───


def generate_csrf_token():
    """Buat atau ambil CSRF token dari session."""
    if '_csrf_token' not in session:
        session['_csrf_token'] = secrets.token_hex(32)
    return session['_csrf_token']


def inject_csrf():
    """Context processor — sediakan csrf_token di semua template."""
    return dict(csrf_token=generate_csrf_token())


def csrf_required(f):
    """Dekorator — validasi CSRF token di setiap POST request."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'POST':
            token = request.form.get('_csrf_token')
            stored = session.get('_csrf_token')
            if not token or not stored or not secrets.compare_digest(token, stored):
                abort(403)
        return f(*args, **kwargs)
    return decorated_function
