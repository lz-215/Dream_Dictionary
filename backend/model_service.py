"""
Model Service Module for Dream Interpretation
This module manages loading, caching, and serving of dream interpretation models
"""

import os
import logging
import threading
import time
from typing import Dict, Any, List, Optional, Tuple
import json
import functools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("backend.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Model status flags
MODEL_AVAILABLE = False
ENHANCED_ANALYZER_AVAILABLE = False
TRANSFORMER_AVAILABLE = False
BERT_AVAILABLE = False

# Model instances
dream_interpreter = None
enhanced_analyzer = None
transformer_analyzer = None
bert_analyzer = None

# Cache for interpretation results
result_cache = {}
CACHE_TIMEOUT = 3600  # 1 hour cache timeout

# Thread lock for thread-safe model loading
model_lock = threading.Lock()

def load_dream_model() -> bool:
    """
    Load the deep learning dream interpreter model
    
    Returns:
        bool: Whether loading was successful
    """
    global dream_interpreter, MODEL_AVAILABLE
    
    with model_lock:
        try:
            from dream_model import DreamInterpreter
            start_time = time.time()
            dream_interpreter = DreamInterpreter()
            load_time = time.time() - start_time
            MODEL_AVAILABLE = True
            logger.info(f"Deep learning model loaded successfully in {load_time:.2f}s")
            return True
        except ImportError as e:
            logger.warning(f"Could not import deep learning model: {e}")
            logger.info("Falling back to enhanced dream analyzer")
            return False
        except Exception as e:
            logger.error(f"Error initializing dream interpreter: {str(e)}", exc_info=True)
            return False

def load_enhanced_analyzer() -> bool:
    """
    Load the enhanced dream analyzer
    
    Returns:
        bool: Whether loading was successful
    """
    global enhanced_analyzer, ENHANCED_ANALYZER_AVAILABLE
    
    with model_lock:
        try:
            from dream_analyzer import EnhancedDreamAnalyzer
            start_time = time.time()
            enhanced_analyzer = EnhancedDreamAnalyzer()
            load_time = time.time() - start_time
            ENHANCED_ANALYZER_AVAILABLE = True
            logger.info(f"Enhanced dream analyzer loaded successfully in {load_time:.2f}s")
            return True
        except ImportError as e:
            logger.warning(f"Could not import enhanced dream analyzer: {e}")
            logger.info("Falling back to basic keyword matching")
            return False
        except Exception as e:
            logger.error(f"Error initializing enhanced analyzer: {str(e)}", exc_info=True)
            return False

def load_transformer_model() -> bool:
    """
    Load the transformer-based dream analyzer
    
    Returns:
        bool: Whether loading was successful
    """
    global transformer_analyzer, TRANSFORMER_AVAILABLE
    
    with model_lock:
        try:
            from dream_transformer import DreamTransformer
            start_time = time.time()
            transformer_analyzer = DreamTransformer()
            load_time = time.time() - start_time
            TRANSFORMER_AVAILABLE = True
            logger.info(f"Transformer-based dream analyzer loaded successfully in {load_time:.2f}s")
            return True
        except ImportError as e:
            logger.warning(f"Could not import transformer-based dream analyzer: {e}")
            logger.info("Transformer models not available")
            return False
        except Exception as e:
            logger.error(f"Error initializing transformer analyzer: {str(e)}", exc_info=True)
            return False

def load_bert_model() -> bool:
    """
    Load the BERT-based dream analyzer
    
    Returns:
        bool: Whether loading was successful
    """
    global bert_analyzer, BERT_AVAILABLE
    
    with model_lock:
        try:
            from dream_bert import DreamBERT
            start_time = time.time()
            bert_analyzer = DreamBERT()
            load_time = time.time() - start_time
            BERT_AVAILABLE = True
            logger.info(f"BERT-based dream analyzer loaded successfully in {load_time:.2f}s")
            return True
        except ImportError as e:
            logger.warning(f"Could not import BERT-based dream analyzer: {e}")
            logger.info("BERT models not available")
            return False
        except Exception as e:
            logger.error(f"Error initializing BERT analyzer: {str(e)}", exc_info=True)
            return False

def initialize_models(async_loading: bool = True) -> None:
    """
    Initialize all dream interpretation models
    
    Args:
        async_loading: Whether to load models asynchronously
    """
    if async_loading:
        # Load models in separate threads for faster startup
        threading.Thread(target=load_bert_model, daemon=True).start()
        threading.Thread(target=load_transformer_model, daemon=True).start()
        threading.Thread(target=load_dream_model, daemon=True).start()
        threading.Thread(target=load_enhanced_analyzer, daemon=True).start()
        logger.info("Models are being loaded asynchronously")
    else:
        # Load models sequentially
        load_bert_model()
        load_transformer_model()
        load_dream_model()
        load_enhanced_analyzer()
        logger.info("Models loaded synchronously")

def get_model_status() -> Dict[str, Any]:
    """
    Get the current status of all models
    
    Returns:
        Dict: Status information for all models
    """
    models = {
        "bert": {
            "available": BERT_AVAILABLE,
            "status": "loaded" if BERT_AVAILABLE else "unavailable"
        },
        "transformer": {
            "available": TRANSFORMER_AVAILABLE,
            "status": "loaded" if TRANSFORMER_AVAILABLE else "unavailable"
        },
        "deep_learning": {
            "available": MODEL_AVAILABLE,
            "status": "loaded" if MODEL_AVAILABLE else "unavailable"
        },
        "enhanced_analyzer": {
            "available": ENHANCED_ANALYZER_AVAILABLE,
            "status": "loaded" if ENHANCED_ANALYZER_AVAILABLE else "unavailable"
        },
        "basic_matching": {
            "available": True,
            "status": "loaded"
        }
    }
    
    return {
        "models": models,
        "default_model": get_best_available_model_name(),
        "cache_entries": len(result_cache)
    }

def get_best_available_model_name() -> str:
    """
    Get the name of the best available model
    
    Returns:
        str: Name of the best available model
    """
    if BERT_AVAILABLE:
        return "bert"
    elif TRANSFORMER_AVAILABLE:
        return "transformer"
    elif MODEL_AVAILABLE:
        return "deep_learning"
    elif ENHANCED_ANALYZER_AVAILABLE:
        return "enhanced_analyzer"
    else:
        return "basic_matching"

def analyze_dream(dream_text: str, user_id: str = "anonymous", use_ml: bool = True) -> Dict[str, Any]:
    """
    Analyze a dream using the best available model
    
    Args:
        dream_text: The dream text to analyze
        user_id: User ID for tracking
        use_ml: Whether to use machine learning models
        
    Returns:
        Dict: Dream analysis results
    """
    if not dream_text:
        return {"error": "Dream description cannot be empty"}
    
    start_time = time.time()
    dream_text = dream_text.lower()
    
    # Generate cache key
    cache_key = f"{dream_text[:100]}_{use_ml}"
    
    # Check cache first
    if cache_key in result_cache:
        cache_entry = result_cache[cache_key]
        if time.time() - cache_entry['timestamp'] < CACHE_TIMEOUT:
            logger.info(f"Cache hit for dream analysis - {len(dream_text)} chars")
            return cache_entry['response']
    
    # Use the best available model based on the use_ml flag
    model_used = "unknown"
    results = []
    psych_perspective = ""
    dream_summary = ""
    
    try:
        if BERT_AVAILABLE and bert_analyzer and use_ml:
            results = bert_analyzer.analyze_dream(dream_text)
            psych_perspective = bert_analyzer.get_psychological_perspective(dream_text, results)
            dream_summary = bert_analyzer.summarize_dream(dream_text)
            model_used = "bert"
        elif TRANSFORMER_AVAILABLE and transformer_analyzer and use_ml:
            results = transformer_analyzer.analyze_dream(dream_text)
            psych_perspective = transformer_analyzer.get_psychological_perspective(dream_text, results)
            dream_summary = transformer_analyzer.summarize_dream(dream_text)
            model_used = "transformer"
        elif MODEL_AVAILABLE and dream_interpreter and use_ml:
            results = dream_interpreter.analyze_dream(dream_text)
            psych_perspective = dream_interpreter.get_psychological_perspective(dream_text, results)
            dream_summary = dream_interpreter.summarize_dream(dream_text)
            model_used = "deep_learning"
        elif ENHANCED_ANALYZER_AVAILABLE and enhanced_analyzer:
            results = enhanced_analyzer.analyze_dream(dream_text)
            psych_perspective = enhanced_analyzer.get_psychological_perspective(dream_text, results)
            dream_summary = enhanced_analyzer.summarize_dream(dream_text)
            model_used = "enhanced_analyzer"
        else:
            # Fall back to basic keyword matching (this would be implemented in app.py)
            model_used = "basic_matching"
            # Return None to signal that we need to fall back to basic matching
            return None
    except Exception as e:
        logger.error(f"Error analyzing dream: {str(e)}", exc_info=True)
        return {
            "error": "An error occurred during dream analysis",
            "details": str(e)
        }
    
    # If no matches found, provide a generic response
    if not results:
        results.append({
            "keyword": "General",
            "interpretation": "Your dream contains elements that may represent your subconscious thoughts. Dreams are highly personal, and you might want to consider what these symbols mean specifically to you."
        })
    
    # Format response
    response = {
        "dream_summary": dream_summary,
        "interpretations": results,
        "psychological_perspective": psych_perspective,
        "model_used": model_used,
        "processing_time": f"{time.time() - start_time:.2f}s"
    }
    
    # Cache result
    result_cache[cache_key] = {
        'response': response,
        'timestamp': time.time()
    }
    
    # Limit cache size to prevent memory issues
    if len(result_cache) > 1000:
        # Remove oldest entry
        oldest_key = min(result_cache.keys(), key=lambda k: result_cache[k]['timestamp'])
        del result_cache[oldest_key]
    
    logger.info(f"Dream analysis completed using {model_used} model in {time.time() - start_time:.2f}s")
    return response

def clear_cache() -> int:
    """
    Clear the result cache
    
    Returns:
        int: Number of cache entries cleared
    """
    global result_cache
    count = len(result_cache)
    result_cache = {}
    logger.info(f"Cleared {count} entries from result cache")
    return count

# Basic keyword matching implementation for fallback
def analyze_dream_basic(dream_text: str) -> List[Dict[str, str]]:
    """Basic keyword matching for dream analysis when no models are available"""
    try:
        # Load interpretations knowledge base
        with open('interpretations.json', 'r', encoding='utf-8') as f:
            interpretations_kb = json.load(f)
        
        import re
        from collections import Counter
        
        # Extract words from dream text
        words = re.findall(r'\b\w+\b', dream_text.lower())
        word_counter = Counter(words)
        word_set = set(words)
        
        # Check for compound keywords
        compound_matches = []
        for keyword in interpretations_kb:
            if '_' in keyword:
                parts = keyword.split('_')
                if all(part in dream_text for part in parts):
                    compound_matches.append({
                        "keyword": keyword.replace('_', ' '),
                        "interpretation": interpretations_kb[keyword],
                        "relevance": sum(word_counter.get(part, 0) for part in parts) / len(parts)
                    })
        
        # Check single keywords
        single_matches = []
        for keyword in interpretations_kb:
            if '_' not in keyword and keyword in dream_text:
                single_matches.append({
                    "keyword": keyword,
                    "interpretation": interpretations_kb[keyword],
                    "relevance": word_counter.get(keyword, 0)
                })
        
        # Combine and sort by relevance
        all_matches = compound_matches + single_matches
        all_matches.sort(key=lambda x: x["relevance"], reverse=True)
        
        # Take top results
        top_results = all_matches[:5]
        
        # Remove relevance field
        for result in top_results:
            result.pop("relevance", None)
        
        return top_results
    except Exception as e:
        logger.error(f"Error in basic dream analysis: {str(e)}", exc_info=True)
        return []

@functools.lru_cache(maxsize=100)
def summarize_dream_basic(dream_text: str) -> str:
    """Create a basic summary of the dream when no models are available"""
    try:
        import re
        
        # Basic fallback summarization
        if len(dream_text) <= 50:
            return dream_text

        # Try to find a sentence break for a more natural summary
        sentences = re.split(r'[.。!！?？]', dream_text)
        if sentences and len(sentences[0]) < 100:
            return sentences[0].strip() + "..."
        else:
            return dream_text[:100] + "..."
    except Exception as e:
        logger.error(f"Error in basic dream summarization: {str(e)}", exc_info=True)
        return dream_text[:100] + "..."

@functools.lru_cache(maxsize=50)
def get_psychological_perspective_basic(dream_text: str, results: List[Dict[str, str]]) -> str:
    """Provide a basic psychological perspective when no models are available"""
    try:
        import random
        import re
        
        perspectives = [
            "From a Freudian perspective, dreams often represent unconscious desires and wish fulfillment. The symbols in your dream may reflect deeper urges or conflicts.",
            "According to Jung's analytical psychology, dreams connect us to the collective unconscious. Your dream symbols might represent universal archetypes that appear across cultures.",
            "Modern cognitive theory suggests dreams help process emotions and consolidate memories. Your dream may be helping you work through recent experiences.",
            "From an existential perspective, dreams can reflect our search for meaning and authenticity. Consider how this dream relates to your life's purpose.",
            "Neurologically, dreams occur during REM sleep when the brain processes information and emotions. The symbols in your dream may represent neural connections being formed."
        ]
        
        # Check for specific themes
        word_set = set(re.findall(r'\b\w+\b', dream_text.lower()))
        
        chase_keywords = {"chase", "run", "escape", "hide"}
        water_keywords = {"water", "ocean", "river", "swim", "sea"}
        flying_keywords = {"fly", "flying", "float", "soar"}
        
        if word_set.intersection(chase_keywords):
            return "Your dream contains themes of pursuit or escape. From a psychological perspective, this often represents avoiding an issue or emotion in waking life. Consider what you might be reluctant to face."
        
        if word_set.intersection(water_keywords):
            return "Water in dreams often symbolizes emotions and the unconscious mind. From a Jungian perspective, the state of the water may reflect your emotional state. Consider what feelings might be surfacing in your life."
        
        if word_set.intersection(flying_keywords):
            return "Flying dreams often represent freedom, transcendence, or a desire to escape limitations. Consider what areas of your life might benefit from a broader perspective."
            
        return random.choice(perspectives)
    except Exception as e:
        logger.error(f"Error in basic psychological perspective generation: {str(e)}", exc_info=True)
        return "Dreams often reflect our unconscious mind's processing of daily experiences and emotions." 