import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.optimizers import Adam
import numpy as np
import joblib
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIModel:
    def __init__(self, input_dim, output_dim, model_type='classification'):
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.model_type = model_type
        self.model = self._build_model()
        self.is_trained = False
        self.version = "1.0.0"
        
    def _build_model(self):
        """Build the neural network architecture"""
        model = Sequential([
            Dense(128, input_dim=self.input_dim, activation='relu'),
            BatchNormalization(),
            Dropout(0.3),
            
            Dense(64, activation='relu'),
            BatchNormalization(),
            Dropout(0.2),
            
            Dense(32, activation='relu'),
            Dropout(0.1),
            
            Dense(self.output_dim, activation='sigmoid' if self.model_type == 'classification' else 'linear')
        ])
        
        optimizer = Adam(learning_rate=0.001)
        loss = 'binary_crossentropy' if self.model_type == 'classification' else 'mse'
        metrics = ['accuracy'] if self.model_type == 'classification' else ['mae']
        
        model.compile(optimizer=optimizer, loss=loss, metrics=metrics)
        return model

    def train(self, X_train, y_train, X_val=None, y_val=None, epochs=100, batch_size=32):
        """Train the model with validation and callbacks"""
        logger.info(f"Starting training for {epochs} epochs...")
        
        callbacks = [
            ModelCheckpoint('best_model.h5', save_best_only=True, monitor='val_loss'),
            EarlyStopping(patience=10, restore_best_weights=True),
            ReduceLROnPlateau(factor=0.5, patience=5, min_lr=1e-7)
        ]
        
        validation_data = (X_val, y_val) if X_val is not None else None
        
        history = self.model.fit(
            X_train, y_train,
            validation_data=validation_data,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1
        )
        
        self.is_trained = True
        logger.info("Training completed successfully!")
        return history

    def predict_with_confidence(self, X):
        """Make prediction with confidence score"""
        if not self.is_trained:
            logger.warning("Model not trained yet!")
            
        predictions = self.model.predict(X)
        
        # Calculate confidence based on prediction probability
        if self.model_type == 'classification':
            confidence = np.max(predictions, axis=1) * 100
        else:
            # For regression, use inverse of prediction variance as confidence
            confidence = np.ones(len(predictions)) * 85  # Placeholder
            
        return predictions, confidence

    def evaluate_model(self, X_test, y_test):
        """Evaluate model performance"""
        if not self.is_trained:
            raise ValueError("Model must be trained before evaluation")
            
        loss, metric = self.model.evaluate(X_test, y_test, verbose=0)
        logger.info(f"Test Loss: {loss:.4f}, Test Metric: {metric:.4f}")
        return loss, metric

    def save_model(self, filepath):
        """Save the trained model"""
        self.model.save(filepath)
        
        # Save metadata
        metadata = {
            'input_dim': self.input_dim,
            'output_dim': self.output_dim,
            'model_type': self.model_type,
            'is_trained': self.is_trained,
            'version': self.version
        }
        joblib.dump(metadata, f"{filepath}_metadata.pkl")
        logger.info(f"Model saved to {filepath}")

    def load_model(self, filepath):
        """Load a pre-trained model"""
        self.model = load_model(filepath)
        
        # Load metadata
        try:
            metadata = joblib.load(f"{filepath}_metadata.pkl")
            self.input_dim = metadata['input_dim']
            self.output_dim = metadata['output_dim']
            self.model_type = metadata['model_type']
            self.is_trained = metadata['is_trained']
            self.version = metadata['version']
        except FileNotFoundError:
            logger.warning("Metadata file not found, using defaults")
            
        logger.info(f"Model loaded from {filepath}")

    def get_model_info(self):
        """Get model information"""
        return {
            'version': self.version,
            'input_dim': self.input_dim,
            'output_dim': self.output_dim,
            'model_type': self.model_type,
            'is_trained': self.is_trained,
            'parameters': self.model.count_params()
        }