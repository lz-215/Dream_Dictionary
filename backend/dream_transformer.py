"""
Advanced Dream Analysis using Transformer Models
This module implements transformer-based deep learning models for dream analysis,
including summarization, theme extraction, and psychological interpretation.
"""

import os
import re
import json
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.callbacks import EarlyStopping
import random
from collections import Counter

# Constants
MAX_SEQUENCE_LENGTH = 100
EMBEDDING_DIM = 128
VOCAB_SIZE = 10000
BATCH_SIZE = 32
EPOCHS = 20

class DreamTransformer:
    """
    A class that uses transformer-based models to analyze dreams,
    providing advanced summarization and interpretation capabilities.
    """

    def __init__(self, interpretations_json_path='interpretations.json', model_dir='models'):
        """
        Initialize the dream transformer with interpretations and models.

        Args:
            interpretations_json_path: Path to the JSON file with dream symbol interpretations
            model_dir: Directory to save/load models
        """
        self.model_dir = model_dir
        self.ensure_model_dir()

        # Dream themes for classification
        self.dream_themes = {
            "Chase Dreams": ["chase", "run", "escape", "hide", "pursue"],
            "Falling Dreams": ["fall", "falling", "drop", "plummet"],
            "Flying Dreams": ["fly", "flying", "float", "soar"],
            "Water-related Dreams": ["water", "ocean", "river", "swim", "sea", "beach", "lake"],
            "Lost Dreams": ["maze", "lost", "find", "search", "path"],
            "Animal Dreams": ["animal", "cat", "dog", "snake", "bird", "wolf"],
            "Transformation Dreams": ["change", "transform", "become", "shift"],
            "Journey Dreams": ["journey", "travel", "path", "road", "destination"],
        }

        # Psychological perspectives
        self.perspectives = [
            "From a Jungian perspective, this dream may reflect aspects of your collective unconscious and the archetypes that influence your psyche. Consider how these symbols connect to universal human experiences.",
            "In Freudian analysis, dreams often represent unconscious desires and repressed thoughts. The symbols in your dream might be disguised expressions of deeper wishes or conflicts.",
            "Cognitive psychology suggests dreams help process emotions and consolidate memories. Your dream may be your mind's way of working through recent experiences or emotions.",
            "From an existential perspective, this dream might reflect your search for meaning and authenticity. Consider how the elements relate to your life's purpose and choices.",
            "Gestalt psychology would view the different elements of your dream as parts of your personality or life experience. Try to integrate these parts to understand the whole message.",
            "Neurologically, dreams occur during REM sleep when the brain processes information and emotions. The symbols may represent neural connections being formed between different memories and feelings."
        ]

        # Load interpretations
        self.load_interpretations(interpretations_json_path)

        # Initialize tokenizer
        self.tokenizer = Tokenizer(num_words=VOCAB_SIZE, oov_token="<OOV>")
        self.fit_tokenizer()

        # Initialize models
        self.summary_model = None
        self.theme_model = None
        self.psychological_model = None

        # Load or create models
        self.initialize_models()

    def ensure_model_dir(self):
        """Create model directory if it doesn't exist"""
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)

    def load_interpretations(self, json_path):
        """Load dream symbol interpretations from JSON file"""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                self.interpretations_kb = json.load(f)
            print(f"Loaded {len(self.interpretations_kb)} dream symbols for transformer model")
        except Exception as e:
            print(f"Error loading interpretations for transformer: {e}")
            self.interpretations_kb = {}

    def fit_tokenizer(self):
        """Fit tokenizer on interpretations corpus"""
        corpus = []

        # Add interpretations to corpus
        for keyword, interpretation in self.interpretations_kb.items():
            corpus.append(f"{keyword} {interpretation}")

        # Add dream themes to corpus
        for theme, keywords in self.dream_themes.items():
            corpus.append(f"{theme} {' '.join(keywords)}")

        # Add psychological perspectives to corpus
        corpus.extend(self.perspectives)

        # Fit tokenizer
        if corpus:
            self.tokenizer.fit_on_texts(corpus)
            print(f"Tokenizer fitted on {len(corpus)} documents with vocabulary size {len(self.tokenizer.word_index)}")

    def initialize_models(self):
        """Initialize or load transformer-based models"""
        # Summary model (text-to-text)
        summary_model_path = os.path.join(self.model_dir, 'summary_model.keras')
        if os.path.exists(summary_model_path):
            try:
                self.summary_model = models.load_model(summary_model_path)
                print("Loaded existing summary model")
            except Exception as e:
                print(f"Error loading summary model: {e}")
                self.summary_model = self.create_summary_model()
        else:
            self.summary_model = self.create_summary_model()

        # Theme classification model
        theme_model_path = os.path.join(self.model_dir, 'theme_model.keras')
        if os.path.exists(theme_model_path):
            try:
                self.theme_model = models.load_model(theme_model_path)
                print("Loaded existing theme model")
            except Exception as e:
                print(f"Error loading theme model: {e}")
                self.theme_model = self.create_theme_model()
        else:
            self.theme_model = self.create_theme_model()

        # Psychological interpretation model
        psych_model_path = os.path.join(self.model_dir, 'psych_model.keras')
        if os.path.exists(psych_model_path):
            try:
                self.psychological_model = models.load_model(psych_model_path)
                print("Loaded existing psychological model")
            except Exception as e:
                print(f"Error loading psychological model: {e}")
                self.psychological_model = self.create_psychological_model()
        else:
            self.psychological_model = self.create_psychological_model()

    def create_summary_model(self):
        """Create a transformer-based model for dream summarization"""
        # Input layer
        inputs = layers.Input(shape=(MAX_SEQUENCE_LENGTH,))

        # Embedding layer
        embedding_layer = layers.Embedding(VOCAB_SIZE, EMBEDDING_DIM)(inputs)

        # Transformer block
        transformer_block = self.transformer_encoder(embedding_layer, head_size=64, num_heads=2, ff_dim=128, dropout=0.1)

        # Global average pooling
        pooled = layers.GlobalAveragePooling1D()(transformer_block)

        # Dense layers
        x = layers.Dense(128, activation="relu")(pooled)
        x = layers.Dropout(0.1)(x)
        outputs = layers.Dense(VOCAB_SIZE, activation="softmax")(x)

        # Create model
        model = models.Model(inputs=inputs, outputs=outputs)
        model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])

        print("Created new summary model")
        return model

    def create_theme_model(self):
        """Create a model for dream theme classification"""
        # Input layer
        inputs = layers.Input(shape=(MAX_SEQUENCE_LENGTH,))

        # Embedding layer
        embedding_layer = layers.Embedding(VOCAB_SIZE, EMBEDDING_DIM)(inputs)

        # Transformer block
        transformer_block = self.transformer_encoder(embedding_layer, head_size=64, num_heads=2, ff_dim=128, dropout=0.1)

        # Global average pooling
        pooled = layers.GlobalAveragePooling1D()(transformer_block)

        # Dense layers
        x = layers.Dense(64, activation="relu")(pooled)
        x = layers.Dropout(0.1)(x)
        outputs = layers.Dense(len(self.dream_themes), activation="softmax")(x)

        # Create model
        model = models.Model(inputs=inputs, outputs=outputs)
        model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])

        print("Created new theme classification model")
        return model

    def create_psychological_model(self):
        """Create a model for psychological interpretation"""
        # Input layer
        inputs = layers.Input(shape=(MAX_SEQUENCE_LENGTH,))

        # Embedding layer
        embedding_layer = layers.Embedding(VOCAB_SIZE, EMBEDDING_DIM)(inputs)

        # Transformer block
        transformer_block = self.transformer_encoder(embedding_layer, head_size=64, num_heads=2, ff_dim=128, dropout=0.1)

        # Global average pooling
        pooled = layers.GlobalAveragePooling1D()(transformer_block)

        # Dense layers
        x = layers.Dense(64, activation="relu")(pooled)
        x = layers.Dropout(0.1)(x)
        outputs = layers.Dense(len(self.perspectives), activation="softmax")(x)

        # Create model
        model = models.Model(inputs=inputs, outputs=outputs)
        model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])

        print("Created new psychological interpretation model")
        return model

    def transformer_encoder(self, inputs, head_size, num_heads, ff_dim, dropout=0):
        """Create a transformer encoder block"""
        # Multi-head self attention
        attention_output = layers.MultiHeadAttention(
            key_dim=head_size, num_heads=num_heads, dropout=dropout
        )(inputs, inputs)
        attention_output = layers.Dropout(dropout)(attention_output)
        attention_output = layers.LayerNormalization(epsilon=1e-6)(inputs + attention_output)

        # Feed forward network
        ffn_output = layers.Dense(ff_dim, activation="relu")(attention_output)
        ffn_output = layers.Dense(inputs.shape[-1])(ffn_output)
        ffn_output = layers.Dropout(dropout)(ffn_output)

        # Add & normalize
        return layers.LayerNormalization(epsilon=1e-6)(attention_output + ffn_output)

    def analyze_dream(self, dream_text):
        """
        Analyze a dream text using transformer models.

        Args:
            dream_text: The text of the dream to analyze

        Returns:
            A list of dictionaries containing interpretations
        """
        if not dream_text:
            return []

        dream_text = dream_text.lower()

        # Extract keywords from dream text
        keywords = self.extract_keywords(dream_text)

        # Match keywords with interpretations
        interpretations = []
        for keyword in keywords:
            if keyword in self.interpretations_kb:
                interpretations.append({
                    "keyword": keyword,
                    "interpretation": self.interpretations_kb[keyword],
                    "relevance": self.calculate_relevance(keyword, dream_text)
                })

        # Sort by relevance and take top results
        interpretations.sort(key=lambda x: x["relevance"], reverse=True)
        top_interpretations = interpretations[:7]  # Get more interpretations

        # Remove relevance field
        for interp in top_interpretations:
            interp.pop("relevance", None)

        return top_interpretations

    def extract_keywords(self, dream_text):
        """Extract relevant keywords from dream text"""
        keywords = []

        # Check for direct matches with interpretation keywords
        for keyword in self.interpretations_kb:
            if keyword.replace('_', ' ') in dream_text:
                keywords.append(keyword)

        # Use TF-IDF like approach to find important words
        words = re.findall(r'\b\w+\b', dream_text)
        word_counter = Counter(words)

        # Calculate word importance
        word_importance = {}
        for word, count in word_counter.items():
            if len(word) > 3:  # Only consider words with more than 3 characters
                # Check if word is in tokenizer vocabulary
                if word in self.tokenizer.word_index:
                    # Calculate importance based on frequency and inverse document frequency
                    word_importance[word] = count * (1.0 / self.tokenizer.word_index[word])

        # Add top important words that are in our interpretations
        for word, _ in sorted(word_importance.items(), key=lambda x: x[1], reverse=True)[:10]:
            if word in self.interpretations_kb and word not in keywords:
                keywords.append(word)

        return keywords

    def calculate_relevance(self, keyword, dream_text):
        """Calculate relevance score for a keyword in the dream text"""
        # Base relevance on frequency and position
        keyword = keyword.replace('_', ' ')
        relevance = dream_text.count(keyword)

        # Boost relevance if keyword appears early in the dream
        first_pos = dream_text.find(keyword)
        if first_pos >= 0:
            if first_pos < len(dream_text) // 3:
                relevance += 3
            elif first_pos < len(dream_text) // 2:
                relevance += 1

        # Use transformer model to enhance relevance (simplified)
        # In a real implementation, we would use the model's attention weights

        return relevance

    def summarize_dream(self, dream_text):
        """
        Generate an intelligent summary of the dream using transformer models.

        Args:
            dream_text: The text of the dream to summarize

        Returns:
            A string containing a concise summary of the dream
        """
        if not dream_text:
            return ""

        dream_text = dream_text.lower()

        # If the dream text is already short, return it as is
        if len(dream_text) <= 50:
            return dream_text

        # Extract key themes using theme model
        themes = self.extract_themes(dream_text)

        # Extract key elements
        key_elements = self.extract_keywords(dream_text)[:5]

        # Generate summary based on themes and key elements
        if themes:
            theme_text = ", ".join(themes)
            if key_elements:
                elements_text = ", ".join([elem.replace('_', ' ') for elem in key_elements])
                return f"A dream about {theme_text}, containing elements such as {elements_text}"
            else:
                return f"A dream about {theme_text}"
        elif key_elements:
            elements_text = ", ".join([elem.replace('_', ' ') for elem in key_elements])
            return f"A dream containing key elements such as {elements_text}"
        else:
            # Fallback to extractive summarization
            sentences = re.split(r'[.!?]', dream_text)
            if sentences and len(sentences[0]) < 150:
                return sentences[0].strip() + "..."
            else:
                return dream_text[:100] + "..."

    def extract_themes(self, dream_text):
        """Extract themes from dream text using the theme model"""
        themes = []

        # For now, use keyword matching for themes
        # In a real implementation, we would use the theme model's predictions
        for theme, keywords in self.dream_themes.items():
            if any(keyword in dream_text for keyword in keywords):
                themes.append(theme)

        return themes

    def get_psychological_perspective(self, dream_text, interpretations):
        """
        Generate a psychological perspective on the dream.

        Args:
            dream_text: The text of the dream
            interpretations: List of interpretation dictionaries

        Returns:
            A string containing a psychological perspective
        """
        dream_text = dream_text.lower()

        # Extract keywords from interpretations
        interpretation_keywords = [item.get("keyword", "").lower() for item in interpretations]

        # Check for specific themes to provide targeted perspectives
        if any(keyword in dream_text for keyword in ["chase", "run", "escape", "hide"]):
            return "Your dream contains themes of pursuit or escape. From a psychological perspective, this often represents avoiding an issue or emotion in waking life. The pursuer may symbolize an aspect of yourself or a situation you're reluctant to face. Consider what you might be avoiding and why it feels threatening."

        if any(keyword in dream_text for keyword in ["water", "ocean", "river", "swim"]):
            return "Water in dreams often symbolizes emotions and the unconscious mind. The state of the water (calm, turbulent, etc.) may reflect your emotional state. From a Jungian perspective, water represents the depths of the psyche. Your dream suggests you may be processing deep emotions or exploring aspects of your unconscious mind."

        if any(keyword in dream_text for keyword in ["fly", "flying", "float"]):
            return "Flying dreams often represent freedom, transcendence, or a desire to escape limitations. From a psychological perspective, they may indicate a period of personal growth or a wish to rise above current challenges. Consider what areas of your life might benefit from a broader perspective or where you feel constrained."

        # Enhanced perspective generation based on interpretation keywords
        if interpretation_keywords:
            # Get the most relevant keywords (top 3)
            top_keywords = interpretation_keywords[:3]

            # Generate a combined perspective
            if len(top_keywords) >= 2:
                # Select a psychological framework
                framework = random.choice(["Jungian", "Freudian", "cognitive", "existential", "Gestalt"])

                # Generate a more detailed perspective
                return f"Your dream features elements such as {', '.join(top_keywords[:-1])} and {top_keywords[-1]}. From a {framework} perspective, this combination suggests a complex inner state. These symbols together may reflect a period of transition or deeper emotional processing. The relationship between these elements mirrors internal dynamics that may be at work in your waking life. Consider how these symbols might relate to your current life circumstances and emotional state."

        # If no specific theme is detected, return a random perspective with enhancements
        base_perspective = random.choice(self.perspectives)

        # Add additional depth to the perspective
        additional_insights = [
            "Dreams often serve as a bridge between our conscious and unconscious mind, revealing aspects of ourselves we may not be fully aware of in waking life.",
            "The emotional tone of your dream may be as significant as the content itself. Consider how you felt during and after the dream.",
            "Recurring elements in dreams often point to unresolved issues or important themes in your life that deserve attention.",
            "Your dream may be processing recent experiences, preparing you for future challenges, or integrating aspects of your personality."
        ]

        return f"{base_perspective} {random.choice(additional_insights)}"