"""
Advanced ML Models for Energy Monitoring
Includes multiple algorithms and model comparison
"""
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.svm import OneClassSVM
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
from datetime import datetime

class EnsembleEnergyModel:
    """
    Ensemble model combining multiple ML algorithms for robust anomaly detection
    """
    
    def __init__(self, appliance_name):
        self.appliance_name = appliance_name
        self.scaler = StandardScaler()
        
        # Multiple models for ensemble
        self.isolation_forest = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )
        
        self.one_class_svm = OneClassSVM(
            kernel='rbf',
            gamma='auto',
            nu=0.1
        )
        
        self.lof = LocalOutlierFactor(
            n_neighbors=20,
            contamination=0.1,
            novelty=True
        )
        
        self.is_trained = False
        self.training_data = []
        self.feature_importance = {}
        
    def extract_features(self, power, hour, day_of_week, historical_avg=None):
        """
        Extract advanced features for ML model
        """
        features = [
            power,  # Raw power
            hour,  # Hour of day
            day_of_week,  # Day of week
            np.sin(2 * np.pi * hour / 24),  # Cyclical hour (sine)
            np.cos(2 * np.pi * hour / 24),  # Cyclical hour (cosine)
            np.sin(2 * np.pi * day_of_week / 7),  # Cyclical day (sine)
            np.cos(2 * np.pi * day_of_week / 7),  # Cyclical day (cosine)
        ]
        
        # Add historical context if available
        if historical_avg is not None:
            features.extend([
                power / (historical_avg + 1e-6),  # Ratio to average
                power - historical_avg,  # Absolute difference
            ])
        
        return np.array(features).reshape(1, -1)
    
    def train(self, power_data, hours, days_of_week):
        """
        Train all models in the ensemble
        """
        if len(power_data) < 20:
            return False
        
        # Calculate historical average
        historical_avg = np.mean(power_data)
        
        # Extract features for all training data
        X = []
        for power, hour, day in zip(power_data, hours, days_of_week):
            features = self.extract_features(power, hour, day, historical_avg)
            X.append(features.flatten())
        
        X = np.array(X)
        
        # Normalize features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train all models
        self.isolation_forest.fit(X_scaled)
        self.one_class_svm.fit(X_scaled)
        self.lof.fit(X_scaled)
        
        self.is_trained = True
        self.training_data = power_data
        
        # Calculate feature importance (simplified)
        self.feature_importance = {
            'power': 0.4,
            'hour': 0.2,
            'day_of_week': 0.15,
            'cyclical_features': 0.15,
            'historical_context': 0.1
        }
        
        return True
    
    def predict(self, power, hour, day_of_week):
        """
        Predict if reading is anomalous using ensemble voting
        """
        if not self.is_trained:
            return {
                'is_anomaly': False,
                'confidence': 0.0,
                'anomaly_score': 0.0,
                'model_votes': {}
            }
        
        # Calculate historical average
        historical_avg = np.mean(self.training_data)
        
        # Extract features
        features = self.extract_features(power, hour, day_of_week, historical_avg)
        features_scaled = self.scaler.transform(features)
        
        # Get predictions from all models
        if_pred = self.isolation_forest.predict(features_scaled)[0]
        if_score = self.isolation_forest.score_samples(features_scaled)[0]
        
        svm_pred = self.one_class_svm.predict(features_scaled)[0]
        svm_score = self.one_class_svm.decision_function(features_scaled)[0]
        
        lof_pred = self.lof.predict(features_scaled)[0]
        lof_score = self.lof.decision_function(features_scaled)[0]
        
        # Ensemble voting (majority vote)
        votes = [if_pred, svm_pred, lof_pred]
        anomaly_votes = sum(1 for v in votes if v == -1)
        
        is_anomaly = anomaly_votes >= 2  # At least 2 out of 3 models agree
        
        # Calculate confidence (percentage of models agreeing)
        confidence = anomaly_votes / len(votes) if is_anomaly else (len(votes) - anomaly_votes) / len(votes)
        
        # Average anomaly score (normalized)
        avg_score = (if_score + svm_score + lof_score) / 3
        
        return {
            'is_anomaly': is_anomaly,
            'confidence': round(confidence * 100, 1),
            'anomaly_score': round(avg_score, 4),
            'model_votes': {
                'isolation_forest': 'anomaly' if if_pred == -1 else 'normal',
                'one_class_svm': 'anomaly' if svm_pred == -1 else 'normal',
                'local_outlier_factor': 'anomaly' if lof_pred == -1 else 'normal'
            },
            'individual_scores': {
                'isolation_forest': round(if_score, 4),
                'one_class_svm': round(svm_score, 4),
                'local_outlier_factor': round(lof_score, 4)
            }
        }
    
    def evaluate_performance(self, test_data, test_labels):
        """
        Evaluate model performance on test data
        """
        if not self.is_trained:
            return None
        
        predictions = []
        for power, hour, day in test_data:
            result = self.predict(power, hour, day)
            predictions.append(1 if result['is_anomaly'] else 0)
        
        # Calculate metrics
        accuracy = accuracy_score(test_labels, predictions)
        precision = precision_score(test_labels, predictions, zero_division=0)
        recall = recall_score(test_labels, predictions, zero_division=0)
        f1 = f1_score(test_labels, predictions, zero_division=0)
        
        return {
            'accuracy': round(accuracy * 100, 2),
            'precision': round(precision * 100, 2),
            'recall': round(recall * 100, 2),
            'f1_score': round(f1 * 100, 2)
        }
    
    def save_model(self, filename):
        """Save model to disk"""
        if not self.is_trained:
            return False
        
        model_data = {
            'appliance_name': self.appliance_name,
            'isolation_forest': self.isolation_forest,
            'one_class_svm': self.one_class_svm,
            'lof': self.lof,
            'scaler': self.scaler,
            'training_data': self.training_data,
            'feature_importance': self.feature_importance
        }
        
        joblib.dump(model_data, filename)
        return True
    
    def load_model(self, filename):
        """Load model from disk"""
        try:
            model_data = joblib.load(filename)
            self.appliance_name = model_data['appliance_name']
            self.isolation_forest = model_data['isolation_forest']
            self.one_class_svm = model_data['one_class_svm']
            self.lof = model_data['lof']
            self.scaler = model_data['scaler']
            self.training_data = model_data['training_data']
            self.feature_importance = model_data['feature_importance']
            self.is_trained = True
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False

def compare_models(power_data, hours, days, test_power, test_hours, test_days, test_labels):
    """
    Compare performance of different ML models
    """
    results = {}
    
    # Isolation Forest only
    if_model = IsolationForest(contamination=0.1, random_state=42)
    X_train = np.column_stack([power_data, hours, days])
    X_test = np.column_stack([test_power, test_hours, test_days])
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    if_model.fit(X_train_scaled)
    if_pred = if_model.predict(X_test_scaled)
    if_pred_binary = [1 if p == -1 else 0 for p in if_pred]
    
    results['Isolation Forest'] = {
        'accuracy': round(accuracy_score(test_labels, if_pred_binary) * 100, 2),
        'precision': round(precision_score(test_labels, if_pred_binary, zero_division=0) * 100, 2),
        'recall': round(recall_score(test_labels, if_pred_binary, zero_division=0) * 100, 2),
        'f1_score': round(f1_score(test_labels, if_pred_binary, zero_division=0) * 100, 2)
    }
    
    # One-Class SVM
    svm_model = OneClassSVM(kernel='rbf', gamma='auto', nu=0.1)
    svm_model.fit(X_train_scaled)
    svm_pred = svm_model.predict(X_test_scaled)
    svm_pred_binary = [1 if p == -1 else 0 for p in svm_pred]
    
    results['One-Class SVM'] = {
        'accuracy': round(accuracy_score(test_labels, svm_pred_binary) * 100, 2),
        'precision': round(precision_score(test_labels, svm_pred_binary, zero_division=0) * 100, 2),
        'recall': round(recall_score(test_labels, svm_pred_binary, zero_division=0) * 100, 2),
        'f1_score': round(f1_score(test_labels, svm_pred_binary, zero_division=0) * 100, 2)
    }
    
    return results
