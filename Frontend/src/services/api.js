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
    async analyzeRepository(repoUrl, branch = 'main') {
        const response = await fetch(`${API_BASE_URL}/api/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                repo_url: repoUrl,
                branch: branch,
                github_token: null
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
     * Optimize repository files (V3)
     * @param {string} analysisId - Analysis ID
     * @param {Object} options - Cleanup options
     * @returns {Promise<Object>} Job ID
     */
    async optimizeRepository(analysisId, options = {
        remove_comments: true,
        remove_whitespace: true,
        remove_unused_files: true,
        optimize_images: true,
        minify_code: true
    }) {
        const response = await fetch(`${API_BASE_URL}/api/optimize`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                analysis_id: analysisId,
                cleanup_options: options,
                output_format: 'zip'
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Optimization failed');
        }

        return await response.json();
    }

    /**
     * Get optimization status
     * @param {string} jobId - Job ID
     * @returns {Promise<Object>} Job status
     */
    async getOptimizationStatus(jobId) {
        const response = await fetch(`${API_BASE_URL}/api/optimize/status/${jobId}`);
        if (!response.ok) throw new Error('Failed to get status');
        return await response.json();
    }

    /**
     * Get download URL
     * @param {string} jobId - Job ID
     * @returns {string} Download URL
     */
    getDownloadUrl(jobId) {
        return `${API_BASE_URL}/api/optimize/download/${jobId}`;
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
