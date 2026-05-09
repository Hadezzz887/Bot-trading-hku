#!/usr/bin/env python3
"""
Machine learning price prediction module.
"""

import numpy as np
import pandas as pd
import logging
from typing import Tuple, List
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
import pickle
from pathlib import Path

logger = logging.getLogger(__name__)

class PricePredictor:
    """ML-based price prediction model."""
    
    def __init__(self, window_size: int = 20):
        self.window_size = window_size
        self.scaler = MinMaxScaler()
        self.model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        self.is_trained = False
        self.model_path = Path('models/price_predictor.pkl')
    
    def prepare_data(self, prices: List[float]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare data for training."""
        if len(prices) < self.window_size + 1:
            return None, None
        
        prices = np.array(prices).reshape(-1, 1)
        prices_scaled = self.scaler.fit_transform(prices)
        
        X, y = [], []
        for i in range(len(prices_scaled) - self.window_size):
            X.append(prices_scaled[i:i+self.window_size].flatten())
            y.append(prices_scaled[i+self.window_size][0])
        
        return np.array(X), np.array(y)
    
    def train(self, prices: List[float]) -> bool:
        """Train the price prediction model."""
        try:
            X, y = self.prepare_data(prices)
            if X is None:
                logger.warning("Insufficient data for training")
                return False
            
            self.model.fit(X, y)
            self.is_trained = True
            logger.info(f"Price predictor trained on {len(prices)} price points")
            return True
        except Exception as e:
            logger.error(f"Error training price predictor: {e}")
            return False
    
    def predict(self, prices: List[float], steps_ahead: int = 1) -> List[float]:
        """Predict future prices."""
        if not self.is_trained:
            logger.warning("Model not trained yet")
            return []
        
        try:
            prices = np.array(prices[-self.window_size:]).reshape(-1, 1)
            prices_scaled = self.scaler.transform(prices)
            
            predictions = []
            current_seq = prices_scaled.flatten()
            
            for _ in range(steps_ahead):
                pred_scaled = self.model.predict([current_seq])[0]
                predictions.append(self.scaler.inverse_transform([[pred_scaled]])[0][0])
                
                current_seq = np.append(current_seq[1:], pred_scaled)
            
            return predictions
        except Exception as e:
            logger.error(f"Error making price prediction: {e}")
            return []
    
    def get_feature_importance(self) -> dict:
        """Get feature importance from the model."""
        if not self.is_trained:
            return {}
        
        importance = self.model.feature_importances_
        return {
            f"feature_{i}": float(imp) for i, imp in enumerate(importance)
        }
    
    def save_model(self):
        """Save trained model to disk."""
        try:
            self.model_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.model_path, 'wb') as f:
                pickle.dump(self.model, f)
            logger.info(f"Model saved to {self.model_path}")
        except Exception as e:
            logger.error(f"Error saving model: {e}")
    
    def load_model(self) -> bool:
        """Load trained model from disk."""
        try:
            if self.model_path.exists():
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                self.is_trained = True
                logger.info(f"Model loaded from {self.model_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False


if __name__ == "__main__":
    predictor = PricePredictor()
    print("Price predictor initialized")
