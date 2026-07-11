import os
import logging
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# ─── Load .env file automatically if exists ───
env_file = os.path.join(BASE_DIR, ".env")
if os.path.exists(env_file):
    with open(env_file, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip("'\"")
                os.environ[key] = val


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
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or os.environ.get('SQLALCHEMY_DATABASE_URI')
    if not SQLALCHEMY_DATABASE_URI:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'spk_pkh.db')
    
    # Fix for Heroku/Supabase where URI might start with postgres:// instead of postgresql://
    if SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)

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
