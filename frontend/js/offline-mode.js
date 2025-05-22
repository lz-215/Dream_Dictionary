// Offline mode functionality for Dream Interpreter
// This provides basic functionality when the backend API is not available

// Offline mode dictionary and functions
const offlineDreamSymbols = {
    "water": "Water in dreams often symbolizes emotions, the unconscious mind, or the flow of life. Clear water may represent clarity and peace, while turbulent water might indicate emotional turmoil.",
    "flying": "Flying in dreams usually represents freedom, transcending limitations, or gaining a new perspective. It can also indicate a desire to escape from something in your waking life.",
    "falling": "Falling in dreams often relates to insecurity, anxiety, or feeling out of control. It might reflect a situation in your life where you feel you're losing your footing.",
    "teeth": "Dreams about teeth, especially losing teeth, commonly symbolize anxiety about appearance, communication issues, or fear of loss. It might reflect concerns about how others perceive you.",
    "chase": "Being chased in dreams typically represents avoiding an issue or person in your waking life. The pursuer often embodies a fear or problem you're reluctant to confront.",
    "house": "Houses in dreams often represent the self, with different rooms symbolizing different aspects of your personality or life. The condition of the house may reflect your self-image.",
    "death": "Death in dreams rarely predicts actual death. Instead, it typically symbolizes the end of one phase and the beginning of another, representing transformation and change.",
    "naked": "Being naked or inappropriately dressed in public in dreams often reflects vulnerability, shame, or fear of being exposed. It might indicate feeling unprepared for a situation.",
    "exam": "Dreams about taking or failing exams commonly relate to self-evaluation, fear of failure, or feeling tested in some aspect of your life. They may reflect performance anxiety.",
    "snake": "Snakes in dreams can have multiple meanings, including transformation (shedding skin), healing, wisdom, or hidden threats. Cultural context often influences this symbol's interpretation.",
    "money": "Money in dreams often represents self-worth, power, or life energy rather than literal financial concerns. Finding money might suggest discovering your inner resources.",
    "baby": "Babies in dreams frequently symbolize new beginnings, innocence, or creative potential. They might represent a new project, relationship, or aspect of yourself developing.",
    "car": "Cars in dreams typically represent your direction in life and your ability to control your journey. Car problems might reflect obstacles or lack of control in your life path.",
    "ocean": "The ocean in dreams often symbolizes the unconscious mind, overwhelming emotions, or the vastness of possibilities. Your interaction with the ocean reflects your relationship with these elements.",
    "fire": "Fire in dreams can represent transformation, passion, destruction, or purification. The context of the fire and your feelings about it in the dream are important for interpretation.",
    "food": "Food in dreams often relates to nourishment, not just physical but emotional and spiritual. It can represent what you're 'consuming' mentally or the need for sustenance in some area of life.",
    "bird": "Birds in dreams frequently symbolize freedom, perspective, or spiritual messages. Different types of birds or their behaviors can add specific meanings to the interpretation.",
    "door": "Doors in dreams often represent opportunities, transitions, or access to new aspects of yourself. Locked doors might indicate perceived limitations or hidden potential.",
    "mountain": "Mountains in dreams typically represent challenges, obstacles to overcome, or spiritual quests. Climbing a mountain might symbolize your determination and ambition.",
    "spider": "Spiders in dreams can symbolize creativity, female energy, or feeling entangled in a web of circumstances. Fear of spiders might reflect fear of a powerful feminine figure or manipulative aspects of life."
};

// Function to interpret dreams offline
function interpretDreamOffline(dreamText) {
    console.log("Interpreting dream offline:", dreamText);
    
    // Split the dream text into words and check for matches with our symbol dictionary
    const dreamWords = dreamText.toLowerCase().replace(/[.,\/#!$%\^&\*;:{}=\-_`~()]/g, "").split(/\s+/);
    const foundSymbols = [];
    
    dreamWords.forEach(word => {
        if (offlineDreamSymbols[word]) {
            // Only add unique symbols
            if (!foundSymbols.some(item => item.symbol === word)) {
                foundSymbols.push({
                    symbol: word,
                    interpretation: offlineDreamSymbols[word]
                });
            }
        }
    });
    
    // Generate a summary interpretation
    let summary = "Based on the symbols in your dream, ";
    
    if (foundSymbols.length === 0) {
        summary += "I couldn't identify any common dream symbols. Your dream may contain personal symbols unique to you.";
    } else if (foundSymbols.length === 1) {
        summary += `the presence of '${foundSymbols[0].symbol}' suggests ${foundSymbols[0].interpretation.split('.')[0].toLowerCase()}.`;
    } else {
        summary += "there are several key elements to consider:\n\n";
        foundSymbols.forEach(item => {
            summary += `• The '${item.symbol}' in your dream might represent ${item.interpretation.split('.')[0].toLowerCase()}.\n`;
        });
    }
    
    // Generate a psychological perspective
    let psychPerspective = "";
    
    if (foundSymbols.length > 0) {
        psychPerspective = "From a psychological perspective, your dream might be processing ";
        
        if (foundSymbols.some(item => ["water", "ocean"].includes(item.symbol))) {
            psychPerspective += "deep emotions or unconscious thoughts. ";
        } else if (foundSymbols.some(item => ["flying", "bird"].includes(item.symbol))) {
            psychPerspective += "a desire for freedom or transcendence. ";
        } else if (foundSymbols.some(item => ["falling", "chase"].includes(item.symbol))) {
            psychPerspective += "anxiety or fear in your waking life. ";
        } else if (foundSymbols.some(item => ["house", "door", "mountain"].includes(item.symbol))) {
            psychPerspective += "personal growth and self-discovery. ";
        } else if (foundSymbols.some(item => ["death", "fire"].includes(item.symbol))) {
            psychPerspective += "transformation or significant life changes. ";
        } else {
            psychPerspective += "various aspects of your personal experiences and emotions. ";
        }
        
        psychPerspective += "Consider how these symbols relate to your current life situation.";
    }
    
    return {
        summary: summary,
        symbols: foundSymbols,
        psychological_perspective: psychPerspective,
        is_offline: true
    };
}

// Mock API functions for offline mode
function getModelStatus() {
    return {
        status: "offline",
        message: "Currently in offline mode. Using local dream dictionary for interpretations."
    };
}

function interpretDream(dreamText) {
    return new Promise((resolve) => {
        setTimeout(() => {
            resolve(interpretDreamOffline(dreamText));
        }, 1000); // Simulate a short delay
    });
}

function getDreamHistory(page = 1, perPage = 10) {
    return {
        items: [],
        total_items: 0,
        total_pages: 0,
        current_page: 1
    };
}

function getDreamStats() {
    return {
        total_dreams: 0,
        common_keywords: [],
        last_week_count: 0,
        personal_stats: false
    };
}