from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import re
import os
from datetime import datetime, timedelta
import time
import logging
import model_service
import hashlib
import secrets
import jwt

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

# Set secret key for JWT tokens
SECRET_KEY = secrets.token_hex(32)
TOKEN_EXPIRE_HOURS = 24  # Token expiration time in hours

# Initialize dreams history storage
DREAMS_HISTORY_FILE = 'dreams_history.json'
if not os.path.exists(DREAMS_HISTORY_FILE):
    with open(DREAMS_HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f)
    logger.info(f"Created new dreams history file: {DREAMS_HISTORY_FILE}")

# Initialize user database
USERS_DB_FILE = 'users.json'
if not os.path.exists(USERS_DB_FILE):
    with open(USERS_DB_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f)
    logger.info(f"Created new users database file: {USERS_DB_FILE}")

# Initialize models asynchronously for faster startup
model_service.initialize_models(async_loading=True)

# User authentication functions
def hash_password(password, salt=None):
    """Hash a password with a salt using SHA-256"""
    if not salt:
        salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return password_hash, salt

def verify_password(password, stored_hash, salt):
    """Verify a password against a stored hash"""
    password_hash, _ = hash_password(password, salt)
    return password_hash == stored_hash

def generate_token(user_id, username):
    """Generate a JWT token for authenticated users"""
    expiration = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': expiration
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token):
    """Verify a JWT token and return the user information"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

@app.route('/api/register', methods=['POST'])
def register_user():
    """Register a new user"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400

        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        # Validate input
        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400
        
        if len(username) < 3:
            return jsonify({"error": "Username must be at least 3 characters"}), 400
            
        if len(password) < 6:
            return jsonify({"error": "Password must be at least 6 characters"}), 400

        # Load existing users
        with open(USERS_DB_FILE, 'r', encoding='utf-8') as f:
            users = json.load(f)

        # Check if username already exists
        if any(user['username'] == username for user in users):
            return jsonify({"error": "Username already exists"}), 409

        # Hash password
        password_hash, salt = hash_password(password)

        # Create new user
        new_user = {
            "id": str(len(users) + 1),
            "username": username,
            "password_hash": password_hash,
            "salt": salt,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Add to users list
        users.append(new_user)

        # Save users back to file
        with open(USERS_DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)

        # Generate token
        token = generate_token(new_user["id"], username)

        return jsonify({
            "message": "User registered successfully",
            "user_id": new_user["id"],
            "username": username,
            "token": token
        })

    except Exception as e:
        logger.error(f"Error in register_user: {str(e)}", exc_info=True)
        return jsonify({"error": "An error occurred during registration"}), 500

@app.route('/api/login', methods=['POST'])
def login_user():
    """Login an existing user"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400

        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        # Validate input
        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        # Load existing users
        with open(USERS_DB_FILE, 'r', encoding='utf-8') as f:
            users = json.load(f)

        # Find user by username
        user = next((user for user in users if user['username'] == username), None)
        if not user:
            return jsonify({"error": "Invalid username or password"}), 401

        # Verify password
        if not verify_password(password, user['password_hash'], user['salt']):
            return jsonify({"error": "Invalid username or password"}), 401

        # Generate token
        token = generate_token(user["id"], username)

        return jsonify({
            "message": "Login successful",
            "user_id": user["id"],
            "username": username,
            "token": token
        })

    except Exception as e:
        logger.error(f"Error in login_user: {str(e)}", exc_info=True)
        return jsonify({"error": "An error occurred during login"}), 500

@app.route('/api/user', methods=['GET'])
def get_user_info():
    """Get user information from token"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Authorization header missing or invalid"}), 401
        
        token = auth_header.split(' ')[1]
        
        # Verify token
        payload = verify_token(token)
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        return jsonify({
            "user_id": payload["user_id"],
            "username": payload["username"]
        })
        
    except Exception as e:
        logger.error(f"Error in get_user_info: {str(e)}", exc_info=True)
        return jsonify({"error": "An error occurred while retrieving user information"}), 500

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
    """Get dream interpretation history with pagination and user authentication"""
    try:
        # Get auth token from header
        auth_header = request.headers.get('Authorization')
        user_id = None
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            payload = verify_token(token)
            if payload:
                user_id = payload['user_id']
        
        # Return empty response if not authenticated
        if not user_id:
            return jsonify({
                "error": "Authentication required to view dream history"
            }), 401
            
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))

        # Read history
        with open(DREAMS_HISTORY_FILE, 'r', encoding='utf-8') as f:
            history = json.load(f)

        # Filter by user_id 
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
    """Get statistics about dream interpretations with user authentication for personal stats"""
    try:
        # Get auth token from header
        auth_header = request.headers.get('Authorization')
        user_id = None
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            payload = verify_token(token)
            if payload:
                user_id = payload['user_id']
        
        # Read history
        with open(DREAMS_HISTORY_FILE, 'r', encoding='utf-8') as f:
            history = json.load(f)

        # Filter by user_id if authenticated, otherwise show global stats
        personal_stats = False
        if user_id:
            personal_history = [entry for entry in history if entry.get('user_id') == user_id]
            if len(personal_history) > 0:
                personal_stats = True
                history = personal_history

        if not history:
            return jsonify({
                "total_dreams": 0,
                "common_keywords": [],
                "last_week_count": 0,
                "personal_stats": personal_stats
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
        common_keywords = [{"keyword": k, "count": c} 
                          for k, c in keyword_counter.most_common(10)]
        
        # Count dreams from last week
        from datetime import datetime, timedelta
        one_week_ago = datetime.now() - timedelta(days=7)
        one_week_ago_str = one_week_ago.strftime("%Y-%m-%d")
        
        last_week_count = sum(1 for entry in history 
                             if entry.get('date', '').split()[0] >= one_week_ago_str)
        
        return jsonify({
            "total_dreams": total_dreams,
            "common_keywords": common_keywords,
            "last_week_count": last_week_count,
            "personal_stats": personal_stats
        })
        
    except Exception as e:
        logger.error(f"Error retrieving dream stats: {e}")
        return jsonify({"error": "Failed to retrieve dream statistics"}), 500

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

@app.route('/api/google-login', methods=['POST'])
def google_login():
    """Process Google login data and create/update a user account"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400

        google_id = data.get('google_id')
        name = data.get('name', '')
        email = data.get('email', '')
        
        if not google_id:
            return jsonify({"error": "Google ID is required"}), 400

        # Load existing users
        with open(USERS_DB_FILE, 'r', encoding='utf-8') as f:
            users = json.load(f)

        # Check if user with this Google ID already exists
        user = next((user for user in users if user.get('google_id') == google_id), None)
        
        if not user:
            # Create new user with Google info
            new_user = {
                "id": str(len(users) + 1),
                "username": name or email or f"user_{len(users) + 1}",
                "google_id": google_id,
                "email": email,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Add to users list
            users.append(new_user)
            
            # Save users back to file
            with open(USERS_DB_FILE, 'w', encoding='utf-8') as f:
                json.dump(users, f, ensure_ascii=False, indent=2)
                
            user = new_user
        
        # Generate token
        token = generate_token(user["id"], user.get("username", ""))

        return jsonify({
            "message": "Google login successful",
            "user_id": user["id"],
            "username": user.get("username", ""),
            "token": token
        })
        
    except Exception as e:
        logger.error(f"Error in google_login: {str(e)}", exc_info=True)
        return jsonify({"error": "An error occurred during Google login"}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)