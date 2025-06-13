import joblib
import numpy as np
import json
import logging
from typing import Dict, List, Tuple, Any
from datetime import datetime
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InferenceModel:
    def __init__(self, model_path: str, model_type: str = 'sklearn'):
        self.model_path = model_path
        self.model_type = model_type
        self.model = self.load_model(model_path)
        self.prediction_cache = {}
        self.request_history = []
        
    def load_model(self, model_path: str):
        """Load model based on type"""
        try:
            if self.model_type == 'sklearn':
                return joblib.load(model_path)
            elif self.model_type == 'tensorflow':
                from tensorflow.keras.models import load_model
                return load_model(model_path)
            else:
                raise ValueError(f"Unsupported model type: {self.model_type}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

    def preprocess_input(self, input_data: List[float]) -> np.ndarray:
        """Preprocess input data for prediction"""
        try:
            # Convert to numpy array and reshape
            input_array = np.array(input_data, dtype=np.float32)
            if input_array.ndim == 1:
                input_array = input_array.reshape(1, -1)
            
            # Basic validation
            if np.any(np.isnan(input_array)) or np.any(np.isinf(input_array)):
                raise ValueError("Input contains NaN or infinite values")
                
            return input_array
        except Exception as e:
            logger.error(f"Input preprocessing failed: {e}")
            raise

    def predict_with_confidence(self, input_data: List[float]) -> Tuple[List[float], float]:
        """Make prediction with confidence score"""
        try:
            # Create cache key
            cache_key = hashlib.md5(str(input_data).encode()).hexdigest()
            
            # Check cache first
            if cache_key in self.prediction_cache:
                logger.info("Returning cached prediction")
                return self.prediction_cache[cache_key]
            
            # Preprocess input
            processed_input = self.preprocess_input(input_data)
            
            # Make prediction
            if self.model_type == 'sklearn':
                prediction = self.model.predict(processed_input)
                
                # Calculate confidence for sklearn models
                if hasattr(self.model, 'predict_proba'):
                    probabilities = self.model.predict_proba(processed_input)
                    confidence = float(np.max(probabilities) * 100)
                else:
                    confidence = 85.0  # Default confidence for regression
                    
            elif self.model_type == 'tensorflow':
                prediction = self.model.predict(processed_input)
                
                # Calculate confidence for neural networks
                if prediction.shape[1] > 1:  # Classification
                    confidence = float(np.max(prediction) * 100)
                else:  # Regression
                    confidence = 90.0  # Default confidence
            
            # Convert prediction to list
            prediction_list = prediction.flatten().tolist()
            
            # Cache the result
            result = (prediction_list, confidence)
            self.prediction_cache[cache_key] = result
            
            # Log the prediction
            self._log_prediction(input_data, prediction_list, confidence)
            
            return result
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise

    def predict(self, input_data: List[float]) -> List[float]:
        """Simple prediction without confidence (backward compatibility)"""
        prediction, _ = self.predict_with_confidence(input_data)
        return prediction

    def batch_predict(self, input_batch: List[List[float]]) -> List[Tuple[List[float], float]]:
        """Make predictions for a batch of inputs"""
        results = []
        for input_data in input_batch:
            try:
                result = self.predict_with_confidence(input_data)
                results.append(result)
            except Exception as e:
                logger.error(f"Batch prediction failed for input {input_data}: {e}")
                results.append(([], 0.0))
        return results

    def _log_prediction(self, input_data: List[float], prediction: List[float], confidence: float):
        """Log prediction for audit trail"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'input': input_data,
            'prediction': prediction,
            'confidence': confidence,
            'model_path': self.model_path
        }
        self.request_history.append(log_entry)
        
        # Keep only last 1000 entries
        if len(self.request_history) > 1000:
            self.request_history = self.request_history[-1000:]

    def get_model_stats(self) -> Dict[str, Any]:
        """Get model statistics"""
        return {
            'model_path': self.model_path,
            'model_type': self.model_type,
            'cache_size': len(self.prediction_cache),
            'total_predictions': len(self.request_history),
            'avg_confidence': np.mean([entry['confidence'] for entry in self.request_history]) if self.request_history else 0
        }

    def clear_cache(self):
        """Clear prediction cache"""
        self.prediction_cache.clear()
        logger.info("Prediction cache cleared")

    def export_history(self, filename: str):
        """Export prediction history to JSON file"""
        try:
            with open(filename, 'w') as f:
                json.dump(self.request_history, f, indent=2)
            logger.info(f"Prediction history exported to {filename}")
        except Exception as e:
            logger.error(f"Failed to export history: {e}")

class ModelValidator:
    """Utility class for validating model predictions"""
    
    @staticmethod
    def validate_prediction_format(prediction: List[float], expected_length: int) -> bool:
        """Validate prediction format"""
        if not isinstance(prediction, list):
            return False
        if len(prediction) != expected_length:
            return False
        if not all(isinstance(x, (int, float)) for x in prediction):
            return False
        return True
    
    @staticmethod
    def validate_confidence_score(confidence: float) -> bool:
        """Validate confidence score"""
        return isinstance(confidence, (int, float)) and 0 <= confidence <= 100