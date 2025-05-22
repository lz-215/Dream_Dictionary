"""
Deep Learning Model for Dream Interpretation
This module implements a deep learning approach to analyze and interpret dreams
based on the knowledge base and rules defined in the project.
"""

import re
import json
import random
import numpy as np
from collections import Counter
import os
import logging
import functools
import time
from typing import List, Dict, Any, Optional, Tuple

# Configure logging
logger = logging.getLogger(__name__)

# Try to import deep learning libraries, with fallback to simpler methods if not available
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
    logger.info("scikit-learn available, using advanced text analysis")
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn not available, falling back to basic matching")

# Try to import TensorFlow, but don't fail if it's not available
TENSORFLOW_AVAILABLE = False
try:
    import tensorflow as tf
    from tensorflow.keras import layers, models
    TENSORFLOW_AVAILABLE = True
    logger.info("TensorFlow available, advanced models will be used")
    
    # Set memory growth to prevent TensorFlow from consuming all GPU memory
    try:
        gpus = tf.config.list_physical_devices('GPU')
        if gpus:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            logger.info(f"GPU memory growth enabled for {len(gpus)} GPUs")
    except Exception as e:
        logger.warning(f"Error configuring GPU memory: {e}")
except ImportError:
    logger.warning("TensorFlow not available, advanced models will not be used")

# Path to knowledge base files
KNOWLEDGE_BASE_PATH = 'dream-interpretation-knowledge-base.md'
RULES_PATH = 'dream-interpretation-rules.md'

class DreamInterpreter:
    """
    A class that uses deep learning techniques to interpret dreams
    based on the knowledge base and rules.
    """

    def __init__(self, interpretations_json_path='interpretations.json'):
        """
        Initialize the dream interpreter with the knowledge base.

        Args:
            interpretations_json_path: Path to the JSON file containing dream symbol interpretations
        """
        self.interpretations_kb = {}
        self.kb_content = ""
        self.rules_content = ""
        self.perspectives = []
        self.vectorizer = None
        self.tf_model = None
        
        # Performance optimization: caching
        self._analysis_cache = {}
        self._summary_cache = {}
        self._perspective_cache = {}
        
        # Initialize models and load data
        start_time = time.time()
        self.load_interpretations(interpretations_json_path)
        self.load_knowledge_base()
        self.extract_perspectives()
        self.initialize_models()
        
        # Precompile regex patterns for better performance
        self.word_pattern = re.compile(r'\b\w+\b')
        
        # Create keyword indexes for faster lookup
        self._create_keyword_indexes()
        
        logger.info(f"Dream interpreter initialized in {time.time() - start_time:.2f} seconds")

    def load_interpretations(self, json_path: str) -> None:
        """Load the dream symbol interpretations from JSON file"""
        try:
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    self.interpretations_kb = json.load(f)
                logger.info(f"Loaded {len(self.interpretations_kb)} dream symbols from {json_path}")
        except Exception as e:
            logger.error(f"Error loading interpretations: {e}")
            self.interpretations_kb = {}

    def load_knowledge_base(self) -> None:
        """Load and process the knowledge base and rules"""
        # Try to load knowledge base
        try:
            if os.path.exists(KNOWLEDGE_BASE_PATH):
                with open(KNOWLEDGE_BASE_PATH, 'r', encoding='utf-8') as f:
                    self.kb_content = f.read()
                logger.info(f"Loaded knowledge base from {KNOWLEDGE_BASE_PATH}")
        except Exception as e:
            logger.error(f"Error loading knowledge base: {e}")

        # Try to load rules
        try:
            if os.path.exists(RULES_PATH):
                with open(RULES_PATH, 'r', encoding='utf-8') as f:
                    self.rules_content = f.read()
                logger.info(f"Loaded rules from {RULES_PATH}")
        except Exception as e:
            logger.error(f"Error loading rules: {e}")

    def _create_keyword_indexes(self) -> None:
        """Create keyword indexes for faster matching"""
        self.single_keywords = set()
        self.compound_keywords = []
        
        for keyword in self.interpretations_kb:
            if '_' in keyword:
                parts = keyword.split('_')
                self.compound_keywords.append((keyword, parts))
            else:
                self.single_keywords.add(keyword)
                
        logger.info(f"Created keyword indexes with {len(self.single_keywords)} single keywords and {len(self.compound_keywords)} compound keywords")

    def extract_perspectives(self) -> None:
        """Extract psychological perspectives from the knowledge base"""
        self.perspectives = [
            "从弗洛伊德的观点来看，梦境常常代表无意识的欲望和潜意识的满足。你梦中的符号可能反映了更深层次的欲求或冲突。",
            "根据荣格的分析心理学，梦境将我们连接到集体无意识。你的梦境符号可能代表了跨文化出现的普遍原型。",
            "现代认知理论表明，梦境有助于处理情绪和巩固记忆。你的梦可能在帮助你处理近期的经历。",
            "从存在主义的角度看，梦境可以反映我们对意义和真实性的追求。考虑这个梦与你生活目标的关系。",
            "从神经学角度，梦境发生在REM睡眠期间，大脑正在处理信息和情绪。你梦中的符号可能代表正在形成的神经连接。"
        ]

        # If we have knowledge base content, try to extract more perspectives
        if self.kb_content:
            # Extract sections that might contain good perspectives
            sections = re.split(r'#{2,3}\s+', self.kb_content)
            for section in sections:
                if '心理学' in section or '理论' in section:
                    # Extract sentences that might be good perspectives
                    sentences = re.split(r'[.。]', section)
                    for sentence in sentences:
                        if len(sentence) > 30 and ('梦境' in sentence or '象征' in sentence):
                            cleaned = sentence.strip()
                            if cleaned and cleaned not in self.perspectives:
                                self.perspectives.append(cleaned)

    def initialize_models(self) -> None:
        """Initialize the deep learning models if available"""
        if SKLEARN_AVAILABLE:
            try:
                # Initialize TF-IDF vectorizer for text similarity
                self.vectorizer = TfidfVectorizer(
                    min_df=1,
                    stop_words='english',
                    lowercase=True,
                    max_features=5000
                )

                # Create a corpus from our interpretations to train the vectorizer
                corpus = []
                for keyword, interpretation in self.interpretations_kb.items():
                    corpus.append(f"{keyword} {interpretation}")

                if corpus:
                    self.vectorizer.fit(corpus)
                    logger.info("TF-IDF vectorizer initialized with a corpus of %d documents", len(corpus))
            except Exception as e:
                logger.error(f"Error initializing TF-IDF vectorizer: {e}")
                self.vectorizer = None

        # Initialize TensorFlow model if available
        if TENSORFLOW_AVAILABLE:
            try:
                # Create a simple text classification model with better memory efficiency
                self.tf_model = models.Sequential([
                    layers.Dense(64, activation='relu', input_shape=(5000,)),  # Reduced from 128
                    layers.Dropout(0.4),
                    layers.Dense(32, activation='relu'),  # Reduced from 64
                    layers.Dropout(0.3),
                    layers.Dense(16, activation='relu'),  # Reduced from 32
                    layers.Dense(8, activation='softmax')  # Reduced from 10
                ])

                # Compile the model with mixed precision for better performance
                tf.keras.mixed_precision.set_global_policy('mixed_float16')
                
                self.tf_model.compile(
                    optimizer='adam',
                    loss='sparse_categorical_crossentropy',
                    metrics=['accuracy']
                )

                logger.info("TensorFlow model initialized with optimized architecture")
            except Exception as e:
                logger.error(f"Error initializing TensorFlow model: {e}")
                self.tf_model = None

    @functools.lru_cache(maxsize=128)
    def analyze_dream(self, dream_text: str) -> List[Dict[str, str]]:
        """
        Analyze a dream text using deep learning techniques if available,
        otherwise fall back to enhanced keyword matching.

        Args:
            dream_text: The text of the dream to analyze

        Returns:
            A list of dictionaries containing interpretations
        """
        if not dream_text:
            return []

        # Check cache
        if dream_text in self._analysis_cache:
            return self._analysis_cache[dream_text]

        dream_text = dream_text.lower()
        start_time = time.time()

        # If scikit-learn is available, use TF-IDF and cosine similarity
        if SKLEARN_AVAILABLE and self.vectorizer:
            results = self._analyze_with_tfidf(dream_text)
        else:
            # Fall back to enhanced keyword matching
            results = self._analyze_with_keywords(dream_text)

        # Cache results
        self._analysis_cache[dream_text] = results
        
        # Limit cache size to prevent memory issues
        if len(self._analysis_cache) > 1000:
            self._analysis_cache.pop(next(iter(self._analysis_cache)))
        
        logger.debug(f"Dream analysis completed in {time.time() - start_time:.2f}s")
        return results

    def _analyze_with_tfidf(self, dream_text: str) -> List[Dict[str, str]]:
        """Analyze dream using TF-IDF and cosine similarity, with enhanced features"""
        results = []

        try:
            # Transform the dream text
            dream_vector = self.vectorizer.transform([dream_text])

            # Calculate similarity with each keyword and interpretation
            similarities = []
            for keyword, interpretation in self.interpretations_kb.items():
                # Create a document combining the keyword and interpretation
                key_interp = f"{keyword} {interpretation}"
                key_vector = self.vectorizer.transform([key_interp])

                # Calculate cosine similarity
                similarity = cosine_similarity(dream_vector, key_vector)[0][0]
                
                # Only consider matches above a threshold to improve relevance
                if similarity > 0.1:
                    similarities.append((keyword, interpretation, similarity))

            # Sort by similarity score (highest first)
            similarities.sort(key=lambda x: x[2], reverse=True)
            
            # Take top results
            top_similarities = similarities[:10]
            
            # Format results
            for keyword, interpretation, score in top_similarities:
                # Convert underscores to spaces for display
                display_keyword = keyword.replace('_', ' ')
                
                results.append({
                    "keyword": display_keyword,
                    "interpretation": interpretation,
                    "relevance": float(score)  # Convert numpy float to Python float
                })
                
            # Remove relevance field before returning
            for result in results:
                result.pop("relevance", None)
                
        except Exception as e:
            logger.error(f"Error in TF-IDF analysis: {e}")
            # Fall back to keyword matching if TF-IDF fails
            results = self._analyze_with_keywords(dream_text)
            
        return results

    def _analyze_with_keywords(self, dream_text: str) -> List[Dict[str, str]]:
        """Analyze dream using enhanced keyword matching with optimizations"""
        # Get all words in the dream text
        words = self.word_pattern.findall(dream_text)
        word_counter = Counter(words)
        word_set = set(words)  # For faster lookups
        
        # Check for compound keywords efficiently
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
        
        # Combine and sort by relevance
        all_matches = compound_matches + single_matches
        all_matches.sort(key=lambda x: x["relevance"], reverse=True)
        
        # Take top results
        top_results = all_matches[:8]  # Increased from 5 to 8 for more comprehensive analysis
        
        # Remove relevance field
        for result in top_results:
            result.pop("relevance", None)
            
        return top_results

    @functools.lru_cache(maxsize=64)
    def summarize_dream(self, dream_text: str) -> str:
        """
        Create an intelligent summary of the dream using NLP techniques.
        
        Args:
            dream_text: The text of the dream to summarize
            
        Returns:
            A string containing a summary of the dream
        """
        if not dream_text:
            return ""
            
        # Check cache
        if dream_text in self._summary_cache:
            return self._summary_cache[dream_text]
            
        # Categorize dream themes
        dream_themes = {
            "追逐梦": {"chase", "run", "escape", "hide", "pursue", "follow"},
            "坠落梦": {"fall", "falling", "drop", "plummet", "descend"},
            "飞行梦": {"fly", "flying", "float", "soar", "levitate", "hover"},
            "水相关梦": {"water", "ocean", "river", "swim", "sea", "beach", "lake", "drown", "dive", "boat"},
            "迷失梦": {"maze", "lost", "find", "search", "path", "way", "direction", "confused"},
            "动物梦": {"animal", "cat", "dog", "snake", "bird", "wolf", "horse", "bear", "fox", "lion", "tiger"},
            "变形梦": {"change", "transform", "become", "shift", "evolve", "morph", "different"},
            "旅途梦": {"journey", "travel", "path", "road", "destination", "trip", "adventure", "quest"},
        }
            
        # Use TF-IDF if available for better summarization
        if SKLEARN_AVAILABLE and self.vectorizer and len(dream_text) > 100:
            try:
                # Get the most important words using TF-IDF
                tfidf_matrix = self.vectorizer.transform([dream_text])
                feature_names = self.vectorizer.get_feature_names_out()
                
                # Get top words
                tfidf_scores = zip(feature_names, tfidf_matrix.toarray()[0])
                sorted_scores = sorted(tfidf_scores, key=lambda x: x[1], reverse=True)
                top_words = [word for word, score in sorted_scores[:8] if len(word) > 3]
                
                # Create a more informative summary
                if top_words:
                    summary = f"梦境分析: 这个梦包含了 {', '.join(top_words)} 等关键元素。"
                    
                    # Extract dream themes
                    word_set = set(self.word_pattern.findall(dream_text.lower()))
                    themes = []
                    for theme, keywords in dream_themes.items():
                        if keywords.intersection(word_set):
                            themes.append(theme)
                    
                    if themes:
                        summary += f" 这是一个 {'/'.join(themes)}。"
                        
                    # Cache and return
                    self._summary_cache[dream_text] = summary
                    return summary
            except Exception as e:
                logger.error(f"Error in TF-IDF summarization: {e}")
                # Fall back to basic summarization
        
        # Basic fallback summarization
        dream_text_lower = dream_text.lower()
        word_set = set(self.word_pattern.findall(dream_text_lower))
        
        # Extract themes
        themes = []
        for theme, keywords in dream_themes.items():
            if keywords.intersection(word_set):
                themes.append(theme)
                
        # Extract key elements using our keyword index
        key_elements = list(self.single_keywords.intersection(word_set))
        
        # Generate summary based on themes and elements
        if themes:
            theme_text = ", ".join(themes)
            if key_elements and len(key_elements) >= 2:
                elements_text = ", ".join(key_elements[:5])
                summary = f"梦境类型: {theme_text}, 包含 {elements_text} 等关键元素"
            else:
                summary = f"梦境类型: {theme_text}"
        elif key_elements and len(key_elements) >= 2:
            elements_text = ", ".join(key_elements[:5])
            summary = f"梦境包含 {elements_text} 等关键元素"
        else:
            # Extract the first sentence or a portion of text
            sentences = re.split(r'[.。!！?？]', dream_text)
            if sentences and len(sentences[0]) < 150:
                summary = sentences[0].strip() + "..."
            else:
                summary = dream_text[:120] + "..."
                
        # Cache the result
        self._summary_cache[dream_text] = summary
        
        # Limit cache size
        if len(self._summary_cache) > 500:
            self._summary_cache.pop(next(iter(self._summary_cache)))
            
        return summary

    @functools.lru_cache(maxsize=64)
    def get_psychological_perspective(self, dream_text: str, interpretations: List[Dict[str, str]]) -> str:
        """
        Generate a psychological perspective on the dream using deep learning if available.
        
        Args:
            dream_text: The text of the dream
            interpretations: List of interpretation dictionaries
            
        Returns:
            A string containing a psychological perspective
        """
        # Check cache
        cache_key = f"{dream_text[:100]}"  # Use first 100 chars as key
        if cache_key in self._perspective_cache:
            return self._perspective_cache[cache_key]
            
        dream_text = dream_text.lower()
        
        # Get keywords from dream
        word_set = set(self.word_pattern.findall(dream_text))
        
        # More efficient theme checking using sets
        chase_keywords = {"chase", "run", "escape", "hide", "pursue"}
        water_keywords = {"water", "ocean", "river", "swim", "sea", "lake", "beach"}
        flying_keywords = {"fly", "flying", "float", "soar", "levitate"}
        falling_keywords = {"fall", "falling", "drop", "plummet"}
        test_keywords = {"test", "exam", "school", "grade", "fail", "pass", "study"}
        teeth_keywords = {"teeth", "tooth", "dentist", "mouth", "falling out", "loose"}
        
        # Extract emotions from dream text
        positive_emotions = {"happy", "joy", "excited", "peaceful", "calm", "love"}
        negative_emotions = {"fear", "anxiety", "worried", "sad", "angry", "scared", "terror", "horror"}
        
        emotion = "neutral"
        if word_set.intersection(positive_emotions):
            emotion = "positive"
        elif word_set.intersection(negative_emotions):
            emotion = "negative"
        
        # Check specific themes to provide more targeted analysis
        if chase_keywords.intersection(word_set):
            perspective = "你的梦包含追逐或逃跑的主题。从心理学角度看，这通常代表在现实生活中回避某个问题或情绪。追赶者可能象征你自己的一个方面或你不愿面对的情况。考虑一下你可能在回避什么，以及为什么它感觉有威胁。"
            
        elif water_keywords.intersection(word_set):
            perspective = "梦中的水往往象征情绪和无意识心灵。水的状态（平静、湍急等）可能反映你的情绪状态。从荣格的角度看，水代表心灵的深处。你的梦暗示你可能正在处理深层情绪或探索你无意识心灵的各个方面。"
            
        elif flying_keywords.intersection(word_set):
            perspective = "飞行梦通常代表自由、超越或摆脱限制的愿望。从心理学角度看，它们可能表明个人成长期或希望超越当前挑战。考虑一下你生活中哪些领域可能受益于更广阔的视角或你在哪里感到受限。"
            
        elif falling_keywords.intersection(word_set):
            perspective = "坠落梦往往与不安全感、焦虑或失控感有关。从心理学角度看，它们可能反映一种你感到缺乏支持或不知所措的情况。考虑你生活中哪些领域可能需要更多的稳定性或支持。"
            
        elif test_keywords.intersection(word_set):
            perspective = "考试或测试梦通常与自我评价和对失败的恐惧有关。这类梦可能反映你在生活中感到被评判或担心无法达到期望。考虑一下你是否在对自己要求过高，或者是否需要在某个领域建立更多的信心。"
            
        elif teeth_keywords.intersection(word_set):
            perspective = "关于牙齿的梦，特别是牙齿掉落，通常与担忧自己的形象、权力丧失或沟通恐惧有关。从心理学角度看，牙齿代表你的自信和个人力量。这个梦可能反映你担心失去某种控制或面临重大变化。"
            
        # Use TensorFlow for more advanced analysis if available
        elif TENSORFLOW_AVAILABLE and self.tf_model:
            try:
                # Simplified perspective generation
                if emotion == "positive":
                    perspective = random.choice([
                        "你的梦有积极情绪，表明你的潜意识可能在处理令人满足的经历或情感。从心理学角度看，这类梦境有助于巩固积极心理状态，可能标志着你处于个人成长或自我接纳的阶段。",
                        "这个积极的梦境反映了你内心的和谐状态。荣格理论认为，梦中的愉悦情绪常与自我整合和潜能实现相关，表明你可能正朝着更完整的自我迈进。"
                    ])
                elif emotion == "negative":
                    perspective = random.choice([
                        "你的梦包含负面情绪，这在心理学上通常被视为处理未解决问题或应对压力的方式。梦境可能在帮助你面对和整合日常生活中尚未充分承认的担忧或恐惧。",
                        "这个带有焦虑元素的梦可能是你潜意识在处理压力或未解决的冲突。弗洛伊德认为，这类梦是潜意识将白天压抑的情绪转化为象征性形象的方式，可能需要你反思生活中的某些挑战。"
                    ])
                else:
                    # Default to a random perspective
                    perspective = random.choice(self.perspectives)
            except Exception as e:
                logger.error(f"Error in TensorFlow perspective generation: {e}")
                perspective = random.choice(self.perspectives)
        else:
            # Use interpretation keywords if available
            if interpretations and len(interpretations) >= 2:
                interpretation_keywords = [item.get("keyword", "").lower() for item in interpretations[:3]]
                if interpretation_keywords:
                    keyword_list = ", ".join(interpretation_keywords)
                    perspective = f"你的梦包含 {keyword_list} 等元素。从心理学角度看，这种组合暗示了复杂的内在状态。这些符号共同可能反映了过渡期或更深层的情绪处理。这些元素之间的关系映射了可能在你的清醒生活中起作用的内部动态。"
                else:
                    perspective = random.choice(self.perspectives)
            else:
                perspective = random.choice(self.perspectives)
        
        # Cache the result
        self._perspective_cache[cache_key] = perspective
        
        # Limit cache size
        if len(self._perspective_cache) > 500:
            self._perspective_cache.pop(next(iter(self._perspective_cache)))
            
        return perspective