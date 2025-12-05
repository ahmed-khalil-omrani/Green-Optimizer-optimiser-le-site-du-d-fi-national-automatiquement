const API_BASE_URL = 'http://localhost:8000';

/**
 * API Service for Green Optimizer Backend
 */
class ApiService {
    /**
     * Analyze a GitHub repository
     * @param {string} repoUrl - GitHub repository URL
     * @param {string} branch - Branch name (default: 'main')
     * @param {string|null} githubToken - Optional GitHub token
     * @returns {Promise<Object>} Analysis result
     */
    async analyzeRepository(repoUrl, branch = 'main', githubToken = null) {
        const response = await fetch(`${API_BASE_URL}/api/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                repo_url: repoUrl,
                branch: branch,
                github_token: githubToken
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Analysis failed');
        }

        return await response.json();
    }

    /**
     * Get analysis results by ID
     * @param {string} analysisId - Analysis ID
     * @returns {Promise<Object>} Analysis data
     */
    async getAnalysis(analysisId) {
        const response = await fetch(`${API_BASE_URL}/api/analysis/${analysisId}`);

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to fetch analysis');
        }

        return await response.json();
    }

    /**
     * Optimize repository files
     * @param {string} analysisId - Analysis ID
     * @param {Array<string>} optimizations - Types of optimizations to apply
     * @returns {Promise<Object>} Optimization result
     */
    async optimizeRepository(analysisId, optimizations = ['images', 'css', 'js', 'html']) {
        const response = await fetch(`${API_BASE_URL}/api/optimize`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                analysis_id: analysisId,
                optimizations: optimizations,
                create_pull_request: false
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Optimization failed');
        }

        return await response.json();
    }

    /**
     * Check API health
     * @returns {Promise<Object>} Health status
     */
    async checkHealth() {
        const response = await fetch(`${API_BASE_URL}/api/health`);
        return await response.json();
    }
}

export default new ApiService();
