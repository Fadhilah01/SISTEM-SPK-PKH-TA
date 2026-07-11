"""
Flask App — SPK Kelayakan Calon Penerima Bantuan PKH.

Entry point & factory. Routes diorganisir dalam Blueprints
(routes/) dan business logic di core/.
"""
import os
import logging
import mimetypes
from flask import Flask
from config import Config
from models_db import db, User
from werkzeug.security import generate_password_hash
from routes import register_blueprints
from core.auth import inject_user, inject_csrf
from core.limiter import limiter

# Override Windows registry MIME types to avoid 'text/plain' script block errors
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')


# ─── Konfigurasi Logging ───
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)


def create_app():
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Nonaktifkan debug mode untuk production
    app.debug = False

    app.jinja_env.globals.update(zip=zip)

    db.init_app(app)
    limiter.init_app(app)
    register_blueprints(app)

    # Context processors
    app.context_processor(inject_user)
    app.context_processor(inject_csrf)

    # Register error handlers
    from core.error_handlers import register_error_handlers
    register_error_handlers(app)

    # Register security headers
    from core.security import register_security_headers
    register_security_headers(app)

    return app


def init_db():
    """Buat tabel jika belum ada dan seed data admin default."""
    app = create_app()
    with app.app_context():
        db.create_all()

        # ─── Migrasi: Tambah kolom must_change_password jika belum ada ───
        # SQLite dengan SQLAlchemy tidak auto-migrasi, jadi kita cek manual
        import logging
        logger = logging.getLogger(__name__)
        try:
            import sqlalchemy as sa
            inspector = sa.inspect(db.engine)
            columns = [c['name'] for c in inspector.get_columns('users')]
            if 'must_change_password' not in columns:
                db.session.execute(sa.text(
                    "ALTER TABLE users ADD COLUMN must_change_password BOOLEAN DEFAULT 0"
                ))
                db.session.commit()
                logger.info("[MIGRASI] Kolom 'must_change_password' berhasil ditambahkan ke tabel users.")
        except Exception as e:
            logger.warning(f"[MIGRASI] Gagal migrasi (mungkin sudah ada): {e}")

        # ─── Migrasi: Tambah kolom nik ke calon_penerima jika belum ada ───
        try:
            import sqlalchemy as sa
            inspector = sa.inspect(db.engine)
            columns = [c['name'] for c in inspector.get_columns('calon_penerima')]
            if 'nik' not in columns:
                db.session.execute(sa.text(
                    "ALTER TABLE calon_penerima ADD COLUMN nik VARCHAR(16)"
                ))
                db.session.commit()
                logger.info("[MIGRASI] Kolom 'nik' berhasil ditambahkan ke tabel calon_penerima.")

                # Backfill existing data with unique mock NIKs (e.g. 1234567890123 + 3-digit ID)
                from models_db import CalonPenerima
                all_calon = CalonPenerima.query.all()
                for c in all_calon:
                    c.nik = f"1234567890123{c.id:03d}"
                db.session.commit()
                logger.info(f"[MIGRASI] Berhasil mengisi NIK unik untuk {len(all_calon)} data calon penerima lama.")

                # Create unique index
                db.session.execute(sa.text(
                    "CREATE UNIQUE INDEX IF NOT EXISTS idx_calon_penerima_nik ON calon_penerima (nik)"
                ))
                db.session.commit()
                logger.info("[MIGRASI] Berhasil membuat index unik idx_calon_penerima_nik.")
        except Exception as e:
            logger.warning(f"[MIGRASI] Gagal migrasi NIK calon_penerima: {e}")
        
        # Seed akun Superadmin
        if User.query.filter_by(username='admin').first() is None:
            superadmin = User(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                nama_lengkap='Administrator Dinsos (Super)',
                role='superadmin',
                must_change_password=True
            )
            db.session.add(superadmin)
            db.session.commit()
            print("[OK] Superadmin default berhasil dibuat: admin / admin123")
            print("[!] WAJIB ganti password segera — akun default terdeteksi!")

        # Seed akun Admin biasa
        if User.query.filter_by(username='user1').first() is None:
            normal_admin = User(
                username='user1',
                password_hash=generate_password_hash('user1123'),
                nama_lengkap='Pendamping PKH (Admin)',
                role='admin',
                must_change_password=True
            )
            db.session.add(normal_admin)
            db.session.commit()
            print("[OK] Admin default berhasil dibuat: user1 / user1123")

        print("[OK] Database siap.")


app = create_app()

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)  # debug=False via Config di create_app()
