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
    
    // Optimization State
    const [optimizing, setOptimizing] = useState(false);
    const [optimizationJob, setOptimizationJob] = useState(null);
    const [optimizationOptions, setOptimizationOptions] = useState({
        remove_comments: true,
        remove_whitespace: true,
        remove_unused_files: true,
        optimize_images: true,
        minify_code: true
    });

    useEffect(() => {
        const fetchAnalysisData = async () => {
            try {
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

    // Polling function for optimization status
    useEffect(() => {
        let interval;
        if (optimizing && optimizationJob?.job_id) {
            interval = setInterval(async () => {
                try {
                    const status = await api.getOptimizationStatus(optimizationJob.job_id);
                    setOptimizationJob(status);
                    
                    if (status.status === 'completed' || status.status === 'failed') {
                        setOptimizing(false);
                        clearInterval(interval);
                    }
                } catch (err) {
                    console.error('Polling error:', err);
                }
            }, 1000);
        }
        return () => clearInterval(interval);
    }, [optimizing, optimizationJob?.job_id]);

    const handleOptimize = async () => {
        if (!analysisData?.analysis_id) return;
        
        try {
            setOptimizing(true);
            const response = await api.optimizeRepository(
                analysisData.analysis_id, 
                optimizationOptions
            );
            setOptimizationJob({ job_id: response.job_id, progress: 0, status: 'processing' });
        } catch (err) {
            setError('Erreur lors du lancement de l\'optimisation');
            setOptimizing(false);
        }
    };

    const handleDownload = () => {
        if (optimizationJob?.job_id) {
            window.location.href = api.getDownloadUrl(optimizationJob.job_id);
        }
    };

    if (loading) return <div className="loading">Chargement...</div>;
    if (error) return <div className="error">{error}</div>;
    if (!analysisData) return null;

    const { metrics, repo_url, branch, timestamp } = analysisData;
    const unusedFiles = metrics.unused_files_advanced || {};
    const comments = metrics.comments_analysis || {};
    const whitespace = metrics.whitespace_analysis || {};

    // Calculs pour l'affichage
    const totalPotentialSavings = (
        (unusedFiles.total_unused_size_mb || 0) + 
        (whitespace.total_savings_kb || 0) / 1024
    ).toFixed(2);

    return (
        <div className="analysis-report-container">
            <header className="report-header">
                <button className="back-button" onClick={() => navigate('/')}>
                    <i className="fas fa-arrow-left"></i> Retour
                </button>
                <h1 className="report-title">
                    <span className="green-text">Rapport d'Analyse</span> V3.0
                </h1>
                <p className="url-text">{repo_url} ({branch})</p>
            </header>

            {/* SCORE RESUME */}
            <div className="score-container">
                <div className="score-item">
                    <p className="score-label">Fichiers Analysés</p>
                    <span className="score-value">{metrics.total_files}</span>
                </div>
                <div className="score-item">
                    <p className="score-label">Potentiel d'économie</p>
                    <span className="score-value status">~{totalPotentialSavings} Mo</span>
                </div>
                <div className="score-item">
                    <p className="score-label">Fichiers Inutiles</p>
                    <span className="score-value error">
                        {unusedFiles.unused_css?.count + unusedFiles.unused_js?.count + unusedFiles.unused_images?.count || 0}
                    </span>
                </div>
            </div>

            <h2 className="section-title">Détails de l'Optimisation</h2>

            {/* UNUSED FILES */}
            <div className="area-container">
                <h3 className="area-title"><i className="fas fa-trash"></i> Ressources Non Utilisées</h3>
                <p>Ces fichiers sont présents dans le projet mais jamais importés ou référencés.</p>
                
                <div className="details-grid">
                    {/* CSS */}
                    <div className="detail-card">
                        <h4>CSS Inutilisés ({unusedFiles.unused_css?.count || 0})</h4>
                        <ul>
                            {unusedFiles.unused_css?.files?.slice(0, 5).map((f, i) => (
                                <li key={i}>{f.path.split('/').pop()} <span className="size-tag">{f.size_kb} Ko</span></li>
                            ))}
                        </ul>
                    </div>
                    {/* JS */}
                    <div className="detail-card">
                        <h4>JS Inutilisés ({unusedFiles.unused_js?.count || 0})</h4>
                        <ul>
                            {unusedFiles.unused_js?.files?.slice(0, 5).map((f, i) => (
                                <li key={i}>{f.path.split('/').pop()} <span className="size-tag">{f.size_kb} Ko</span></li>
                            ))}
                        </ul>
                    </div>
                    {/* IMAGES */}
                    <div className="detail-card">
                        <h4>Images Inutilisées ({unusedFiles.unused_images?.count || 0})</h4>
                        <ul>
                            {unusedFiles.unused_images?.files?.slice(0, 5).map((f, i) => (
                                <li key={i}>{f.path.split('/').pop()} <span className="size-tag">{f.size_kb} Ko</span></li>
                            ))}
                        </ul>
                    </div>
                </div>
            </div>

            {/* CODE QUALITY */}
            <div className="area-container">
                <h3 className="area-title"><i className="fas fa-code"></i> Qualité du Code</h3>
                <div className="stats-row">
                    <div className="stat-box">
                        <strong>Espaces Inutiles</strong>
                        <p>{whitespace.total_savings_kb || 0} Ko économisables</p>
                        <small>Sur {whitespace.files_with_issues || 0} fichiers</small>
                    </div>
                    <div className="stat-box">
                        <strong>Commentaires</strong>
                        <p>{comments.total_comment_lines || 0} lignes</p>
                        <small>{comments.avg_comment_percent}% du code</small>
                    </div>
                </div>
            </div>

            {/* OPTIMIZATION ACTIONS */}
            <div className="optimization-zone">
                <h2 className="section-title">🚀 Lancer l'Optimisation Automatique</h2>
                
                <div className="options-grid">
                    <label>
                        <input type="checkbox" checked={optimizationOptions.remove_unused_files}
                            onChange={e => setOptimizationOptions({...optimizationOptions, remove_unused_files: e.target.checked})} />
                        Supprimer les fichiers inutiles
                    </label>
                    <label>
                        <input type="checkbox" checked={optimizationOptions.remove_comments}
                            onChange={e => setOptimizationOptions({...optimizationOptions, remove_comments: e.target.checked})} />
                        Supprimer les commentaires
                    </label>
                    <label>
                        <input type="checkbox" checked={optimizationOptions.remove_whitespace}
                            onChange={e => setOptimizationOptions({...optimizationOptions, remove_whitespace: e.target.checked})} />
                        Nettoyer les espaces
                    </label>
                    <label>
                        <input type="checkbox" checked={optimizationOptions.optimize_images}
                            onChange={e => setOptimizationOptions({...optimizationOptions, optimize_images: e.target.checked})} />
                        Compresser les images (WebP)
                    </label>
                    <label>
                        <input type="checkbox" checked={optimizationOptions.minify_code}
                            onChange={e => setOptimizationOptions({...optimizationOptions, minify_code: e.target.checked})} />
                        Minifier le code (CSS/JS)
                    </label>
                </div>

                {!optimizationJob && (
                    <button className="optimize-button-large" onClick={handleOptimize} disabled={optimizing}>
                        {optimizing ? 'Démarrage...' : 'Optimiser le Projet Maintenant'}
                    </button>
                )}

                {/* PROGRESS & RESULT */}
                {optimizationJob && (
                    <div className="optimization-status">
                        <div className="progress-bar">
                            <div className="progress-fill" style={{width: `${optimizationJob.progress}%`}}></div>
                        </div>
                        <p className="status-text">
                            Statut: {optimizationJob.status === 'processing' ? 'En cours...' : 
                                     optimizationJob.status === 'completed' ? 'Terminé !' : 'Erreur'}
                        </p>
                        
                        {optimizationJob.status === 'completed' && (
                            <div className="success-box">
                                <h3>✅ Optimisation Réussie !</h3>
                                <p>Taille économisée : {(optimizationJob.stats?.bytes_saved / 1024 / 1024).toFixed(2)} Mo</p>
                                <p>Fichiers supprimés : {optimizationJob.stats?.files_deleted}</p>
                                <button className="download-button" onClick={handleDownload}>
                                    <i className="fas fa-download"></i> Télécharger le projet optimisé (.zip)
                                </button>
                            </div>
                        )}
                        
                        {optimizationJob.status === 'failed' && (
                            <div className="error-box">
                                <p>Erreur: {optimizationJob.error}</p>
                                <button onClick={() => setOptimizationJob(null)}>Réessayer</button>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default AnalysisReport;
