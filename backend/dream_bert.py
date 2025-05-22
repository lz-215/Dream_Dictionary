"""
BERT-based Dream Analysis Model
This module implements a BERT-based transformer architecture for dream analysis,
providing advanced natural language understanding for dream interpretation.
"""

import os
import re
import json
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
import tensorflow_hub as hub
import tensorflow_text as text
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import random
from collections import Counter

# Constants
MAX_SEQUENCE_LENGTH = 128
BATCH_SIZE = 16
EPOCHS = 10
MODEL_DIR = 'models/bert'

class DreamBERT:
    """
    A class that uses BERT-based transformer models to analyze dreams,
    providing advanced natural language understanding and interpretation.
    """

    def __init__(self, interpretations_json_path='interpretations.json'):
        """
        Initialize the BERT-based dream analyzer with interpretations and models.

        Args:
            interpretations_json_path: Path to the JSON file with dream symbol interpretations
        """
        self.model_dir = MODEL_DIR
        self.ensure_model_dir()

        # Load interpretations
        self.interpretations = self.load_interpretations(interpretations_json_path)

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
            "Freudian", "Jungian", "Cognitive", "Neurological",
            "Existential", "Gestalt", "Behavioral", "Transpersonal"
        ]

        # Initialize models
        self.theme_model = self.load_or_create_theme_model()
        self.psychological_model = self.load_or_create_psychological_model()
        self.bert_preprocessor = None
        self.bert_encoder = None

        # Initialize BERT components
        self.initialize_bert()

        print("BERT-based Dream Analyzer initialized")

    def ensure_model_dir(self):
        """Create model directory if it doesn't exist"""
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)
            print(f"Created model directory: {self.model_dir}")

    def load_interpretations(self, json_path):
        """Load dream symbol interpretations from JSON file"""
        try:
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print(f"Interpretations file {json_path} not found. Using default interpretations.")
                return self.get_default_interpretations()
        except Exception as e:
            print(f"Error loading interpretations: {e}")
            return self.get_default_interpretations()

    def get_default_interpretations(self):
        """Return default interpretations when JSON file is not available"""
        return {
            "water": "Represents your emotional state or the unconscious mind.",
            "flying": "Symbolizes freedom, transcending limitations, or escaping from something.",
            "falling": "May indicate insecurity, anxiety, or loss of control in your life.",
            "teeth": "Often related to appearance, communication, or anxiety about self-image.",
            "chase": "Suggests you're running from a problem or a fear in your waking life.",
            "house": "Represents the self, with different rooms symbolizing different aspects of your personality.",
            "death": "Usually symbolizes transformation, change, or the end of a phase rather than literal death.",
            "naked": "Can indicate vulnerability, exposure, or fear of being revealed.",
            "test": "Reflects feelings of being tested or evaluated in your waking life.",
            "money": "Symbolizes self-worth, power, or how you value yourself."
        }

    def initialize_bert(self):
        """Initialize BERT preprocessor and encoder"""
        try:
            # Load BERT preprocessor and encoder from TensorFlow Hub
            bert_model_name = 'small_bert/bert_en_uncased_L-4_H-512_A-8'
            map_name_to_handle = {
                'small_bert/bert_en_uncased_L-4_H-512_A-8': 'https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-4_H-512_A-8/1',
            }
            map_model_to_preprocess = {
                'small_bert/bert_en_uncased_L-4_H-512_A-8': 'https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3',
            }

            tfhub_handle_encoder = map_name_to_handle[bert_model_name]
            tfhub_handle_preprocess = map_model_to_preprocess[bert_model_name]

            print(f'BERT model selected: {tfhub_handle_encoder}')
            print(f'Preprocessing model: {tfhub_handle_preprocess}')

            # Load BERT preprocessor
            self.bert_preprocessor = hub.load(tfhub_handle_preprocess)
            # Load BERT encoder
            self.bert_encoder = hub.load(tfhub_handle_encoder)

            print("BERT components loaded successfully")
        except Exception as e:
            print(f"Error initializing BERT components: {e}")
            self.bert_preprocessor = None
            self.bert_encoder = None

    def load_or_create_theme_model(self):
        """Load existing theme model or create a new one"""
        model_path = os.path.join(self.model_dir, 'theme_model')

        if os.path.exists(model_path):
            try:
                model = tf.keras.models.load_model(model_path)
                print("Loaded existing theme model")
                return model
            except Exception as e:
                print(f"Error loading theme model: {e}")
                print("Creating new theme model")

        return self.create_theme_model()

    def load_or_create_psychological_model(self):
        """Load existing psychological model or create a new one"""
        model_path = os.path.join(self.model_dir, 'psych_model')

        if os.path.exists(model_path):
            try:
                model = tf.keras.models.load_model(model_path)
                print("Loaded existing psychological model")
                return model
            except Exception as e:
                print(f"Error loading psychological model: {e}")
                print("Creating new psychological model")

        return self.create_psychological_model()

    def create_theme_model(self):
        """Create a BERT-based model for dream theme classification"""
        # Input layer for text
        text_input = tf.keras.layers.Input(shape=(), dtype=tf.string, name='text')

        # Use the BERT preprocessor and encoder if available
        if self.bert_preprocessor and self.bert_encoder:
            preprocessed_text = self.bert_preprocessor(text_input)
            encoder_outputs = self.bert_encoder(preprocessed_text)

            # Use the pooled output for classification
            pooled_output = encoder_outputs['pooled_output']

            # Add dropout and output layer
            x = tf.keras.layers.Dropout(0.1)(pooled_output)
            x = tf.keras.layers.Dense(64, activation='relu')(x)
            x = tf.keras.layers.Dropout(0.1)(x)
            outputs = tf.keras.layers.Dense(len(self.dream_themes), activation='softmax')(x)

            # Create model
            model = tf.keras.Model(inputs=text_input, outputs=outputs)
            model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

            print("Created new BERT-based theme model")
            return model
        else:
            # Fallback to a simpler model if BERT is not available
            print("BERT not available, creating simplified theme model")
            return self.create_simplified_model(len(self.dream_themes))

    def create_psychological_model(self):
        """Create a BERT-based model for psychological interpretation"""
        # Input layer for text
        text_input = tf.keras.layers.Input(shape=(), dtype=tf.string, name='text')

        # Use the BERT preprocessor and encoder if available
        if self.bert_preprocessor and self.bert_encoder:
            preprocessed_text = self.bert_preprocessor(text_input)
            encoder_outputs = self.bert_encoder(preprocessed_text)

            # Use the pooled output for classification
            pooled_output = encoder_outputs['pooled_output']

            # Add dropout and output layer
            x = tf.keras.layers.Dropout(0.1)(pooled_output)
            x = tf.keras.layers.Dense(64, activation='relu')(x)
            x = tf.keras.layers.Dropout(0.1)(x)
            outputs = tf.keras.layers.Dense(len(self.perspectives), activation='softmax')(x)

            # Create model
            model = tf.keras.Model(inputs=text_input, outputs=outputs)
            model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

            print("Created new BERT-based psychological model")
            return model
        else:
            # Fallback to a simpler model if BERT is not available
            print("BERT not available, creating simplified psychological model")
            return self.create_simplified_model(len(self.perspectives))

    def create_simplified_model(self, num_classes):
        """Create a simplified model when BERT is not available"""
        model = models.Sequential([
            layers.Input(shape=(1,), dtype=tf.string),
            layers.Lambda(lambda x: tf.strings.lower(x)),
            layers.Lambda(lambda x: tf.strings.regex_replace(x, r'[^\w\s]', '')),
            layers.TextVectorization(max_tokens=10000, output_sequence_length=MAX_SEQUENCE_LENGTH),
            layers.Embedding(10000, 128),
            layers.Bidirectional(layers.LSTM(64, return_sequences=True)),
            layers.GlobalAveragePooling1D(),
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(num_classes, activation='softmax')
        ])
        model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        return model

    def analyze_dream(self, dream_text):
        """
        Analyze a dream text using BERT-based models.

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

        # Get interpretations for the keywords
        interpretations = []
        for keyword in keywords:
            if keyword in self.interpretations:
                interpretations.append({
                    'keyword': keyword,
                    'interpretation': self.interpretations[keyword]
                })

        # If no interpretations found, use BERT to find semantic matches
        if not interpretations:
            interpretations = self.find_semantic_matches(dream_text)

        return interpretations

    def extract_keywords(self, dream_text):
        """Extract important keywords from dream text"""
        # Simple keyword extraction based on interpretations dictionary
        keywords = []
        for keyword in self.interpretations.keys():
            if keyword in dream_text:
                keywords.append(keyword)

        # Use regex to find whole words only
        refined_keywords = []
        for keyword in keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', dream_text):
                refined_keywords.append(keyword)

        return refined_keywords

    def find_semantic_matches(self, dream_text):
        """Find semantic matches using BERT embeddings"""
        if not self.bert_preprocessor or not self.bert_encoder:
            return []

        try:
            # Get BERT embedding for dream text
            dream_embedding = self.get_bert_embedding(dream_text)

            # Compare with embeddings of all keywords
            matches = []
            for keyword, interpretation in self.interpretations.items():
                keyword_embedding = self.get_bert_embedding(keyword + " " + interpretation)

                # Calculate cosine similarity
                similarity = self.cosine_similarity(dream_embedding, keyword_embedding)

                if similarity > 0.5:  # Threshold for semantic similarity
                    matches.append({
                        'keyword': keyword,
                        'interpretation': interpretation,
                        'similarity': float(similarity)
                    })

            # Sort by similarity and take top 5
            matches.sort(key=lambda x: x['similarity'], reverse=True)
            return matches[:5]
        except Exception as e:
            print(f"Error in semantic matching: {e}")
            return []

    def get_bert_embedding(self, text):
        """Get BERT embedding for text"""
        # Preprocess the text
        preprocessed = self.bert_preprocessor([text])
        # Get the embedding from the BERT encoder
        outputs = self.bert_encoder(preprocessed)
        # Use the pooled output as the embedding
        return outputs['pooled_output'][0]

    def cosine_similarity(self, a, b):
        """Calculate cosine similarity between two vectors"""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def extract_themes(self, dream_text):
        """Extract themes from dream text using the theme model"""
        if not self.theme_model:
            return []

        try:
            # Predict theme probabilities
            probs = self.theme_model.predict([dream_text], verbose=0)[0]

            # Get top themes
            top_indices = np.argsort(probs)[-3:][::-1]  # Top 3 themes
            themes = list(self.dream_themes.keys())

            return [
                {'theme': themes[i], 'probability': float(probs[i])}
                for i in top_indices if probs[i] > 0.2  # Only include themes with probability > 20%
            ]
        except Exception as e:
            print(f"Error extracting themes: {e}")
            return []

    def get_psychological_perspective(self, dream_text, interpretations):
        """Generate psychological perspective based on dream text and interpretations"""
        if not self.psychological_model:
            return self.generate_default_perspective(dream_text, interpretations)

        try:
            # Predict perspective probabilities
            probs = self.psychological_model.predict([dream_text], verbose=0)[0]

            # Get top perspective
            top_index = np.argmax(probs)
            perspective = self.perspectives[top_index]

            # Generate perspective text based on the predicted perspective
            return self.generate_perspective_text(perspective, dream_text, interpretations)
        except Exception as e:
            print(f"Error generating psychological perspective: {e}")
            return self.generate_default_perspective(dream_text, interpretations)

    def generate_perspective_text(self, perspective, dream_text, interpretations):
        """Generate perspective text based on the psychological perspective"""
        # Extract keywords from interpretations
        keywords = [item['keyword'] for item in interpretations]
        keywords_str = ", ".join(keywords) if keywords else "the elements in your dream"

        perspectives = {
            "Freudian": f"From a Freudian perspective, {keywords_str} in your dream may represent unconscious desires or repressed thoughts. The dream could be expressing wishes or conflicts that you're not fully aware of in your waking life.",

            "Jungian": f"A Jungian analysis suggests that {keywords_str} may represent archetypes from the collective unconscious. Your dream appears to be bringing forward symbolic content that connects to universal human experiences and may be guiding you toward greater self-awareness and integration.",

            "Cognitive": f"From a cognitive perspective, your dream about {keywords_str} likely reflects your mind processing information and experiences from your waking life. The dream may be helping you to organize memories, solve problems, or process emotions.",

            "Neurological": f"Neurologically speaking, this dream featuring {keywords_str} is likely the result of your brain's activity during sleep. The imagery may not have inherent meaning but rather represents neural networks activating in patterns that create these dream experiences.",

            "Existential": f"An existential interpretation would suggest that your dream about {keywords_str} reflects deeper questions about meaning, purpose, or authenticity in your life. The dream may be inviting you to consider how you're engaging with fundamental aspects of human existence.",

            "Gestalt": f"From a Gestalt perspective, each element in your dream ({keywords_str}) represents different aspects of yourself. The dream is inviting you to integrate these parts into a more complete whole, recognizing that you are greater than the sum of these individual elements.",

            "Behavioral": f"A behavioral interpretation suggests that your dream about {keywords_str} may be connected to recent experiences that have triggered certain responses or conditioning. The dream might be processing learned associations or reinforcing behavioral patterns.",

            "Transpersonal": f"From a transpersonal perspective, your dream featuring {keywords_str} may be connecting you to something beyond your individual self - perhaps collective consciousness, spiritual dimensions, or transcendent experiences that expand your sense of identity."
        }

        return perspectives.get(perspective, self.generate_default_perspective(dream_text, interpretations))

    def generate_default_perspective(self, dream_text, interpretations):
        """Generate a default psychological perspective when model is not available"""
        # Extract keywords from interpretations
        keywords = [item['keyword'] for item in interpretations]
        keywords_str = ", ".join(keywords) if keywords else "the elements in your dream"

        return f"Your dream about {keywords_str} appears to blend several psychological perspectives. It may reflect both unconscious processes and your mind's attempt to process daily experiences. Consider how these dream symbols relate to your current life circumstances and emotional state."

    def summarize_dream(self, dream_text):
        """Generate a summary of the dream using BERT"""
        if not dream_text:
            return ""

        # If the dream text is already short, return it as is
        if len(dream_text) <= 50:
            return dream_text

        # Extract themes
        themes = self.extract_themes(dream_text)
        theme_names = [t['theme'] for t in themes]

        # Extract keywords
        keywords = self.extract_keywords(dream_text)

        # Create a summary based on themes and keywords
        if theme_names and keywords:
            theme_str = " and ".join(theme_names[:2])
            keyword_str = ", ".join(keywords[:3])
            return f"A {theme_str.lower()} dream involving {keyword_str}."
        elif theme_names:
            theme_str = " and ".join(theme_names[:2])
            return f"A {theme_str.lower()} dream."
        elif keywords:
            keyword_str = ", ".join(keywords[:3])
            return f"A dream featuring {keyword_str}."
        else:
            # Extract sentences and return the first one as a summary
            sentences = re.split(r'[.!?]+', dream_text)
            return sentences[0].strip() + "."