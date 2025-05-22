from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import re
import os
from datetime import datetime
import time
import logging
import model_service

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

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize dreams history storage
DREAMS_HISTORY_FILE = 'dreams_history.json'
if not os.path.exists(DREAMS_HISTORY_FILE):
    with open(DREAMS_HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f)
    logger.info(f"Created new dreams history file: {DREAMS_HISTORY_FILE}")

# Initialize models asynchronously for faster startup
model_service.initialize_models(async_loading=True)

@app.route('/api/interpret', methods=['POST'])
def interpret_dream():
    """API endpoint to interpret dreams"""
    start_time = time.time()
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400

        dream_text = data.get('dream_text', '').lower()
        user_id = data.get('user_id', 'anonymous')
        use_ml = data.get('use_ml', True)

        if not dream_text:
            return jsonify({"error": "Dream description cannot be empty"}), 400

        # Use model service to analyze the dream
        result = model_service.analyze_dream(dream_text, user_id, use_ml)

        # If model_service returns None, fall back to basic analysis
        if result is None:
            # Fall back to basic keyword matching
            results = model_service.analyze_dream_basic(dream_text)
            psych_perspective = model_service.get_psychological_perspective_basic(dream_text, results)
            dream_summary = model_service.summarize_dream_basic(dream_text)
            model_used = "basic_matching"

            # If no matches found, provide a generic response
            if not results:
                results.append({
                    "keyword": "General",
                    "interpretation": "Your dream contains elements that may represent your subconscious thoughts. Dreams are highly personal, and you might want to consider what these symbols mean specifically to you."
                })

            # Format response
            result = {
                "dream_summary": dream_summary,
                "interpretations": results,
                "psychological_perspective": psych_perspective,
                "model_used": model_used,
                "processing_time": f"{time.time() - start_time:.2f}s"
            }

        # Check if there was an error in the model service
        if "error" in result:
            return jsonify(result), 500

        # Save dream to history
        save_dream_to_history(dream_text, result["interpretations"], user_id)

        logger.info(f"Dream analysis completed in {time.time() - start_time:.2f}s using {result['model_used']} model")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in interpret_dream: {str(e)}", exc_info=True)
        return jsonify({"error": "An internal server error occurred", "details": str(e)}), 500

def save_dream_to_history(dream_text, interpretations, user_id):
    """Save dream interpretation to history with improved error handling"""
    try:
        # Read current history
        with open(DREAMS_HISTORY_FILE, 'r', encoding='utf-8') as f:
            history = json.load(f)

        # Add new entry (with shorter dream text representation)
        truncated_dream = dream_text if len(dream_text) < 200 else dream_text[:197] + "..."

        entry = {
            "id": len(history) + 1,
            "user_id": user_id,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "dream_text": truncated_dream,
            "interpretations": interpretations[:3]  # Store only top 3 interpretations to save space
        }

        history.append(entry)

        # Limit history size to prevent file growth
        if len(history) > 1000:
            history = history[-1000:]

        # Write back to file
        with open(DREAMS_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Error saving dream to history: {e}")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """Serve frontend files"""
    frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend')

    if path:
        file_path = os.path.join(frontend_dir, path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            directory, filename = os.path.split(file_path)
            return send_from_directory(directory, filename)

    return send_from_directory(frontend_dir, 'index.html')

@app.route('/api/history', methods=['GET'])
def get_dream_history():
    """Get dream interpretation history with pagination"""
    try:
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        user_id = request.args.get('user_id', None)

        # Read history
        with open(DREAMS_HISTORY_FILE, 'r', encoding='utf-8') as f:
            history = json.load(f)

        # Filter by user_id if specified
        if user_id:
            history = [entry for entry in history if entry.get('user_id') == user_id]

        # Calculate pagination
        total_items = len(history)
        total_pages = (total_items + per_page - 1) // per_page
        start_idx = (page - 1) * per_page
        end_idx = min(start_idx + per_page, total_items)

        # Get paginated items
        items = history[start_idx:end_idx]

        return jsonify({
            "items": items,
            "total_items": total_items,
            "total_pages": total_pages,
            "current_page": page
        })
    except Exception as e:
        logger.error(f"Error retrieving dream history: {e}")
        return jsonify({"error": "Failed to retrieve dream history"}), 500

@app.route('/api/stats', methods=['GET'])
def get_dream_stats():
    """Get statistics about dream interpretations"""
    try:
        # Read history
        with open(DREAMS_HISTORY_FILE, 'r', encoding='utf-8') as f:
            history = json.load(f)

        if not history:
            return jsonify({
                "total_dreams": 0,
                "common_keywords": [],
                "last_week_count": 0
            })

        # Calculate stats
        total_dreams = len(history)

        # Extract all keywords from interpretations
        from collections import Counter
        keyword_counter = Counter()
        for entry in history:
            for interp in entry.get('interpretations', []):
                keyword = interp.get('keyword', '')
                if keyword and keyword != 'General':
                    keyword_counter[keyword] += 1

        # Get common keywords
        common_keywords = [{"keyword": k, "count": c} for k, c in keyword_counter.most_common(10)]

        # Calculate dreams in the last week
        today = datetime.now()
        last_week = [entry for entry in history if
                    (today - datetime.strptime(entry['date'], "%Y-%m-%d %H:%M:%S")).days <= 7]
        last_week_count = len(last_week)

        return jsonify({
            "total_dreams": total_dreams,
            "common_keywords": common_keywords,
            "last_week_count": last_week_count,
            "model_stats": model_service.get_model_status()
        })
    except Exception as e:
        logger.error(f"Error generating dream stats: {e}")
        return jsonify({"error": "Failed to generate statistics"}), 500

@app.route('/api/model-status', methods=['GET'])
def get_model_status():
    """Get current status of available models"""
    try:
        return jsonify(model_service.get_model_status())
    except Exception as e:
        logger.error(f"Error retrieving model status: {e}")
        return jsonify({"error": "Failed to retrieve model status"}), 500

@app.route('/api/clear-cache', methods=['POST'])
def clear_cache():
    """Clear the cache of dream analysis results"""
    try:
        count = model_service.clear_cache()
        return jsonify({"message": f"Cleared {count} entries from cache"})
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        return jsonify({"error": "Failed to clear cache"}), 500

@app.route('/api/reload-models', methods=['POST'])
def reload_models():
    """Reload all models"""
    try:
        model_service.initialize_models(async_loading=False)
        return jsonify({"message": "Models reloaded successfully"})
    except Exception as e:
        logger.error(f"Error reloading models: {e}")
        return jsonify({"error": "Failed to reload models"}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)