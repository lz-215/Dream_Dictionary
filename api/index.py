import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Import the Flask app from the local app.py
    from api.app import app
    logger.info("Successfully imported Flask app")
except Exception as e:
    logger.error(f"Error importing Flask app: {str(e)}")
    # Create a simple Flask app as fallback
    from flask import Flask, jsonify
    app = Flask(__name__)

    @app.route('/')
    def home():
        return jsonify({"status": "error", "message": f"Error importing main app: {str(e)}"})

# This is required for Vercel serverless functions
if __name__ == '__main__':
    app.run()