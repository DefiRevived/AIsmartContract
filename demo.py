#!/usr/bin/env python3
"""
Quick start script for AI Smart Contract Demo
This script demonstrates the basic functionality of the AI model components.
"""

import numpy as np
import json
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_sample_data():
    """Generate sample training data for demonstration"""
    logger.info("Generating sample training data...")
    
    # Generate synthetic data for a simple prediction task
    np.random.seed(42)
    n_samples = 1000
    
    # Features: price, volume, volatility
    X = np.random.rand(n_samples, 3)
    X[:, 0] = X[:, 0] * 100  # Price: 0-100
    X[:, 1] = X[:, 1] * 1000  # Volume: 0-1000
    X[:, 2] = X[:, 2] * 10    # Volatility: 0-10
    
    # Target: Simple rule - high volume + low volatility = buy signal (1), else sell signal (0)
    y = ((X[:, 1] > 500) & (X[:, 2] < 5)).astype(int)
    
    return X, y

def train_demo_model():
    """Train a simple demo model"""
    try:
        from src.ai.model import AIModel
        
        logger.info("Creating and training AI model...")
        
        # Generate sample data
        X, y = create_sample_data()
        
        # Split into train/test
        train_size = int(0.8 * len(X))
        X_train, X_test = X[:train_size], X[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]
        
        # Create and train model
        model = AIModel(input_dim=3, output_dim=1, model_type='classification')
        
        logger.info("Training model...")
        history = model.train(X_train, y_train, X_test, y_test, epochs=50, batch_size=32)
        
        # Evaluate model
        loss, accuracy = model.evaluate_model(X_test, y_test)
        logger.info(f"Model trained! Test Accuracy: {accuracy:.3f}")
        
        # Save model
        model_dir = Path("models")
        model_dir.mkdir(exist_ok=True)
        
        model_path = model_dir / "demo_model.h5"
        model.save_model(str(model_path))
        logger.info(f"Model saved to {model_path}")
        
        # Test prediction with confidence
        sample_input = [[50.0, 750.0, 3.0]]  # High volume, low volatility
        prediction, confidence = model.predict_with_confidence(np.array(sample_input))
        
        logger.info(f"Sample prediction: {prediction[0]:.3f} (confidence: {confidence[0]:.1f}%)")
        
        return model_path
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.error("Please make sure TensorFlow is installed: pip install tensorflow")
        return None
    except Exception as e:
        logger.error(f"Error training model: {e}")
        return None

def demo_inference():
    """Demonstrate the inference module"""
    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import train_test_split
        import joblib
        
        logger.info("Creating sklearn demo model for inference...")
        
        # Generate sample data
        X, y = create_sample_data()
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train a simple sklearn model
        rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        rf_model.fit(X_train, y_train)
        
        # Save the model
        model_dir = Path("models")
        model_dir.mkdir(exist_ok=True)
        
        model_path = model_dir / "sklearn_demo_model.pkl"
        joblib.dump(rf_model, model_path)
        logger.info(f"Sklearn model saved to {model_path}")
        
        # Test inference module
        from src.ai.inference import InferenceModel
        
        inference = InferenceModel(str(model_path), model_type='sklearn')
        
        # Test prediction
        sample_inputs = [
            [50.0, 750.0, 3.0],  # Should predict buy (1)
            [30.0, 200.0, 8.0],  # Should predict sell (0)
            [80.0, 900.0, 2.0],  # Should predict buy (1)
        ]
        
        logger.info("Testing inference predictions:")
        for i, input_data in enumerate(sample_inputs):
            prediction, confidence = inference.predict_with_confidence(input_data)
            signal = "BUY" if prediction[0] > 0.5 else "SELL"
            logger.info(f"Sample {i+1}: {input_data} -> {signal} (confidence: {confidence:.1f}%)")
        
        # Test batch prediction
        batch_results = inference.batch_predict(sample_inputs)
        logger.info("Batch prediction results:")
        for i, (pred, conf) in enumerate(batch_results):
            signal = "BUY" if pred[0] > 0.5 else "SELL"
            logger.info(f"  Batch {i+1}: {signal} (confidence: {conf:.1f}%)")
        
        # Show model stats
        stats = inference.get_model_stats()
        logger.info(f"Model statistics: {stats}")
        
        return model_path
        
    except Exception as e:
        logger.error(f"Error in inference demo: {e}")
        return None

def main():
    """Main demo function"""
    logger.info("=== AI Smart Contract Demo ===")
    
    # Create models directory
    Path("models").mkdir(exist_ok=True)
    
    logger.info("\n1. Training TensorFlow/Keras Model...")
    tf_model_path = train_demo_model()
    
    logger.info("\n2. Training Sklearn Model and Testing Inference...")
    sklearn_model_path = demo_inference()
    
    if tf_model_path or sklearn_model_path:
        logger.info("\n✅ Demo completed successfully!")
        logger.info("\nNext steps:")
        logger.info("1. Update config.json with your blockchain settings")
        logger.info("2. Set up environment variables in .env file")
        logger.info("3. Deploy smart contracts using the deployment scripts")
        logger.info("4. Run the oracle bridge service")
        
        if sklearn_model_path:
            logger.info(f"\n🤖 You can use the sklearn model at: {sklearn_model_path}")
            logger.info("Update config.json to point to this model for testing")
    else:
        logger.error("\n❌ Demo failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
