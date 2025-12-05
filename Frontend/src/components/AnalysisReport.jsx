import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import api from '../services/api';
import './AnalysisReport.css';

const AnalysisReport = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const [analysisData, setAnalysisData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchAnalysisData = async () => {
            try {
                // Get data from navigation state or fetch from API
                if (location.state?.analysisData) {
                    setAnalysisData(location.state.analysisData);
                    setLoading(false);
                } else if (location.state?.analysisId) {
                    const data = await api.getAnalysis(location.state.analysisId);
                    setAnalysisData(data);
                    setLoading(false);
                } else {
                    setError('Aucune donnée d\'analyse disponible');
                    setLoading(false);
                }
            } catch (err) {
                console.error('Failed to fetch analysis:', err);
                setError(err.message || 'Erreur lors du chargement de l\'analyse');
                setLoading(false);
            }
        };

        fetchAnalysisData();
    }, [location]);

    if (loading) {
        return (
            <div className="analysis-report-container" style={{ textAlign: 'center', padding: '100px 20px' }}>
                <h2>Chargement de l'analyse... ⏳</h2>
                <p style={{ color: 'var(--color-text-secondary)' }}>Veuillez patienter</p>
            </div>
        );
    }

    if (error || !analysisData) {
        return (
            <div className="analysis-report-container" style={{ textAlign: 'center', padding: '100px 20px' }}>
                <h2 style={{ color: '#e74c3c' }}>⚠️ Erreur</h2>
                <p>{error || 'Données non disponibles'}</p>
                <button className="back-button" onClick={() => navigate('/')} style={{ position: 'static', marginTop: '20px' }}>
                    Retour à l'accueil
                </button>
            </div>
        );
    }

    const { metrics, repo_name, timestamp } = analysisData;
    const ecoindex = metrics?.ecoindex || {};
    const images = metrics?.images || {};
    const requests = metrics?.requests || {};
    const deadCode = metrics?.dead_code || {};

    // Format date
    const formattedDate = new Date(timestamp).toLocaleDateString('fr-FR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });

    // Calculate savings percentage for images
    const imageSavingsPercent = images.savings_percent || 0;

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
                <p className="url-text">pour {repo_name}</p>
                <p className="date-text">Généré le: {formattedDate}</p>
            </header>

            {/* SECTION SCORE */}
            <div className="score-container">
                <div className="score-item">
                    <p className="score-label">EcoIndex</p>
                    <span className="score-value eco-index">{ecoindex.grade || 'N/A'}</span>
                </div>
                <div className="score-item">
                    <p className="score-label">Score ({ecoindex.rating || 'N/A'})</p>
                    <span className="score-value performance">{ecoindex.score || 0}/100</span>
                </div>
                <div className="score-item">
                    <p className="score-label">Potentiel de Réduction</p>
                    <span className="score-value status">{images.potential_savings_mb || 0} Mo</span>
                </div>
            </div>

            {/* SECTION DÉTAILS */}
            <h2 className="section-title">Détails et Potentiel d'Optimisation</h2>

            {/* BLOC 1: IMAGES */}
            {images.total_images > 0 && (
                <div className="area-container">
                    <div className="area-header">
                        <h3 className="area-title"><i className="fas fa-image"></i> Images (Assets)</h3>
                        <span className={`improvement-pill ${imageSavingsPercent > 50 ? '' : 'pill-warning'}`}>
                            Amélioration: {Math.round(imageSavingsPercent)}%
                        </span>
                    </div>
                    <p className="summary-text">
                        Taille Actuelle Totale: {images.total_size_mb} Mo → Taille Optimale: {(images.total_size_mb - images.potential_savings_mb).toFixed(2)} Mo
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
                            {images.optimizable_list?.slice(0, 10).map((img, idx) => (
                                <tr key={idx}>
                                    <td data-label="Fichier" className="td-filename">{img.path.split('/').pop()}</td>
                                    <td data-label="Taille Actuelle">{img.current_size_kb} Ko</td>
                                    <td data-label="Taille Optimale" className="td-optimal-size">
                                        {(img.current_size_kb - img.estimated_savings_kb).toFixed(2)} Ko
                                    </td>
                                    <td data-label="Suggestion" className="td-suggestion">
                                        Convertir en {img.suggested_format.toUpperCase()} (économie: {img.estimated_savings_kb.toFixed(2)} Ko)
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {/* BLOC 2: REQUÊTES */}
            <div className="area-container">
                <div className="area-header">
                    <h3 className="area-title"><i className="fas fa-network-wired"></i> Requêtes HTTP</h3>
                    <span className="improvement-pill pill-warning">
                        {requests.total_requests} requêtes
                    </span>
                </div>
                <p className="summary-text">
                    Poids total: {requests.total_size_mb} Mo | Moyenne: {requests.avg_file_size_kb} Ko/fichier
                </p>

                <table className="details-table">
                    <thead>
                        <tr>
                            <th>Type</th>
                            <th>Nombre</th>
                            <th>Taille Totale</th>
                            <th>Recommandation</th>
                        </tr>
                    </thead>
                    <tbody>
                        {Object.entries(requests.by_category || {}).map(([type, data]) => (
                            data.count > 0 && (
                                <tr key={type}>
                                    <td data-label="Type" className="td-filename">{type.toUpperCase()}</td>
                                    <td data-label="Nombre">{data.count}</td>
                                    <td data-label="Taille" className="td-optimal-size">{data.size_mb} Mo</td>
                                    <td data-label="Recommandation" className="td-suggestion">
                                        {data.count > 10 ? 'Envisager le bundling' : 'OK'}
                                    </td>
                                </tr>
                            )
                        ))}
                    </tbody>
                </table>
            </div>

            {/* BLOC 3: CODE MORT */}
            {(deadCode.potentially_unused_css > 0 || deadCode.potentially_unused_js > 0) && (
                <div className="area-container">
                    <div className="area-header">
                        <h3 className="area-title"><i className="fas fa-trash"></i> Code Non Utilisé</h3>
                        <span className="improvement-pill pill-danger">
                            {deadCode.total_unused_size_mb} Mo à supprimer
                        </span>
                    </div>
                    <p className="summary-text">
                        {deadCode.potentially_unused_css} fichiers CSS et {deadCode.potentially_unused_js} fichiers JS potentiellement inutilisés
                    </p>

                    <table className="details-table">
                        <thead>
                            <tr>
                                <th>Fichier</th>
                                <th>Type</th>
                                <th>Taille</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {[...(deadCode.unused_css_files || []), ...(deadCode.unused_js_files || [])].slice(0, 10).map((file, idx) => (
                                <tr key={idx}>
                                    <td data-label="Fichier" className="td-filename">{file.path.split('/').pop()}</td>
                                    <td data-label="Type">{file.path.endsWith('.css') ? 'CSS' : 'JS'}</td>
                                    <td data-label="Taille" className="td-optimal-size">{file.size_kb} Ko</td>
                                    <td data-label="Action" className="td-suggestion">Vérifier et supprimer si inutilisé</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {/* FOOTER */}
            <div className="footer">
                <button className="optimize-button" onClick={() => alert('Fonctionnalité d\'optimisation à venir!')}>
                    Lancer l'Optimisation Automatique 🚀
                </button>
            </div>
        </div>
    );
};

export default AnalysisReport;
