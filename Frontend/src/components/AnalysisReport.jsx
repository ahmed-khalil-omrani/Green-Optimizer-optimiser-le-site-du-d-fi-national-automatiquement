import React from 'react';
import { useNavigate } from 'react-router-dom';
import './AnalysisReport.css';

const AnalysisReport = () => {
    const navigate = useNavigate();

    return (
        <div className="analysis-report-container">
            {/* HEADER ET SCORE GLOBAL */}
            <header className="report-header">
                <button className="back-button" onClick={() => navigate(-1)}>
                    <i className="fas fa-arrow-left"></i> Retour
                </button>
                <h1 className="report-title">
                    <span className="green-text">Rapport d'Analyse</span>
                </h1>
                <p className="url-text">pour https://votre-site-a-optimiser.com</p>
                <p className="date-text">Généré le: 29 novembre 2024</p>
            </header>

            {/* SECTION SCORE */}
            <div className="score-container">
                <div className="score-item">
                    <p className="score-label">EcoIndex</p>
                    <span className="score-value eco-index">B</span>
                </div>
                <div className="score-item">
                    <p className="score-label">Lighthouse (Performance)</p>
                    <span className="score-value performance">85/100</span>
                </div>
                <div className="score-item">
                    <p className="score-label">Potentiel de Réduction</p>
                    <span className="score-value status">7.2 Mo</span>
                </div>
            </div>

            {/* SECTION DÉTAILS */}
            <h2 className="section-title">Détails et Potentiel d'Optimisation</h2>

            {/* BLOC 1: IMAGES */}
            <div className="area-container">
                <div className="area-header">
                    <h3 className="area-title"><i className="fas fa-image"></i> Images (Assets)</h3>
                    <span className="improvement-pill">Amélioration: 70%</span>
                </div>
                <p className="summary-text">
                    Taille Actuelle Totale: 20.00 Mo &rarr; Taille Optimale: 6.00 Mo
                </p>

                <table className="details-table">
                    <thead>
                        <tr>
                            <th>Fichier</th>
                            <th>Taille Actuelle</th>
                            <th>Taille Optimale</th>
                            <th>Suggestion d'Optimisation</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td data-label="Fichier" className="td-filename">hero-banner.jpg</td>
                            <td data-label="Taille Actuelle">5.00 Mo</td>
                            <td data-label="Taille Optimale" className="td-optimal-size">1.00 Mo</td>
                            <td data-label="Suggestion" className="td-suggestion">Convertir en AVIF (format de nouvelle génération)</td>
                        </tr>
                        <tr>
                            <td data-label="Fichier" className="td-filename">logo-highres.png</td>
                            <td data-label="Taille Actuelle">800 Ko</td>
                            <td data-label="Taille Optimale" className="td-optimal-size">200 Ko</td>
                            <td data-label="Suggestion" className="td-suggestion">Convertir en WebP (avec compression)</td>
                        </tr>
                        <tr>
                            <td data-label="Fichier" className="td-filename">background-texture.jpg</td>
                            <td data-label="Taille Actuelle">13.5 Mo</td>
                            <td data-label="Taille Optimale" className="td-optimal-size">4.62 Mo</td>
                            <td data-label="Suggestion" className="td-suggestion">Redimensionner et optimiser la qualité JPEG</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            {/* BLOC 2: FICHIERS STATIQUES */}
            <div className="area-container">
                <div className="area-header">
                    <h3 className="area-title"><i className="fas fa-code"></i> Fichiers Statiques (CSS/JS)</h3>
                    <span className="improvement-pill pill-danger">Amélioration: 50%</span>
                </div>
                <p className="summary-text">
                    Taille Actuelle Totale: 512 Ko &rarr; Taille Optimale: 256 Ko
                </p>

                <table className="details-table">
                    <thead>
                        <tr>
                            <th>Fichier</th>
                            <th>Taille Actuelle</th>
                            <th>Taille Optimale</th>
                            <th>Suggestion d'Optimisation</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td data-label="Fichier" className="td-filename">app.css</td>
                            <td data-label="Taille Actuelle">250 Ko</td>
                            <td data-label="Taille Optimale" className="td-optimal-size">125 Ko</td>
                            <td data-label="Suggestion" className="td-suggestion">Minification et purge des classes inutilisées</td>
                        </tr>
                        <tr>
                            <td data-label="Fichier" className="td-filename">vendor.js</td>
                            <td data-label="Taille Actuelle">262 Ko</td>
                            <td data-label="Taille Optimale" className="td-optimal-size">131 Ko</td>
                            <td data-label="Suggestion" className="td-suggestion">Minification et suppression des commentaires/logs</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            {/* BLOC 3: RESSOURCES INUTILISÉES */}
            <div className="area-container">
                <div className="area-header">
                    <h3 className="area-title"><i className="fas fa-trash-alt"></i> Ressources Inutilisées (Dead Code)</h3>
                    <span className="improvement-pill pill-warning">Amélioration: 100%</span>
                </div>
                <p className="summary-text">
                    Taille Actuelle Totale: 300 Ko &rarr; Taille Optimale: 0 Ko
                </p>

                <table className="details-table">
                    <thead>
                        <tr>
                            <th>Fichier</th>
                            <th>Taille Actuelle</th>
                            <th>Taille Optimale</th>
                            <th>Suggestion d'Optimisation</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td data-label="Fichier" className="td-filename">old-styles.css</td>
                            <td data-label="Taille Actuelle">300 Ko</td>
                            <td data-label="Taille Optimale" className="td-optimal-size">0 Ko</td>
                            <td data-label="Suggestion" className="td-suggestion">Supprimer entièrement du build</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            {/* BOUTON D'ACTION FINALE */}
            <footer className="footer">
                <button className="optimize-button" onClick={() => console.log('Optimizing...')}>
                    <i className="fas fa-leaf"></i> Lancer l'Optimisation Automatique
                </button>
            </footer>
        </div>
    );
};

export default AnalysisReport;
