// Configuration for different environments
const config = {
    // Development environment (local)
    development: {
        apiBaseUrl: 'http://localhost:5000/api'
    },
    // Production environment (Cloudflare Pages)
    production: {
        apiBaseUrl: 'https://your-backend-api-url.com/api' // This will need to be updated with your actual backend API URL
    }
};

// Determine current environment
const currentEnvironment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
    ? 'development' 
    : 'production';

// Export the configuration for the current environment
const currentConfig = config[currentEnvironment];

console.log(`Running in ${currentEnvironment} environment`);
