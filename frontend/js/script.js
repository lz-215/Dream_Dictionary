document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const dreamInput = document.getElementById('dreamInput');
    const interpretButton = document.getElementById('interpretButton');
    const clearButton = document.getElementById('clearButton');
    const resultsSection = document.getElementById('results');
    const dreamHistory = document.getElementById('dreamHistory');
    const dreamStats = document.getElementById('dreamStats');

    // Model status
    let modelAvailable = false;
    let modelType = "Basic Keyword Matching";

    // Check model status on load
    checkModelStatus();

    // Navigation Elements
    const navHome = document.getElementById('navHome');
    const navHistory = document.getElementById('navHistory');
    const navStats = document.getElementById('navStats');
    const navAbout = document.getElementById('navAbout');

    // Page Sections
    const homeSection = document.getElementById('homeSection');
    const historySection = document.getElementById('historySection');
    const statsSection = document.getElementById('statsSection');
    const aboutSection = document.getElementById('aboutSection');

    // Modal Elements
    const privacyLink = document.getElementById('privacyLink');
    const termsLink = document.getElementById('termsLink');
    const contactLink = document.getElementById('contactLink');
    const privacyModal = document.getElementById('privacyModal');
    const termsModal = document.getElementById('termsModal');
    const contactModal = document.getElementById('contactModal');
    const closeModal = document.querySelector('.close');
    const termsCloseModal = document.querySelector('.terms-close');
    const contactCloseModal = document.querySelector('.contact-close');

    // User ID (for history tracking)
    const userId = generateUserId();

    // Event Listeners
    interpretButton.addEventListener('click', interpretDream);
    clearButton.addEventListener('click', clearDreamInput);

    // Navigation Event Listeners
    navHome.addEventListener('click', () => showSection(homeSection, navHome));
    navHistory.addEventListener('click', () => {
        showSection(historySection, navHistory);
        loadDreamHistory();
    });
    navStats.addEventListener('click', () => {
        showSection(statsSection, navStats);
        loadDreamStats();
    });
    navAbout.addEventListener('click', () => showSection(aboutSection, navAbout));

    // Modal Event Listeners
    privacyLink.addEventListener('click', showPrivacyModal);
    closeModal.addEventListener('click', hidePrivacyModal);
    window.addEventListener('click', (event) => {
        if (event.target === privacyModal) {
            hidePrivacyModal();
        }
    });

    // Additional footer link handlers
    termsLink.addEventListener('click', function(e) {
        e.preventDefault();
        showTermsModal();
    });

    contactLink.addEventListener('click', function(e) {
        e.preventDefault();
        showContactModal();
    });

    termsCloseModal.addEventListener('click', hideTermsModal);
    contactCloseModal.addEventListener('click', hideContactModal);

    window.addEventListener('click', (event) => {
        if (event.target === termsModal) {
            hideTermsModal();
        }
        if (event.target === contactModal) {
            hideContactModal();
        }
    });

    // Functions
    async function checkModelStatus() {
        try {
            const response = await fetch(`${currentConfig.apiBaseUrl}/model-status`);
            if (response.ok) {
                const data = await response.json();
                modelAvailable = data.model_available;
                modelType = data.model_type;
                console.log(`Model status: ${modelType} (Available: ${modelAvailable})`);

                // Update about section with model info if it exists
                const aboutModelSection = document.getElementById('modelInfo');
                if (aboutModelSection) {
                    aboutModelSection.innerHTML = `
                        <h4>Dream Engine Status</h4>
                        <p>Currently using: <strong>${modelType}</strong></p>
                        <ul>
                            ${data.features.map(feature => `<li>${feature}</li>`).join('')}
                        </ul>
                    `;
                }
            }
        } catch (error) {
            console.error('Error checking model status:', error);
            // Handle offline mode or API unavailability
            const aboutModelSection = document.getElementById('modelInfo');
            if (aboutModelSection) {
                aboutModelSection.innerHTML = `
                    <h4>Dream Engine Status</h4>
                    <p>Currently using: <strong>Offline Mode</strong></p>
                    <p>The dream analysis engine is currently running in offline mode with basic functionality.</p>
                `;
            }
            modelAvailable = false;
            modelType = "Offline Mode";
        }
    }

    async function interpretDream() {
        const dreamText = dreamInput.value.trim();

        if (!dreamText) {
            alert('Please describe your dream first.');
            return;
        }

        // Show loading state
        resultsSection.style.display = 'block';
        resultsSection.innerHTML = '<div class="loading"><i class="fas fa-spinner fa-spin"></i> Analyzing your dream...</div>';

        try {
            let data;

            // Try to use the backend API
            try {
                const response = await fetch(`${currentConfig.apiBaseUrl}/interpret`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        dream_text: dreamText,
                        user_id: userId,
                        use_ml: modelAvailable,
                        model_preference: 'auto'
                    }),
                    // Set a timeout to fail fast if the API is not available
                    signal: AbortSignal.timeout(5000)
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                data = await response.json();
            } catch (apiError) {
                console.warn('API error, falling back to offline mode:', apiError);
                // Fall back to offline mode
                data = offlineAPI.interpretDream(dreamText, userId);
            }

            displayResults(data);

        } catch (error) {
            console.error('Error:', error);
            resultsSection.innerHTML = `
                <div class="result-section">
                    <h3><i class="fas fa-exclamation-circle"></i> Error</h3>
                    <p>Sorry, we couldn't interpret your dream. Please try again later.</p>
                </div>
            `;
        }
    }

    function displayResults(data) {
        resultsSection.innerHTML = '';

        // Dream Summary
        const summarySection = document.createElement('div');
        summarySection.className = 'result-section';
        summarySection.innerHTML = `
            <h3><i class="fas fa-quote-left"></i> Dream Summary</h3>
            <p>${data.dream_summary}</p>
        `;
        resultsSection.appendChild(summarySection);

        // Interpretations
        const interpretationsSection = document.createElement('div');
        interpretationsSection.className = 'result-section';
        interpretationsSection.innerHTML = `<h3><i class="fas fa-key"></i> Symbol Interpretations</h3>`;

        if (data.interpretations.length === 0) {
            interpretationsSection.innerHTML += `<p>No specific symbols were identified in your dream.</p>`;
        } else {
            // Create a more structured display for interpretations
            const symbolsContainer = document.createElement('div');
            symbolsContainer.className = 'symbols-container';

            data.interpretations.forEach(item => {
                const interpDiv = document.createElement('div');
                interpDiv.className = 'symbol-card';
                interpDiv.innerHTML = `
                    <h4 class="keyword">Symbol: ${item.keyword}</h4>
                    <p class="interpretation">${item.interpretation}</p>
                `;
                symbolsContainer.appendChild(interpDiv);
            });

            interpretationsSection.appendChild(symbolsContainer);
        }

        resultsSection.appendChild(interpretationsSection);

        // Psychological Perspective
        const psychSection = document.createElement('div');
        psychSection.className = 'result-section';
        psychSection.innerHTML = `
            <h3><i class="fas fa-brain"></i> Psychological Perspective</h3>
            <div class="psych-content">
                <p>${data.psychological_perspective}</p>
            </div>
        `;
        resultsSection.appendChild(psychSection);

        // Add reflection questions section
        const reflectionSection = document.createElement('div');
        reflectionSection.className = 'result-section';
        reflectionSection.innerHTML = `
            <h3><i class="fas fa-lightbulb"></i> Reflection Questions</h3>
            <ul class="reflection-questions">
                <li>How do the symbols in this dream connect to your current life situation?</li>
                <li>What emotions did you feel during the dream, and how might they relate to your waking emotions?</li>
                <li>If you could continue this dream or change its outcome, what would happen next?</li>
            </ul>
        `;
        resultsSection.appendChild(reflectionSection);


        // Share Options
        const shareSection = document.createElement('div');
        shareSection.className = 'result-section';
        shareSection.innerHTML = `
            <h3><i class="fas fa-share-alt"></i> Share Your Interpretation</h3>
            <div class="share-buttons">
                <button onclick="shareOnTwitter()" class="share-button twitter"><i class="fab fa-twitter"></i> Twitter</button>
                <button onclick="shareOnFacebook()" class="share-button facebook"><i class="fab fa-facebook-f"></i> Facebook</button>
                <button onclick="copyInterpretation()" class="share-button copy"><i class="fas fa-copy"></i> Copy</button>
            </div>
        `;
        resultsSection.appendChild(shareSection);

        // Model info
        const modelInfoSection = document.createElement('div');
        modelInfoSection.className = 'result-section model-info';

        // Determine model badge class and icon based on model_used
        let modelBadgeClass = 'basic-model';
        let modelIcon = 'fas fa-book';
        let modelText = 'Basic Keyword Matching';

        if (data.model_used === 'bert') {
            modelBadgeClass = 'bert-model';
            modelIcon = 'fas fa-microchip';
            modelText = 'BERT Neural Network Analysis';
        } else if (data.model_used === 'transformer') {
            modelBadgeClass = 'transformer-model';
            modelIcon = 'fas fa-network-wired';
            modelText = 'Transformer Neural Network Analysis';
        } else if (data.model_used === 'deep_learning') {
            modelBadgeClass = 'ai-model';
            modelIcon = 'fas fa-robot';
            modelText = 'Deep Learning Analysis';
        } else if (data.model_used === 'enhanced_analyzer') {
            modelBadgeClass = 'enhanced-model';
            modelIcon = 'fas fa-brain';
            modelText = 'Enhanced Dream Analysis';
        }

        modelInfoSection.innerHTML = `
            <p class="model-badge ${modelBadgeClass}">
                <i class="${modelIcon}"></i>
                ${modelText}
            </p>
        `;
        resultsSection.appendChild(modelInfoSection);

        // Disclaimer reminder
        const disclaimerSection = document.createElement('div');
        disclaimerSection.className = 'result-section';
        disclaimerSection.innerHTML = `
            <p><em>Reminder: Dream interpretations are subjective and should be considered alongside your personal experiences and feelings.</em></p>
        `;
        resultsSection.appendChild(disclaimerSection);

        // Make results visible
        resultsSection.style.display = 'block';

        // Add share functionality to window
        window.shareOnTwitter = function() {
            const text = `I just interpreted my dream about ${data.dream_summary} using Dream Interpreter!`;
            const url = window.location.href;
            window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(url)}`, '_blank');
        };

        window.shareOnFacebook = function() {
            const url = window.location.href;
            window.open(`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`, '_blank');
        };

        window.copyInterpretation = function() {
            const summary = `Dream: ${data.dream_summary}\n\n`;

            let symbols = 'Symbols:\n';
            data.interpretations.forEach(item => {
                symbols += `- ${item.keyword}: ${item.interpretation}\n`;
            });

            const perspective = `\nPsychological Perspective:\n${data.psychological_perspective}\n`;

            const reflections = `\nReflection Questions:\n` +
                `- How do the symbols in this dream connect to your current life situation?\n` +
                `- What emotions did you feel during the dream, and how might they relate to your waking emotions?\n` +
                `- If you could continue this dream or change its outcome, what would happen next?\n`;

            const disclaimer = `\nReminder: Dream interpretations are subjective and should be considered alongside your personal experiences and feelings.`;

            const fullText = summary + symbols + perspective + reflections + disclaimer;

            navigator.clipboard.writeText(fullText).then(() => {
                alert('Interpretation copied to clipboard!');
            }).catch(err => {
                console.error('Could not copy text: ', err);
            });
        };
    }

    function clearDreamInput() {
        dreamInput.value = '';
        resultsSection.style.display = 'none';
        dreamInput.focus();
    }

    async function loadDreamHistory() {
        dreamHistory.innerHTML = '<p class="loading"><i class="fas fa-spinner fa-spin"></i> Loading your dream history...</p>';

        try {
            const response = await fetch(`${currentConfig.apiBaseUrl}/history?user_id=${userId}&limit=10`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            displayDreamHistory(data.history);

        } catch (error) {
            console.error('Error:', error);
            dreamHistory.innerHTML = `
                <p>Sorry, we couldn't load your dream history. Please try again later.</p>
            `;
        }
    }

    function displayDreamHistory(history) {
        if (!history || history.length === 0) {
            dreamHistory.innerHTML = `
                <p>You haven't interpreted any dreams yet. Go to the home page to interpret your first dream!</p>
            `;
            return;
        }

        dreamHistory.innerHTML = '';

        history.forEach(item => {
            const date = new Date(item.timestamp);
            const formattedDate = date.toLocaleDateString() + ' ' + date.toLocaleTimeString();

            const dreamCard = document.createElement('div');
            dreamCard.className = 'dream-card';

            // Create a truncated version of the dream text
            const dreamText = item.dream_text.length > 150
                ? item.dream_text.substring(0, 150) + '...'
                : item.dream_text;

            // Create symbol tags
            let symbolsHtml = '';
            if (item.interpretations && item.interpretations.length > 0) {
                symbolsHtml = '<div class="symbols">';
                item.interpretations.forEach(interp => {
                    symbolsHtml += `<span class="symbol-tag">${interp.keyword}</span>`;
                });
                symbolsHtml += '</div>';
            }

            dreamCard.innerHTML = `
                <h3>Dream Interpretation</h3>
                <p class="date">${formattedDate}</p>
                <p class="dream-text">${dreamText}</p>
                ${symbolsHtml}
            `;

            dreamHistory.appendChild(dreamCard);
        });
    }

    async function loadDreamStats() {
        dreamStats.innerHTML = '<p class="loading"><i class="fas fa-spinner fa-spin"></i> Loading dream statistics...</p>';

        try {
            const response = await fetch(`${currentConfig.apiBaseUrl}/stats`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            displayDreamStats(data);

        } catch (error) {
            console.error('Error:', error);
            dreamStats.innerHTML = `
                <p>Sorry, we couldn't load dream statistics. Please try again later.</p>
            `;
        }
    }

    function displayDreamStats(stats) {
        dreamStats.innerHTML = '';

        // Total Dreams Card
        const totalDreamsCard = document.createElement('div');
        totalDreamsCard.className = 'stats-card';
        totalDreamsCard.innerHTML = `
            <h3><i class="fas fa-chart-line"></i> Dream Count</h3>
            <div class="stats-item">
                <span class="stats-label">Total Dreams Interpreted:</span>
                <span class="stats-value">${stats.total_dreams}</span>
            </div>
        `;
        dreamStats.appendChild(totalDreamsCard);

        // Top Symbols Card
        const topSymbolsCard = document.createElement('div');
        topSymbolsCard.className = 'stats-card';
        topSymbolsCard.innerHTML = `<h3><i class="fas fa-star"></i> Most Common Dream Symbols</h3>`;

        if (stats.top_symbols && stats.top_symbols.length > 0) {
            stats.top_symbols.forEach(([symbol, count]) => {
                const symbolItem = document.createElement('div');
                symbolItem.className = 'stats-item';
                symbolItem.innerHTML = `
                    <span class="stats-label">${symbol}</span>
                    <span class="stats-value">${count}</span>
                `;
                topSymbolsCard.appendChild(symbolItem);
            });
        } else {
            topSymbolsCard.innerHTML += `<p>No symbol data available yet.</p>`;
        }

        dreamStats.appendChild(topSymbolsCard);

        // Dreams by Day Card
        const dreamsByDayCard = document.createElement('div');
        dreamsByDayCard.className = 'stats-card';
        dreamsByDayCard.innerHTML = `<h3><i class="fas fa-calendar-alt"></i> Dreams by Day of Week</h3>`;

        if (stats.dreams_by_day && Object.keys(stats.dreams_by_day).length > 0) {
            const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

            days.forEach(day => {
                const count = stats.dreams_by_day[day] || 0;
                const dayItem = document.createElement('div');
                dayItem.className = 'stats-item';
                dayItem.innerHTML = `
                    <span class="stats-label">${day}</span>
                    <span class="stats-value">${count}</span>
                `;
                dreamsByDayCard.appendChild(dayItem);
            });
        } else {
            dreamsByDayCard.innerHTML += `<p>No day-of-week data available yet.</p>`;
        }

        dreamStats.appendChild(dreamsByDayCard);
    }

    function showSection(section, navItem) {
        // Hide all sections
        const sections = document.querySelectorAll('.page-section');
        sections.forEach(s => s.classList.remove('active'));

        // Remove active class from all nav items
        const navItems = document.querySelectorAll('nav a');
        navItems.forEach(item => item.classList.remove('active'));

        // Show selected section and mark nav item as active
        section.classList.add('active');
        navItem.classList.add('active');
    }

    function showPrivacyModal() {
        privacyModal.style.display = 'block';
    }

    function hidePrivacyModal() {
        privacyModal.style.display = 'none';
    }

    function showTermsModal() {
        termsModal.style.display = 'block';
    }

    function hideTermsModal() {
        termsModal.style.display = 'none';
    }

    function showContactModal() {
        contactModal.style.display = 'block';
    }

    function hideContactModal() {
        contactModal.style.display = 'none';
    }

    function generateUserId() {
        // Check if user ID exists in localStorage
        let userId = localStorage.getItem('dreamInterpreterUserId');

        // If not, create a new one
        if (!userId) {
            userId = 'user_' + Math.random().toString(36).substring(2, 15);
            localStorage.setItem('dreamInterpreterUserId', userId);
        }

        return userId;
    }
});