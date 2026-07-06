"""Flask Blueprints registration."""


def register_blueprints(app):
    """Daftarkan semua blueprint ke aplikasi Flask."""
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.calon import calon_bp
    from routes.about import about_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(calon_bp)
    app.register_blueprint(about_bp)
