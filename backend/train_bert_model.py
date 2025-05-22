"""
Training Script for BERT-based Dream Analysis Models
This script trains the BERT-based models for dream analysis.
"""

import os
import json
import numpy as np
import tensorflow as tf
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import random
from dream_bert import DreamBERT

# Constants
BATCH_SIZE = 16
EPOCHS = 10
VALIDATION_SPLIT = 0.2

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

def generate_synthetic_data(num_samples=100):
    """
    Generate synthetic dream data for training when real data is not available.

    Args:
        num_samples: Number of synthetic samples to generate

    Returns:
        A list of dictionaries containing synthetic dream data
    """
    print(f"Generating {num_samples} synthetic dream samples...")

    # Load interpretations for keywords
    dream_bert = DreamBERT()
    interpretations = dream_bert.interpretations

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
    themes = list(dream_bert.dream_themes.keys())
    
    # Psychological perspectives
    perspectives = dream_bert.perspectives

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

def prepare_data(dream_data, dream_bert):
    """
    Prepare data for training BERT models.

    Args:
        dream_data: List of dream data dictionaries
        dream_bert: DreamBERT instance

    Returns:
        Tuple of (dream_texts, theme_labels, psych_labels)
    """
    print("Preparing data for training...")
    
    # Extract dream texts and labels
    dream_texts = [item["dream_text"] for item in dream_data]
    theme_labels = [item["theme_index"] for item in dream_data]
    psych_labels = [item["psych_index"] for item in dream_data]
    
    return dream_texts, np.array(theme_labels), np.array(psych_labels)

def train_models(dream_bert, dream_data):
    """
    Train the BERT models on dream data.

    Args:
        dream_bert: DreamBERT instance
        dream_data: List of dream data dictionaries
    """
    print(f"Training models on {len(dream_data)} dream samples...")

    # Prepare data
    dream_texts, theme_labels, psych_labels = prepare_data(dream_data, dream_bert)

    # Create callbacks
    early_stopping = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)

    # Train theme model
    print("Training theme classification model...")
    theme_checkpoint = ModelCheckpoint(
        os.path.join(dream_bert.model_dir, 'theme_model'),
        save_best_only=True,
        monitor='val_loss'
    )
    
    dream_bert.theme_model.fit(
        dream_texts, theme_labels,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        validation_split=VALIDATION_SPLIT,
        callbacks=[early_stopping, theme_checkpoint]
    )

    # Train psychological model
    print("Training psychological interpretation model...")
    psych_checkpoint = ModelCheckpoint(
        os.path.join(dream_bert.model_dir, 'psych_model'),
        save_best_only=True,
        monitor='val_loss'
    )
    
    dream_bert.psychological_model.fit(
        dream_texts, psych_labels,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        validation_split=VALIDATION_SPLIT,
        callbacks=[early_stopping, psych_checkpoint]
    )

    print("Model training complete!")

def main():
    """Main function to train the BERT-based dream analysis models"""
    print("Initializing DreamBERT...")
    dream_bert = DreamBERT()

    print("Loading dream data...")
    dream_data = load_dream_data()

    print("Training models...")
    train_models(dream_bert, dream_data)

    print("All models trained successfully!")

if __name__ == "__main__":
    main()
