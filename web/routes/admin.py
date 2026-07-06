"""Blueprint — Manajemen Pengguna (Superadmin Only)."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash
from models_db import User, db
from core.auth import login_required, superadmin_required, csrf_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/users')
@login_required
@superadmin_required
def list_users():
    """Tampilkan daftar semua user admin."""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)


@admin_bp.route('/users/tambah', methods=['GET', 'POST'])
@login_required
@superadmin_required
@csrf_required
def tambah_user():
    """Tambah user admin baru."""
    if request.method == 'POST':
        nama_lengkap = request.form['nama_lengkap']
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        # Validasi duplikasi username
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash(f"Username '{username}' sudah terdaftar.", 'danger')
            return redirect(url_for('admin.tambah_user'))

        if len(password) < 6:
            flash("Password minimal harus 6 karakter.", 'danger')
            return redirect(url_for('admin.tambah_user'))

        if role not in ('superadmin', 'admin'):
            flash("Role tidak valid.", 'danger')
            return redirect(url_for('admin.tambah_user'))

        try:
            new_user = User(
                username=username,
                nama_lengkap=nama_lengkap,
                password_hash=generate_password_hash(password),
                role=role
            )
            db.session.add(new_user)
            db.session.commit()
            flash(f"User admin '{nama_lengkap}' berhasil ditambahkan.", 'success')
            return redirect(url_for('admin.list_users'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", 'danger')
            return redirect(url_for('admin.tambah_user'))

    return render_template('admin/user_form.html', user=None)


@admin_bp.route('/users/<int:id>/detail')
@login_required
@superadmin_required
def detail_user(id):
    """Lihat detail profil admin."""
    user = User.query.get_or_404(id)
    return render_template('admin/user_detail.html', user=user)


@admin_bp.route('/users/<int:id>/hapus', methods=['POST'])
@login_required
@superadmin_required
@csrf_required
def hapus_user(id):
    """Hapus user admin."""
    user = User.query.get_or_404(id)

    # Validasi: mencegah menghapus diri sendiri
    if user.id == session.get('user_id'):
        flash("Anda tidak dapat menghapus akun Anda sendiri saat sedang masuk log.", 'danger')
        return redirect(url_for('admin.list_users'))

    try:
        db.session.delete(user)
        db.session.commit()
        flash(f"User admin '{user.nama_lengkap}' berhasil dihapus.", 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", 'danger')

    return redirect(url_for('admin.list_users'))
