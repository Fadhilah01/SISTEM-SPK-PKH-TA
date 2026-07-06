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
        if User.query.filter_by(username='admin').first() is None:
            admin_user = User(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                nama_lengkap='Administrator Dinsos',
            )
            db.session.add(admin_user)
            db.session.commit()
            print("[OK] Admin user default berhasil dibuat: admin / admin123")
        print("[OK] Database siap.")


if __name__ == '__main__':
    init_db()
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
