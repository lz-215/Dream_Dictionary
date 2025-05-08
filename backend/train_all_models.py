"""
Training Script for All Dream Analysis Models
This script trains all available dream analysis models.
"""

import os
import sys
import json
import numpy as np
import tensorflow as tf
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import random
import time

# Set TensorFlow logging level
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # 0=all, 1=info, 2=warning, 3=error

# Import all available models
models_available = {
    'bert': False,
    'transformer': False,
    'deep_learning': False,
    'enhanced': False
}

# Try to import BERT model
try:
    from dream_bert import DreamBERT
    models_available['bert'] = True
    print("✓ BERT model available")
except ImportError as e:
    print(f"✗ BERT model not available: {e}")

# Try to import Transformer model
try:
    from dream_transformer import DreamTransformer
    models_available['transformer'] = True
    print("✓ Transformer model available")
except ImportError as e:
    print(f"✗ Transformer model not available: {e}")

# Try to import Deep Learning model
try:
    from dream_model import DreamInterpreter
    models_available['deep_learning'] = True
    print("✓ Deep Learning model available")
except ImportError as e:
    print(f"✗ Deep Learning model not available: {e}")

# Try to import Enhanced Analyzer
try:
    from dream_analyzer import EnhancedDreamAnalyzer
    models_available['enhanced'] = True
    print("✓ Enhanced Analyzer available")
except ImportError as e:
    print(f"✗ Enhanced Analyzer not available: {e}")

def load_dream_data(data_path='dream_data.json'):
    """
    Load dream data for training.

    Args:
        data_path: Path to the JSON file containing dream data

    Returns:
        A list of dictionaries containing dream texts and their interpretations
    """
    try:
        if os.path.exists(data_path):
            with open(data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print(f"Dream data file {data_path} not found. Using synthetic data.")
            return generate_synthetic_data()
    except Exception as e:
        print(f"Error loading dream data: {e}")
        return generate_synthetic_data()

def generate_synthetic_data(num_samples=200):
    """
    Generate synthetic dream data for training when real data is not available.

    Args:
        num_samples: Number of synthetic samples to generate

    Returns:
        A list of dictionaries containing synthetic dream data
    """
    print(f"Generating {num_samples} synthetic dream samples...")

    # Load interpretations for keywords
    interpretations = {}
    try:
        with open('interpretations.json', 'r', encoding='utf-8') as f:
            interpretations = json.load(f)
    except Exception as e:
        print(f"Error loading interpretations: {e}")
        # Fallback to basic interpretations
        interpretations = {
            "water": "Represents your emotional state or the unconscious mind.",
            "flying": "Symbolizes freedom, transcending limitations, or escaping from something.",
            "falling": "May indicate insecurity, anxiety, or loss of control in your life.",
            "teeth": "Often related to appearance, communication, or anxiety about self-image.",
            "chase": "Suggests you're running from a problem or a fear in your waking life."
        }

    # Elements for synthetic dreams
    elements = {
        "action": ["flying", "falling", "running", "swimming", "hiding", "searching", "fighting", "talking", "dancing", "climbing"],
        "place": ["house", "forest", "ocean", "mountain", "city", "school", "office", "cave", "desert", "garden"],
        "object": ["water", "door", "key", "animal", "car", "book", "phone", "mirror", "stairs", "tree"],
        "object2": ["snake", "teeth", "money", "clock", "bridge", "fire", "cloud", "computer", "flower", "bird"],
        "emotion": ["scared", "happy", "confused", "anxious", "peaceful", "excited", "sad", "angry", "surprised", "curious"]
    }

    # Dream templates
    templates = [
        "I dreamed I was {action} in a {place} with {object}. I felt {emotion}.",
        "Last night I dreamed about {object} and {object2}. It was {emotion}.",
        "In my dream, I was {action} while {object} appeared. I remember feeling {emotion}.",
        "I had a dream where I was in a {place} and suddenly {action}. There was also {object}.",
        "My dream involved {object} in a {place}. I was {action} and felt {emotion}."
    ]

    # Dream themes
    themes = [
        "Chase Dreams", "Falling Dreams", "Flying Dreams", "Water-related Dreams",
        "Lost Dreams", "Animal Dreams", "Transformation Dreams", "Journey Dreams"
    ]
    
    # Psychological perspectives
    perspectives = [
        "Freudian", "Jungian", "Cognitive", "Neurological", 
        "Existential", "Gestalt", "Behavioral", "Transpersonal"
    ]

    # Generate synthetic dreams
    synthetic_data = []
    for i in range(num_samples):
        # Select a random template
        template = random.choice(templates)

        # Fill in the template with random elements
        dream_text = template
        for key, values in elements.items():
            if "{" + key + "}" in dream_text:
                dream_text = dream_text.replace("{" + key + "}", random.choice(values))

        # Extract keywords that match our interpretations
        keywords = []
        for keyword in interpretations:
            if keyword in dream_text:
                keywords.append(keyword)

        # If no keywords found, add a random one
        if not keywords:
            random_keyword = random.choice(list(interpretations.keys()))
            keywords.append(random_keyword)
            # Add the keyword to the dream text
            dream_text += f" There was also {random_keyword}."

        # Create interpretations for the keywords
        dream_interpretations = []
        for keyword in keywords:
            dream_interpretations.append({
                "keyword": keyword,
                "interpretation": interpretations[keyword]
            })

        # Assign a random theme
        theme_index = random.randint(0, len(themes) - 1)
        
        # Assign a random psychological perspective
        psych_index = random.randint(0, len(perspectives) - 1)

        # Create a synthetic dream data entry
        synthetic_data.append({
            "dream_text": dream_text,
            "interpretations": dream_interpretations,
            "theme_index": theme_index,
            "theme": themes[theme_index],
            "psych_index": psych_index,
            "perspective": perspectives[psych_index]
        })

    print(f"Generated {len(synthetic_data)} synthetic dream samples.")
    return synthetic_data

def train_bert_model(dream_data):
    """Train the BERT model if available"""
    if not models_available['bert']:
        print("BERT model not available for training.")
        return
    
    print("\n=== Training BERT Model ===")
    try:
        from train_bert_model import train_models
        
        # Initialize BERT model
        from dream_bert import DreamBERT
        bert_model = DreamBERT()
        
        # Train the model
        train_models(bert_model, dream_data)
        
        print("BERT model training completed successfully!")
    except Exception as e:
        print(f"Error training BERT model: {e}")

def train_transformer_model(dream_data):
    """Train the Transformer model if available"""
    if not models_available['transformer']:
        print("Transformer model not available for training.")
        return
    
    print("\n=== Training Transformer Model ===")
    try:
        from train_dream_models import train_models
        
        # Initialize Transformer model
        from dream_transformer import DreamTransformer
        transformer_model = DreamTransformer()
        
        # Train the model
        train_models(transformer_model, dream_data)
        
        print("Transformer model training completed successfully!")
    except Exception as e:
        print(f"Error training Transformer model: {e}")

def main():
    """Main function to train all available models"""
    print("=== Dream Analysis Models Training ===")
    
    # Check if any models are available
    if not any(models_available.values()):
        print("No models available for training. Please install the required dependencies.")
        return
    
    # Load dream data
    print("\nLoading dream data...")
    dream_data = load_dream_data()
    
    # Train BERT model
    train_bert_model(dream_data)
    
    # Train Transformer model
    train_transformer_model(dream_data)
    
    print("\n=== All Training Completed ===")

if __name__ == "__main__":
    main()
