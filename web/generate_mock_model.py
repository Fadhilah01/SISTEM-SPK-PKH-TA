import os
import numpy as np
from sklearn.svm import SVC
from sklearn.preprocessing import MinMaxScaler
import joblib

def generate_mock():
    print("Generating mock SVM model pipeline...")
    
    # Boundary data to ensure the MinMaxScaler fits columns 0-2 for 1 to 5, and columns 3-7 for 0 to 1
    X_dummy_min = [1, 1, 1, 0, 0, 0, 0, 0]
    X_dummy_max = [5, 5, 5, 1, 1, 1, 1, 1]
    
    # Generate 100 random training instances
    np.random.seed(42)
    X_train = np.random.randint(1, 6, size=(100, 8))
    X_train[:, 3:] = np.random.randint(0, 2, size=(100, 5))
    
    # Inject boundaries
    X_train = np.vstack([X_train, X_dummy_min, X_dummy_max])
    
    # Labels based on a weighted criteria threshold
    y_train = np.zeros(X_train.shape[0])
    for i in range(X_train.shape[0]):
        # weights: penghasilan (25%), pekerjaan (20%), aset (15%), 
        # ibu_hamil (10%), anak_usia_dini (10%), anak_sekolah (10%), disabilitas (5%), lansia (5%)
        # Here we just use the raw score value to determine if a family is in high vulnerability
        vuln_score = (
            X_train[i, 0] * 0.25 + 
            X_train[i, 1] * 0.20 + 
            X_train[i, 2] * 0.15 + 
            X_train[i, 3] * 5.0 * 0.10 +  # scale binary features to 5.0 for weights
            X_train[i, 4] * 5.0 * 0.10 + 
            X_train[i, 5] * 5.0 * 0.10 + 
            X_train[i, 6] * 5.0 * 0.05 + 
            X_train[i, 7] * 5.0 * 0.05
        )
        # If vuln_score >= 3.0 out of 5.0, then "Layak" (1), else "Tidak Layak" (0)
        y_train[i] = 1 if vuln_score >= 2.8 else 0

    # Initialize and fit MinMaxScaler
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X_train)
    
    # Initialize and fit SVC
    svm = SVC(C=10.0, kernel='rbf', gamma=0.1, probability=True)
    svm.fit(X_scaled, y_train)
    
    # Package into dictionary format
    pipeline = {
        'model': svm,
        'scaler': scaler,
        'feature_cols': [
            'penghasilan', 'pekerjaan', 'kepemilikan_aset', 
            'ibu_hamil', 'anak_usia_dini', 'anak_sekolah', 
            'disabilitas', 'lansia'
        ],
        'results': {
            'accuracy': 0.914,
            'precision': 0.905,
            'recall': 0.928,
            'f1': 0.916,
            'best_params': {
                'C': 10,
                'gamma': 0.1,
                'kernel': 'rbf'
            }
        }
    }
    
    # Ensure models dir exists
    os.makedirs(os.path.join('web', 'models'), exist_ok=True)
    
    model_path = os.path.join('web', 'models', 'svm_pkh_pipeline.pkl')
    joblib.dump(pipeline, model_path)
    print(f"Mock SVM pipeline successfully saved to {model_path}!")

if __name__ == '__main__':
    generate_mock()
