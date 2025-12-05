import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import './GreenOptimizer.css';

const MainPage = () => {
    const navigate = useNavigate();
    const [repoUrl, setRepoUrl] = useState('');
    const [branch, setBranch] = useState('main');
    const [githubToken, setGithubToken] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleAnalyze = async () => {
        // Validate input
        if (!repoUrl.trim()) {
            setError('Veuillez entrer une URL de repository GitHub');
            return;
        }

        // Basic GitHub URL validation
        if (!repoUrl.includes('github.com')) {
            setError('Veuillez entrer une URL GitHub valide');
            return;
        }

        setError('');
        setLoading(true);

        try {
            // Call backend API
            const result = await api.analyzeRepository(repoUrl, branch, githubToken || null);

            // Navigate to report page with analysis data
            navigate('/report', {
                state: {
                    analysisId: result.analysis_id,
                    analysisData: result
                }
            });
        } catch (err) {
            console.error('Analysis failed:', err);
            setError(err.message || 'Une erreur est survenue lors de l\'analyse');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container">
            <header className="header">
                <h1 className="title">
                    Green Optimizer
                </h1>
                <p className="subtitle">Défi Nuit d'Info 🌙</p>
            </header>

            <main className="main-content">
                <h2 className="main-heading">
                    Optimisez l'empreinte carbone de votre projet web
                </h2>

                <div className="github-box">
                    <div className="input-group">
                        <label htmlFor="url-input" className="label">
                            Entrez l'URL du repository GitHub :
                        </label>
                        <input
                            id="url-input"
                            type="url"
                            placeholder="https://github.com/username/repository"
                            className="url-input"
                            value={repoUrl}
                            onChange={(e) => setRepoUrl(e.target.value)}
                            disabled={loading}
                            required
                        />
                        <small className="help-text">
                            Nous allons analyser les images, CSS, JS et calculer l'éco-score de ce repository.
                        </small>
                    </div>

                    <div className="input-group" style={{ marginTop: '15px' }}>
                        <label htmlFor="branch-input" className="label">
                            Branche (optionnel) :
                        </label>
                        <input
                            id="branch-input"
                            type="text"
                            placeholder="main"
                            className="url-input"
                            value={branch}
                            onChange={(e) => setBranch(e.target.value)}
                            disabled={loading}
                        />
                    </div>

                    <div className="input-group" style={{ marginTop: '15px' }}>
                        <label htmlFor="token-input" className="label">
                            GitHub Token (optionnel, recommandé) :
                        </label>
                        <input
                            id="token-input"
                            type="password"
                            placeholder="ghp_xxxxxxxxxxxx"
                            className="url-input"
                            value={githubToken}
                            onChange={(e) => setGithubToken(e.target.value)}
                            disabled={loading}
                        />
                        <small className="help-text">
                            Un token GitHub permet d'éviter les limites de taux de l'API.
                            <a href="https://github.com/settings/tokens" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--color-link)', marginLeft: '5px' }}>
                                Créer un token →
                            </a>
                        </small>
                    </div>

                    {error && (
                        <div style={{
                            marginTop: '15px',
                            padding: '12px',
                            backgroundColor: '#fcebeb',
                            color: '#e74c3c',
                            borderRadius: '6px',
                            fontSize: '0.9em'
                        }}>
                            {error.includes('403') || error.includes('rate limit') ? (
                                <span>
                                    ⚠️ <strong>Limite GitHub atteinte.</strong><br/>
                                    Vous avez dépassé le quota de requêtes anonymes (60/heure).<br/>
                                    Veuillez réessayer dans une heure.
                                </span>
                            ) : (
                                <span>⚠️ {error}</span>
                            )}
                        </div>
                    )}

                    <div className="button-center">
                        <button
                            id="analyze-button"
                            className="analyze-button"
                            onClick={handleAnalyze}
                            disabled={loading}
                            style={{
                                opacity: loading ? 0.6 : 1,
                                cursor: loading ? 'not-allowed' : 'pointer'
                            }}
                        >
                            {loading ? 'Analyse en cours... ⏳' : 'Analyser le Site 🚀'}
                        </button>
                    </div>
                </div>
            </main>
        </div>
    );
};

export default MainPage;

