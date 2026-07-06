"""
Predictor singleton — inisialisasi early, import dari mana saja.

Memecah circular import: blueprint tidak perlu import dari app.py.
"""
from svm_predictor import SVMPredictor

try:
    predictor = SVMPredictor()
    model_loaded = True
except Exception as e:
    print(f"[WARNING] Gagal load model: {e}")
    predictor = None
    model_loaded = False
