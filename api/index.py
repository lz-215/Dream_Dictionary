import sys
import os

# Add the backend directory to the path so we can import from it
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Import the Flask app from the backend
from app import app

# This is required for Vercel serverless functions
if __name__ == '__main__':
    app.run()
