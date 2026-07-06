import os
import logging
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # ─── Secret Key ───
    # Prioritaskan env var, fallback ke key acak per restart
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if SECRET_KEY is None:
        SECRET_KEY = os.urandom(32).hex()
        logging.warning(
            "[SECURITY] SECRET_KEY tidak di-set via env var. "
            "Menggunakan key acak (session akan invalid setelah restart). "
            "Set SECRET_KEY di environment variable untuk persistensi."
        )

    # ─── Database ───
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'spk_pkh.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ─── Model Path ───
    MODEL_PATH = os.path.join(BASE_DIR, 'models', 'svm_pkh_pipeline.pkl')

    # ─── Session Security ───
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False  # Set True jika sudah pakai HTTPS
    PERMANENT_SESSION_LIFETIME = timedelta(hours=4)

    # ─── Rate Limiting ───
    RATELIMIT_DEFAULT = "200 per day"
    RATELIMIT_STORAGE_URL = "memory://"
    RATELIMIT_HEADERS_ENABLED = True
