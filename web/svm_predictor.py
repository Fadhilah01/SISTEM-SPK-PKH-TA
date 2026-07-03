"""
Service untuk load model SVM pipeline dan melakukan prediksi.
Pipeline .pkl terdiri dari:
    - model: SVM classifier (scikit-learn)
    - scaler: StandardScaler
    - le_pekerjaan: LabelEncoder untuk pekerjaan
    - le_aset: LabelEncoder untuk kepemilikan_aset
    - feature_cols: list nama fitur
    - results: dict metrik evaluasi
"""
import os
import numpy as np
import joblib
from config import Config


class SVMPredictor:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.model = None
        self.scaler = None
        self.le_pekerjaan = None
        self.le_aset = None
        self.feature_cols = None
        self.metrics = {}
        self._load_model()

    def _load_model(self):
        """Load pipeline dari file .pkl."""
        model_path = Config.MODEL_PATH
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model tidak ditemukan di {model_path}")

        pipeline = joblib.load(model_path)
        self.model = pipeline['model']
        self.scaler = pipeline['scaler']
        self.le_pekerjaan = pipeline['le_pekerjaan']
        self.le_aset = pipeline['le_aset']
        self.feature_cols = pipeline['feature_cols']
        self.metrics = pipeline.get('results', {})
        self.best_params = self.metrics.get('best_params', {})

    def predict(self, penghasilan, pekerjaan, aset, ibu_hamil,
                anak_usia_dini, anak_sekolah, disabilitas, lansia):
        """
        Prediksi kelayakan calon penerima PKH.

        Returns:
            dict: { 'label': 'Layak'/'Tidak Layak',
                    'probabilitas': float,
                    'confidence_pct': float }
        """
        # Encode kategorikal
        try:
            pekerjaan_enc = self.le_pekerjaan.transform([pekerjaan])[0]
        except ValueError:
            # Jika kategori tidak dikenal, default ke 0
            pekerjaan_enc = 0

        try:
            aset_enc = self.le_aset.transform([aset])[0]
        except ValueError:
            aset_enc = 0

        # Siapkan feature vector
        features = np.array([[
            penghasilan, pekerjaan_enc, aset_enc,
            int(ibu_hamil), anak_usia_dini, anak_sekolah,
            int(disabilitas), lansia
        ]])

        # Normalisasi
        features_scaled = self.scaler.transform(features)

        # Prediksi
        pred = self.model.predict(features_scaled)[0]
        proba = self.model.predict_proba(features_scaled)[0]

        label = 'Layak' if pred == 1 else 'Tidak Layak'
        confidence = float(max(proba))

        return {
            'label': label,
            'probabilitas': confidence,
            'confidence_pct': round(confidence * 100, 2)
        }

    def get_metrics(self):
        return self.metrics
