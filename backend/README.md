# Dream Interpreter Backend

This directory contains the backend code for the Dream Interpreter application. The backend is built with Flask and provides API endpoints for dream interpretation using various machine learning models.

## Optimization Improvements

The backend has been optimized with the following improvements:

1. **Modular Architecture**
   - Created separate model service layer for better code organization
   - Implemented clear separation of concerns between API and model handling

2. **Performance Optimizations**
   - Added multi-level caching for dream interpretations
   - Implemented async model loading for faster startup
   - Optimized keyword matching algorithms 
   - Reduced memory usage in model initialization

3. **Error Handling**
   - Comprehensive error logging with proper exception handling
   - Graceful fallbacks when models fail to load
   - Structured error responses for better client handling

4. **Memory Management**
   - Implemented LRU caching with size limits to prevent memory leaks
   - Optimized TensorFlow memory usage with mixed precision
   - Added cache cleanup mechanisms

5. **API Improvements**
   - Added pagination for history endpoint
   - Created model status endpoint for monitoring
   - Implemented cache clearing and model reloading endpoints

## Setup Instructions

### Prerequisites

- Python 3.8+ 
- Pip package manager

### Installation

1. Create a virtual environment:
   ```
   python -m venv venv
   ```

2. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Install deep learning libraries (optional):
   ```
   python install_dl_libraries.py
   ```

### Running the Server

Start the development server:
```
python app.py
```

For production deployment, use Gunicorn:
```
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## API Endpoints

- **POST /api/interpret** - Interpret a dream
- **GET /api/history** - Get dream interpretation history
- **GET /api/stats** - Get usage statistics
- **GET /api/model-status** - Get model status information
- **POST /api/clear-cache** - Clear the interpretation cache
- **POST /api/reload-models** - Reload all models

## Architecture

The backend follows a modular architecture:

- **app.py** - Flask application with API endpoints
- **model_service.py** - Service layer managing models and caching
- **dream_model.py** - Deep learning model for dream interpretation
- **dream_analyzer.py** - Enhanced dream analyzer with pattern matching
- **dream_transformer.py** - Transformer-based dream analyzer
- **dream_bert.py** - BERT-based dream analyzer

## Memory Management

The application implements several strategies to manage memory efficiently:

1. Lazy loading of models
2. Model sharing between requests
3. Cache size limitations
4. Background cache cleanup
5. Mixed precision in TensorFlow operations

## Error Handling

The application uses proper error handling with:

1. Structured logging
2. Graceful degradation when models fail
3. Proper HTTP status codes for errors
4. Detailed error messages for debugging

## Performance Monitoring

Key performance metrics are logged:

1. Model initialization time
2. Request processing time
3. Memory usage for large operations
4. Cache hit/miss ratios 