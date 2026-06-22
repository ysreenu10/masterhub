
import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from scipy.signal import butter, lfilter
from config import DATASET_PATH, MODEL_PATH, SCALER_PATH

class SimulationEngine:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.states = ['neutral', 'right push', 'right prevtrack', 'right nexttrack', 'right volume up', 'right volumedown', 'right home', 'right think']
        self.left_channels = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        self.right_channels = [16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28]
        
    def butter_bandpass(self, lowcut, highcut, fs, order=4):
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype='band')
        return b, a

    def apply_bandpass_filter(self, data, lowcut=1.0, highcut=45.0, fs=128.0, order=4):
        b, a = self.butter_bandpass(lowcut, highcut, fs, order=order)
        return lfilter(b, a, data, axis=0)

    def extract_features(self, window):
        # Energy (RMS)
        rms = np.sqrt(np.mean(window**2, axis=0))
        
        # Hemispheric Asymmetry
        left_energy = np.mean(rms[self.left_channels])
        right_energy = np.mean(rms[self.right_channels])
        asymmetry = left_energy - right_energy
        
        # Zero Crossing Rate
        zcr = np.mean(np.diff(np.sign(window), axis=0) != 0, axis=0)
        
        return np.concatenate([rms, [asymmetry], zcr])

    def train_model(self):
        if not os.path.exists(DATASET_PATH):
            print(f"Error: Dataset {DATASET_PATH} not found.")
            return False

        print(f"Training model on {DATASET_PATH}...")
        df_raw = pd.read_csv(DATASET_PATH).iloc[:, :32]
        df_raw = df_raw.fillna(df_raw.mean())
        n_samples = len(df_raw)

        # Synthetic labeling as per synaptimesh_ai_pipeline.py
        samples_per_class = n_samples // len(self.states)
        labels = []
        for i in range(len(self.states)):
            labels.extend([i] * samples_per_class)
        while len(labels) < n_samples:
            labels.append(len(self.states) - 1)

        filtered_data = self.apply_bandpass_filter(df_raw.values)

        window_size = 16
        X_features = []
        y_labels = []

        for i in range(0, n_samples - window_size, window_size):
            window = filtered_data[i:i+window_size, :]
            features = self.extract_features(window)
            X_features.append(features)
            y_labels.append(labels[i + window_size // 2])

        X_features = np.array(X_features)
        y_labels = np.array(y_labels)

        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X_features)
        
        self.model = MLPClassifier(
            hidden_layer_sizes=(64, 32),
            activation='relu',
            solver='adam',
            max_iter=1000,
            random_state=42
        )
        self.model.fit(X_scaled, y_labels)

        # Save model and scaler
        joblib.dump(self.model, MODEL_PATH)
        joblib.dump(self.scaler, SCALER_PATH)
        print("Model trained and saved successfully.")
        return True

    def load_model(self):
        if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
            self.model = joblib.load(MODEL_PATH)
            self.scaler = joblib.load(SCALER_PATH)
            if hasattr(self.model, 'classes_') and len(self.model.classes_) != len(self.states):
                print(f"Saved model has {len(self.model.classes_)} classes but expected {len(self.states)}. Retraining required.")
                return False
            return True
        return False

    def predict_from_raw(self, raw_window):
        """
        raw_window: (window_size, 32) numpy array
        """
        if self.model is None or self.scaler is None:
            if not self.load_model():
                self.train_model()
        
        features = self.extract_features(raw_window)
        features_scaled = self.scaler.transform([features])
        probs = self.model.predict_proba(features_scaled)[0]
        prediction_idx = np.argmax(probs)
        confidence = probs[prediction_idx]
        
        return self.states[prediction_idx], confidence

if __name__ == "__main__":
    engine = SimulationEngine()
    engine.train_model()