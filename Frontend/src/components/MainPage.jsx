import React from 'react';
import { useNavigate } from 'react-router-dom';
import './GreenOptimizer.css';

const MainPage = () => {
    const navigate = useNavigate();

    const handleAnalyze = () => {
        navigate('/report');
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
                            Entrez l'URL du site web à analyser (Ex: site.com) :
                        </label>
                        <input
                            id="url-input"
                            type="url"
                            placeholder="https://votre-site-a-optimiser.com"
                            className="url-input"
                            required
                        />
                        <small className="help-text">
                            Nous allons mesurer le poids, les requêtes et l'éco-score de cette URL en utilisant EcoIndex/Lighthouse.
                        </small>
                    </div>

                    <div className="button-center">
                        <button
                            id="analyze-button"
                            className="analyze-button"
                            onClick={handleAnalyze}
                        >
                            Analyser le Site 🚀
                        </button>
                    </div>
                </div>
            </main>
        </div>
    );
};

export default MainPage;
