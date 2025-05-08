// Configuration for different environments
const config = {
    // Development environment (local)
    development: {
        apiBaseUrl: 'http://localhost:5000/api'
    },
    // Production environment (Vercel)
    production: {
        apiBaseUrl: '/api' // 相对路径，指向同一域名下的API
    }
};

// Determine current environment
const currentEnvironment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'development'
    : 'production';

// Export the configuration for the current environment
const currentConfig = config[currentEnvironment];

console.log(`Running in ${currentEnvironment} environment`);
