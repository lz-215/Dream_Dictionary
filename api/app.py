from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Simple in-memory dream interpretations
INTERPRETATIONS = {
    "飞翔": "象征自由、目标远大或逃避现实。",
    "掉牙": "可能表示焦虑、失落感或成长的烦恼。",
    "蛇": "通常代表转变、智慧或潜藏的危险/诱惑。",
    "水": "象征情感、潜意识或生命力。清澈的水通常是积极的，浑浊的水则相反。",
    "falling": "Often represents insecurity or anxiety about losing control.",
    "flying": "Usually symbolizes freedom, ambition, or escape from reality.",
    "teeth": "Can represent anxiety, loss, or concerns about appearance.",
    "water": "Symbolizes emotions, the unconscious, or life force.",
    "snake": "Often represents transformation, wisdom, or hidden danger/temptation."
}

# In-memory dream history
DREAMS_HISTORY = []

@app.route('/')
def home():
    """Serve simple status page"""
    return jsonify({
        "status": "online",
        "message": "Dream Interpreter API is running",
        "endpoints": [
            "/api/interpret - POST - Interpret a dream",
            "/api/history - GET - Get dream history",
            "/api/stats - GET - Get usage statistics"
        ]
    })

@app.route('/api/interpret', methods=['POST'])
def interpret_dream():
    """Interpret a dream based on keywords"""
    try:
        data = request.json
        dream_text = data.get('dream_text', '')
        user_id = data.get('user_id', 'anonymous')
        
        if not dream_text:
            return jsonify({"error": "No dream text provided"}), 400
        
        # Simple keyword matching
        results = []
        for keyword, interpretation in INTERPRETATIONS.items():
            if keyword.lower() in dream_text.lower():
                results.append({
                    "keyword": keyword,
                    "interpretation": interpretation
                })
        
        # If no matches found, provide a generic response
        if not results:
            results.append({
                "keyword": "General",
                "interpretation": "Your dream contains elements that may represent your subconscious thoughts. Dreams are highly personal, and you might want to consider what these symbols mean specifically to you."
            })
        
        # Create response
        response = {
            "dream_text": dream_text,
            "interpretations": results,
            "psychological_perspective": "Dreams often reflect our subconscious thoughts and feelings.",
            "summary": "Your dream may be processing recent experiences or emotions.",
            "model_used": "simple_keyword_matching"
        }
        
        # Save to history
        DREAMS_HISTORY.append({
            "user_id": user_id,
            "dream_text": dream_text,
            "interpretations": results,
            "timestamp": "2025-05-08T12:00:00Z"  # Simplified timestamp
        })
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error interpreting dream: {e}")
        return jsonify({"error": "Failed to interpret dream"}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get dream interpretation history"""
    try:
        return jsonify(DREAMS_HISTORY)
    except Exception as e:
        logger.error(f"Error retrieving history: {e}")
        return jsonify({"error": "Failed to retrieve history"}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get usage statistics"""
    try:
        return jsonify({
            "total_dreams": len(DREAMS_HISTORY),
            "common_keywords": ["water", "flying", "falling"],
            "last_week_count": len(DREAMS_HISTORY)
        })
    except Exception as e:
        logger.error(f"Error retrieving stats: {e}")
        return jsonify({"error": "Failed to retrieve stats"}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)