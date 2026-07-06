"""
Error handlers — 404, 500, dll.

Didaftarkan di app.py via register_error_handlers().
"""
from flask import render_template


def register_error_handlers(app):
    """Daftarkan custom error pages."""

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403
