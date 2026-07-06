"""
Flask App — SPK Kelayakan Calon Penerima Bantuan PKH.

Entry point & factory. Routes diorganisir dalam Blueprints
(routes/) dan business logic di core/.
"""
from flask import Flask
from config import Config
from models_db import db, User
from werkzeug.security import generate_password_hash
from routes import register_blueprints
from core.auth import inject_user, inject_csrf


def create_app():
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(Config)
    app.jinja_env.globals.update(zip=zip)

    db.init_app(app)
    register_blueprints(app)

    # Context processors
    app.context_processor(inject_user)
    app.context_processor(inject_csrf)

    # Register error handlers
    from core.error_handlers import register_error_handlers
    register_error_handlers(app)

    return app


def init_db():
    """Buat tabel jika belum ada dan seed data admin default."""
    app = create_app()
    with app.app_context():
        db.create_all()
        
        # Seed akun Superadmin
        if User.query.filter_by(username='admin').first() is None:
            superadmin = User(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                nama_lengkap='Administrator Dinsos (Super)',
                role='superadmin'
            )
            db.session.add(superadmin)
            db.session.commit()
            print("[OK] Superadmin default berhasil dibuat: admin / admin123")
            
        # Seed akun Admin biasa
        if User.query.filter_by(username='user1').first() is None:
            normal_admin = User(
                username='user1',
                password_hash=generate_password_hash('user1123'),
                nama_lengkap='Pendamping PKH (Admin)',
                role='admin'
            )
            db.session.add(normal_admin)
            db.session.commit()
            print("[OK] Admin default berhasil dibuat: user1 / user1123")

        print("[OK] Database siap.")


if __name__ == '__main__':
    init_db()
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
