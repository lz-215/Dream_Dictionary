// Offline mode functionality for Dream Interpreter
// This provides basic functionality when the backend API is not available

// Basic dream symbols dictionary for offline mode
const offlineDreamSymbols = {
    "water": "Water often represents emotions, the unconscious, or a state of transition.",
    "flying": "Flying can symbolize freedom, escape, or a desire to rise above a situation.",
    "falling": "Falling may indicate insecurity, loss of control, or fear of failure.",
    "teeth": "Dreams about teeth can relate to anxiety, appearance, or communication issues.",
    "house": "A house typically represents the self, with different rooms symbolizing different aspects of your personality.",
    "car": "Cars often represent your direction in life, personal drive, or how you present yourself to others.",
    "death": "Death in dreams usually symbolizes transformation, endings, or change rather than literal death.",
    "snake": "Snakes can represent wisdom, transformation, healing, or hidden fears.",
    "baby": "Babies often symbolize new beginnings, innocence, or aspects of yourself that are vulnerable.",
    "money": "Money can represent self-worth, power, or how you value yourself and others."
};

// Offline dream interpretation function
function interpretDreamOffline(dreamText) {
    const dreamLower = dreamText.toLowerCase();
    const results = [];
    
    // Check for matches with our basic symbol dictionary
    for (const [symbol, interpretation] of Object.entries(offlineDreamSymbols)) {
        if (dreamLower.includes(symbol)) {
            results.push({
                keyword: symbol.charAt(0).toUpperCase() + symbol.slice(1),
                interpretation: interpretation
            });
        }
    }
    
    // If no symbols were found, provide a generic response
    if (results.length === 0) {
        results.push({
            keyword: "General",
            interpretation: "Your dream contains elements that may represent your subconscious thoughts. Dreams are highly personal, and you might want to consider what these symbols mean specifically to you."
        });
    }
    
    // Generate a simple summary
    let dreamSummary = "Your dream appears to involve ";
    if (results.length > 1) {
        const keywords = results.map(r => r.keyword.toLowerCase());
        dreamSummary += keywords.slice(0, -1).join(', ') + ' and ' + keywords[keywords.length - 1] + '.';
    } else {
        dreamSummary += results[0].keyword.toLowerCase() + '.';
    }
    
    // Generate a psychological perspective
    const psychPerspective = "From a psychological perspective, this dream may reflect your current emotional state or recent experiences. " +
        "Consider how the symbols in your dream might connect to your waking life and what emotions they evoke.";
    
    return {
        dream_summary: dreamSummary,
        interpretations: results,
        psychological_perspective: psychPerspective,
        model_used: "offline_basic",
        processing_time: "0.01s"
    };
}

// Mock API functions for offline mode
const offlineAPI = {
    // Mock model status endpoint
    getModelStatus: function() {
        return {
            model_available: false,
            model_type: "Offline Mode",
            features: [
                "Basic keyword matching",
                "Limited symbol dictionary",
                "No machine learning capabilities"
            ]
        };
    },
    
    // Mock interpret endpoint
    interpretDream: function(dreamText, userId) {
        return interpretDreamOffline(dreamText);
    },
    
    // Mock history endpoint
    getDreamHistory: function(userId) {
        // Return empty history in offline mode
        return { history: [] };
    },
    
    // Mock stats endpoint
    getDreamStats: function() {
        return {
            total_dreams: 0,
            top_symbols: [],
            dreams_by_day: {}
        };
    }
};