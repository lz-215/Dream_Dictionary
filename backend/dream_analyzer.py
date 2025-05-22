"""
Enhanced Dream Analysis Module
This module provides more sophisticated dream analysis functionality
with deeper interpretations and multi-layered analysis.
"""

import re
import json
import random
from collections import Counter
import logging
import functools
import os

# Configure logging
logger = logging.getLogger(__name__)

class EnhancedDreamAnalyzer:
    """
    Enhanced dream analyzer that provides deeper and more comprehensive
    dream interpretations based on the dream text.
    """

    def __init__(self, interpretations_json_path='interpretations.json'):
        """
        Initialize the dream analyzer with the interpretations knowledge base.
        
        Args:
            interpretations_json_path: Path to the JSON file with dream symbol interpretations
        """
        # Load interpretations knowledge base
        self.interpretations_kb = {}
        self.load_interpretations(interpretations_json_path)
            
        # Load psychological perspectives
        self.perspectives = self._load_psychological_perspectives()
        
        # Precompile regex patterns for better performance
        self.word_pattern = re.compile(r'\b\w+\b')
        
        # Define dream themes for categorization (as sets for faster lookup)
        self.dream_themes = {
            "Chase Dreams": {"chase", "run", "escape", "hide", "pursue", "follow"},
            "Falling Dreams": {"fall", "falling", "drop", "plummet", "descend"},
            "Flying Dreams": {"fly", "flying", "float", "soar", "levitate", "hover"},
            "Water-related Dreams": {"water", "ocean", "river", "swim", "sea", "beach", "lake", "drown", "dive", "boat"},
            "Lost Dreams": {"maze", "lost", "find", "search", "path", "way", "direction", "confused"},
            "Animal Dreams": {"animal", "cat", "dog", "snake", "bird", "wolf", "horse", "bear", "fox", "lion", "tiger"},
            "Transformation Dreams": {"change", "transform", "become", "shift", "evolve", "morph", "different"},
            "Journey Dreams": {"journey", "travel", "path", "road", "destination", "trip", "adventure", "quest"},
        }
        
        # Cache for dream analysis results
        self._analysis_cache = {}
        self._summary_cache = {}
        self._perspective_cache = {}
        
        # Initialize keyword frequency map for efficient lookup
        self._build_keyword_index()
        
    def load_interpretations(self, interpretations_json_path):
        """Load interpretations knowledge base with error handling"""
        try:
            if os.path.exists(interpretations_json_path):
                with open(interpretations_json_path, 'r', encoding='utf-8') as f:
                    self.interpretations_kb = json.load(f)
                logger.info(f"Loaded {len(self.interpretations_kb)} dream symbols")
            else:
                logger.warning(f"Interpretations file not found: {interpretations_json_path}")
        except Exception as e:
            logger.error(f"Error loading interpretations: {str(e)}")
            self.interpretations_kb = {}
    
    def _build_keyword_index(self):
        """Build index of keywords for faster lookup"""
        self.single_keywords = set()
        self.compound_keywords = []
        
        for keyword in self.interpretations_kb:
            if '_' in keyword:
                parts = keyword.split('_')
                self.compound_keywords.append((keyword, parts))
            else:
                self.single_keywords.add(keyword)
                
        logger.info(f"Built keyword index with {len(self.single_keywords)} single keywords and {len(self.compound_keywords)} compound keywords")
    
    def _load_psychological_perspectives(self):
        """Load psychological perspectives for dream analysis"""
        return [
            "From a Jungian perspective, this dream may reflect aspects of your collective unconscious and the archetypes that influence your psyche. Consider how these symbols connect to universal human experiences.",
            
            "In Freudian analysis, dreams often represent unconscious desires and repressed thoughts. The symbols in your dream might be disguised expressions of deeper wishes or conflicts.",
            
            "Cognitive psychology suggests dreams help process emotions and consolidate memories. Your dream may be your mind's way of working through recent experiences or emotions.",
            
            "From an existential perspective, this dream might reflect your search for meaning and authenticity. Consider how the elements relate to your life's purpose and choices.",
            
            "Gestalt psychology would view the different elements of your dream as parts of your personality or life experience. Try to integrate these parts to understand the whole message.",
            
            "Neurologically, dreams occur during REM sleep when the brain processes information and emotions. The symbols may represent neural connections being formed between different memories and feelings."
        ]
        
    @functools.lru_cache(maxsize=128)
    def analyze_dream(self, dream_text):
        """
        Analyze dream text and provide detailed interpretations.
        
        Args:
            dream_text: The text of the dream to analyze
            
        Returns:
            A list of dictionaries containing interpretations
        """
        if not dream_text:
            return []
        
        # Check cache first
        if dream_text in self._analysis_cache:
            return self._analysis_cache[dream_text]
            
        dream_text = dream_text.lower()
        
        # Extract keywords from dream text more efficiently
        words = self.word_pattern.findall(dream_text)
        word_counter = Counter(words)
        word_set = set(words)  # For faster lookups
        
        # Check for compound keywords (phrases) efficiently
        compound_matches = []
        for keyword, parts in self.compound_keywords:
            # Check if search term exists in the dream text
            search_term = keyword.replace('_', ' ')
            if search_term in dream_text:
                compound_matches.append({
                    "keyword": search_term,
                    "interpretation": self.interpretations_kb[keyword],
                    "relevance": 10  # Higher relevance for compound matches
                })
            # Alternatively, check if all parts exist in the dream
            elif all(part in word_set for part in parts):
                compound_matches.append({
                    "keyword": search_term,
                    "interpretation": self.interpretations_kb[keyword],
                    "relevance": 8  # Lower relevance for partial matches
                })
        
        # Check single keywords efficiently using set intersection
        single_matches = []
        matching_keywords = self.single_keywords.intersection(word_set)
        for keyword in matching_keywords:
            # Calculate relevance based on word frequency and position
            relevance = word_counter.get(keyword, 0)
            
            # Boost relevance if keyword appears early in the dream
            if dream_text.find(keyword) < len(dream_text) // 3:
                relevance += 2
                
            single_matches.append({
                "keyword": keyword,
                "interpretation": self.interpretations_kb[keyword],
                "relevance": relevance
            })
        
        # Combine results and sort by relevance
        all_matches = compound_matches + single_matches
        all_matches.sort(key=lambda x: x["relevance"], reverse=True)
        
        # Take top results 
        top_results = all_matches[:7]
        
        # Remove relevance field
        for result in top_results:
            result.pop("relevance", None)
        
        # Cache the result
        self._analysis_cache[dream_text] = top_results
        
        # Limit cache size
        if len(self._analysis_cache) > 1000:
            # Remove a random item to prevent memory issues
            self._analysis_cache.pop(next(iter(self._analysis_cache)))
            
        return top_results
    
    @functools.lru_cache(maxsize=128)
    def summarize_dream(self, dream_text):
        """
        Create a more intelligent summary of the dream.
        
        Args:
            dream_text: The text of the dream to summarize
            
        Returns:
            A string containing a summary of the dream
        """
        if not dream_text:
            return ""
        
        # Check cache first
        if dream_text in self._summary_cache:
            return self._summary_cache[dream_text]
            
        dream_text = dream_text.lower()
        
        # Extract key themes and elements efficiently
        word_set = set(self.word_pattern.findall(dream_text))
        
        # Check for dream themes more efficiently
        key_themes = []
        for theme, keywords in self.dream_themes.items():
            if keywords.intersection(word_set):
                key_themes.append(theme)
                
        # Extract key elements using our keyword index
        key_elements = list(self.single_keywords.intersection(word_set))
                
        # Generate a more detailed summary
        summary = ""
        if key_themes:
            theme_text = ", ".join(key_themes)
            if key_elements:
                elements_text = ", ".join(key_elements[:5])
                summary = f"A dream about {theme_text}, containing elements such as {elements_text}"
            else:
                summary = f"A dream about {theme_text}"
        elif key_elements:
            elements_text = ", ".join(key_elements[:5])
            summary = f"A dream containing key elements such as {elements_text}"
        else:
            # Improved fallback summarization
            sentences = re.split(r'[.!?]', dream_text)
            if sentences and len(sentences[0]) < 150:
                summary = sentences[0].strip() + "..."
            else:
                summary = dream_text[:100] + "..."
        
        # Cache the result
        self._summary_cache[dream_text] = summary
        
        # Limit cache size
        if len(self._summary_cache) > 1000:
            # Remove a random item to prevent memory issues
            self._summary_cache.pop(next(iter(self._summary_cache)))
                
        return summary
    
    @functools.lru_cache(maxsize=64)
    def get_psychological_perspective(self, dream_text, interpretations):
        """
        Generate a more detailed psychological perspective on the dream.
        
        Args:
            dream_text: The text of the dream
            interpretations: List of interpretation dictionaries
            
        Returns:
            A string containing a psychological perspective
        """
        # Create a cache key from dream text and interpretation keywords
        cache_key = dream_text
        if cache_key in self._perspective_cache:
            return self._perspective_cache[cache_key]
            
        dream_text = dream_text.lower()
        word_set = set(self.word_pattern.findall(dream_text))
        
        # Extract keywords from interpretations
        interpretation_keywords = [item.get("keyword", "").lower() for item in interpretations]
        
        # More efficient theme checking using sets
        chase_keywords = {"chase", "run", "escape", "hide", "pursue"}
        water_keywords = {"water", "ocean", "river", "swim", "sea", "lake", "beach"}
        flying_keywords = {"fly", "flying", "float", "soar", "levitate"}
        falling_keywords = {"fall", "falling", "drop", "plummet"}
        
        # Check for specific themes to provide targeted perspectives
        if chase_keywords.intersection(word_set):
            perspective = "Your dream contains themes of pursuit or escape. From a psychological perspective, this often represents avoiding an issue or emotion in waking life. The pursuer may symbolize an aspect of yourself or a situation you're reluctant to face. Consider what you might be avoiding and why it feels threatening."
        elif water_keywords.intersection(word_set):
            perspective = "Water in dreams often symbolizes emotions and the unconscious mind. The state of the water (calm, turbulent, etc.) may reflect your emotional state. From a Jungian perspective, water represents the depths of the psyche. Your dream suggests you may be processing deep emotions or exploring aspects of your unconscious mind."
        elif flying_keywords.intersection(word_set):
            perspective = "Flying dreams often represent freedom, transcendence, or a desire to escape limitations. From a psychological perspective, they may indicate a period of personal growth or a wish to rise above current challenges. Consider what areas of your life might benefit from a broader perspective or where you feel constrained."
        elif falling_keywords.intersection(word_set):
            perspective = "Dreams of falling often relate to feelings of insecurity, anxiety, or loss of control. Psychologically, they may reflect a situation where you feel unsupported or overwhelmed. Consider areas in your life where you might need more stability or support."
        # Enhanced perspective generation based on interpretation keywords
        elif interpretation_keywords and len(interpretation_keywords) >= 2:
            # Get the most relevant keywords (top 3)
            top_keywords = interpretation_keywords[:3]
            perspective = f"Your dream features elements such as {', '.join(top_keywords[:-1])} and {top_keywords[-1]}. From a psychological perspective, this combination suggests a complex inner state. These symbols together may reflect a period of transition or deeper emotional processing. The relationship between these elements mirrors internal dynamics that may be at work in your waking life."
        else:
            # If no specific theme is detected, return a more detailed random perspective
            base_perspective = random.choice(self.perspectives)
            
            # Add additional depth to the perspective
            additional_insights = [
                "Dreams often serve as a bridge between our conscious and unconscious mind, revealing aspects of ourselves we may not be fully aware of in waking life.",
                "The emotional tone of your dream may be as significant as the content itself. Consider how you felt during and after the dream.",
                "Recurring elements in dreams often point to unresolved issues or important themes in your life that deserve attention.",
                "Your dream may be processing recent experiences, preparing you for future challenges, or integrating aspects of your personality."
            ]
            
            perspective = f"{base_perspective} {random.choice(additional_insights)}"
        
        # Cache the result
        self._perspective_cache[cache_key] = perspective
        
        # Limit cache size
        if len(self._perspective_cache) > 500:
            # Remove a random item to prevent memory issues
            self._perspective_cache.pop(next(iter(self._perspective_cache)))
            
        return perspective