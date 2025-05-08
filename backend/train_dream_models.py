"""
Training Script for Dream Analysis Models
This script trains the transformer-based models for dream analysis.
"""

import os
import json
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from dream_transformer import DreamTransformer

# Constants
MAX_SEQUENCE_LENGTH = 100
BATCH_SIZE = 32
EPOCHS = 20
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
        A list of dictionaries containing synthetic dream texts and interpretations
    """
    print("Generating synthetic dream data for training...")

    # Load interpretations for vocabulary
    try:
        with open('interpretations.json', 'r', encoding='utf-8') as f:
            interpretations = json.load(f)
    except Exception as e:
        print(f"Error loading interpretations: {e}")
        interpretations = {
            "water": "Symbolizes emotions and the unconscious.",
            "flying": "Represents freedom and transcendence.",
            "falling": "Indicates fear of failure or loss of control.",
            "chase": "Suggests avoiding an issue in waking life.",
            "teeth": "Related to communication and self-image."
        }

    # Dream templates
    templates = [
        "I dreamed I was {action} in a {place} with {object}. I felt {emotion}.",
        "Last night I dreamed about {object} and {object2}. It was {emotion}.",
        "In my dream, I was {action} while {object} appeared. I remember feeling {emotion}.",
        "I had a dream where I was in a {place} and suddenly {action}. There was also {object}.",
        "My dream involved {object} in a {place}. I was {action} and felt {emotion}."
    ]

    # Dream elements
    elements = {
        "action": ["swimming", "flying", "running", "falling", "hiding", "searching", "talking", "watching"],
        "place": ["house", "forest", "ocean", "mountain", "city", "school", "workplace", "unknown location"],
        "object": ["water", "door", "key", "animal", "stranger", "family member", "vehicle", "book"],
        "object2": ["sky", "tree", "mirror", "clock", "food", "computer", "phone", "light"],
        "emotion": ["scared", "happy", "confused", "anxious", "peaceful", "excited", "sad", "surprised"]
    }

    # Generate synthetic dreams
    synthetic_data = []
    for i in range(num_samples):
        # Select a random template
        template = np.random.choice(templates)

        # Fill in the template with random elements
        dream_text = template
        for key, values in elements.items():
            if "{" + key + "}" in dream_text:
                dream_text = dream_text.replace("{" + key + "}", np.random.choice(values))

        # Extract keywords that match our interpretations
        keywords = []
        for keyword in interpretations:
            if keyword in dream_text:
                keywords.append(keyword)

        # If no keywords found, add a random one
        if not keywords:
            random_keyword = np.random.choice(list(interpretations.keys()))
            keywords.append(random_keyword)
            # Add the keyword to the dream text
            dream_text += f" There was also {random_keyword}."

        # Create interpretation
        interpretation = []
        for keyword in keywords:
            interpretation.append({
                "keyword": keyword,
                "interpretation": interpretations.get(keyword, "Symbolizes something in your subconscious.")
            })

        # Add to synthetic data
        synthetic_data.append({
            "dream_text": dream_text,
            "interpretations": interpretation,
            "summary": f"A dream about {', '.join(keywords)}."
        })

    return synthetic_data

def prepare_data(dream_data, transformer):
    """
    Prepare data for training the models.

    Args:
        dream_data: List of dream data dictionaries
        transformer: DreamTransformer instance

    Returns:
        Prepared data for each model
    """
    # Extract texts and labels
    dream_texts = [item["dream_text"].lower() for item in dream_data]
    summaries = [item.get("summary", "") for item in dream_data]

    # Prepare theme data
    theme_labels = []
    for dream in dream_data:
        # Create one-hot encoding for themes
        label = [0] * len(transformer.dream_themes)
        dream_text = dream["dream_text"].lower()

        for i, (theme, keywords) in enumerate(transformer.dream_themes.items()):
            if any(keyword in dream_text for keyword in keywords):
                label[i] = 1

        # If no themes detected, use the first one as default
        if sum(label) == 0:
            label[0] = 1

        theme_labels.append(label)

    # Prepare psychological perspective data
    psych_labels = []
    for dream in dream_data:
        # Create one-hot encoding for psychological perspectives
        label = [0] * len(transformer.perspectives)

        # For synthetic data, just assign a random perspective
        label[np.random.randint(0, len(transformer.perspectives))] = 1

        psych_labels.append(label)

    # Tokenize and pad sequences
    sequences = transformer.tokenizer.texts_to_sequences(dream_texts)
    padded_sequences = pad_sequences(sequences, maxlen=MAX_SEQUENCE_LENGTH, padding='post')

    # Convert labels to numpy arrays
    theme_labels = np.array(theme_labels)
    psych_labels = np.array(psych_labels)

    return padded_sequences, theme_labels, psych_labels

def train_models(transformer, dream_data):
    """
    Train the transformer models on dream data.

    Args:
        transformer: DreamTransformer instance
        dream_data: List of dream data dictionaries
    """
    print(f"Training models on {len(dream_data)} dream samples...")

    # Prepare data
    padded_sequences, theme_labels, psych_labels = prepare_data(dream_data, transformer)

    # Create callbacks
    early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

    # Train theme model
    print("Training theme classification model...")
    theme_checkpoint = ModelCheckpoint(
        os.path.join(transformer.model_dir, 'theme_model.keras'),
        save_best_only=True,
        monitor='val_loss'
    )
    transformer.theme_model.fit(
        padded_sequences, theme_labels,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        validation_split=VALIDATION_SPLIT,
        callbacks=[early_stopping, theme_checkpoint]
    )

    # Train psychological model
    print("Training psychological interpretation model...")
    psych_checkpoint = ModelCheckpoint(
        os.path.join(transformer.model_dir, 'psych_model.keras'),
        save_best_only=True,
        monitor='val_loss'
    )
    transformer.psychological_model.fit(
        padded_sequences, psych_labels,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        validation_split=VALIDATION_SPLIT,
        callbacks=[early_stopping, psych_checkpoint]
    )

    print("Model training complete!")

def main():
    """Main function to train the dream analysis models"""
    print("Initializing Dream Transformer...")
    transformer = DreamTransformer()

    print("Loading dream data...")
    dream_data = load_dream_data()

    print("Training models...")
    train_models(transformer, dream_data)

    print("All models trained successfully!")

if __name__ == "__main__":
    main()
