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
            console.error('Optimization error:', err);
            if (err.message.includes('not found') || err.message.includes('404')) {
                setError('Session expirée (serveur redémarré). Veuillez relancer l\'analyse depuis l\'accueil.');
            } else {
                setError('Erreur lors du lancement de l\'optimisation: ' + err.message);
            }
            setOptimizing(false);
        }
    };

    const handleDownload = () => {
        if (optimizationJob?.job_id) {
            window.location.href = api.getDownloadUrl(optimizationJob.job_id);
        }
    };

    const handleViewReport = () => {
        if (optimizationJob?.job_id) {
            window.open(`http://localhost:8000/api/report/${optimizationJob.job_id}`, '_blank');
        }
    };

    const handleDownloadReport = () => {
        if (optimizationJob?.job_id) {
            window.location.href = `http://localhost:8000/api/report/${optimizationJob.job_id}/download`;
        }
    };

    const handleDownloadAnalysisReport = () => {
        // Extract actual data from analysisData
        const { metrics, repo_url, branch, timestamp } = analysisData;
        const unusedFiles = metrics.unused_files_advanced || metrics.unused_files || {};
        const comments = metrics.comments_analysis || {};
        const whitespace = metrics.whitespace_analysis || {};
        
        const totalPotentialSavings = (
            (unusedFiles.total_unused_size_mb || 0) + 
            (whitespace.total_savings_kb || 0) / 1024
        ).toFixed(2);

        const reportHtml = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analysis Report - ${repo_url}</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px; margin-bottom: 30px; }
        .header h1 { margin: 0 0 10px 0; }
        .header p { margin: 5px 0; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stat-card h3 { margin: 0 0 10px 0; color: #666; font-size: 14px; }
        .stat-card .value { font-size: 32px; font-weight: bold; color: #667eea; }
        .section { background: white; padding: 20px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .section h2 { color: #333; border-bottom: 2px solid #667eea; padding-bottom: 10px; margin-top: 0; }
        .detail-row { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #eee; }
        .detail-row:last-child { border-bottom: none; }
        .detail-label { font-weight: 600; color: #555; }
        .detail-value { color: #667eea; font-weight: 700; }
        footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 14px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Green Optimizer - Analysis Report</h1>
        <p><strong>Repository:</strong> ${repo_url}</p>
        <p><strong>Branch:</strong> ${branch}</p>
        <p><strong>Analyzed:</strong> ${new Date(timestamp).toLocaleString()}</p>
    </div>

    <div class="stats">
        <div class="stat-card">
            <h3>Unused Files</h3>
            <div class="value">${unusedFiles.total_unused_files || 0}</div>
        </div>
        <div class="stat-card">
            <h3>Potential Savings</h3>
            <div class="value">${totalPotentialSavings} MB</div>
        </div>
        <div class="stat-card">
            <h3>Files with Comments</h3>
            <div class="value">${comments.files_with_excessive_comments || 0}</div>
        </div>
        <div class="stat-card">
            <h3>Whitespace Savings</h3>
            <div class="value">${(whitespace.potential_savings_kb || 0).toFixed(2)} KB</div>
        </div>
    </div>

    <div class="section">
        <h2>🗑️ Unused Files Detected</h2>
        <div class="detail-row">
            <span class="detail-label">Total Unused Files:</span>
            <span class="detail-value">${unusedFiles.total_unused_files || 0} files</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">Total Size:</span>
            <span class="detail-value">${(unusedFiles.total_unused_size_mb || 0).toFixed(2)} MB</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">Unused CSS Files:</span>
            <span class="detail-value">${unusedFiles.unused_css?.files?.length || 0} files</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">Unused JS Files:</span>
            <span class="detail-value">${unusedFiles.unused_js?.files?.length || 0} files</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">Unused Images:</span>
            <span class="detail-value">${unusedFiles.unused_images?.files?.length || 0} files</span>
        </div>
    </div>

    <div class="section">
        <h2>✂️ Comments Analysis</h2>
        <div class="detail-row">
            <span class="detail-label">Files Analyzed:</span>
            <span class="detail-value">${comments.files_analyzed || 0}</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">Files with Excessive Comments:</span>
            <span class="detail-value">${comments.files_with_excessive_comments || 0}</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">Average Comment Percentage:</span>
            <span class="detail-value">${(comments.avg_comment_percent || 0).toFixed(2)}%</span>
        </div>
    </div>

    <div class="section">
        <h2>🧹 Whitespace Analysis</h2>
        <div class="detail-row">
            <span class="detail-label">Files Analyzed:</span>
            <span class="detail-value">${whitespace.files_analyzed || 0}</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">Potential Savings:</span>
            <span class="detail-value">${(whitespace.potential_savings_kb || 0).toFixed(2)} KB</span>
        </div>
    </div>

    <footer>
        <p><strong>Green Optimizer v4.0</strong> - Analysis Report</p>
        <p>This report shows potential optimizations. Click "Optimiser le Projet" to apply these improvements automatically.</p>
        <p>Generated on: ${new Date().toLocaleString()}</p>
    </footer>
</body>
</html>`;

        // Create blob and download
        const blob = new Blob([reportHtml], { type: 'text/html' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `analysis_report_${new Date().getTime()}.html`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
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
                    <span className="green-text">Rapport d'Analyse</span>
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
                    <div style={{display: 'flex', gap: '10px', flexWrap: 'wrap'}}>
                        <button className="optimize-button-large" onClick={handleOptimize} disabled={optimizing}>
                            {optimizing ? 'Démarrage...' : '🚀 Optimiser le Projet Maintenant'}
                        </button>
                        <button className="optimize-button-large" onClick={handleDownloadAnalysisReport} 
                                style={{background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'}}>
                            📄 Télécharger le Rapport d'Analyse
                        </button>
                    </div>
                )}

                {/* PROGRESS & RESULT */}
                {optimizationJob && (
                    <div className="optimization-status">
                        <div className="progress-bar">
                            <div className="progress-fill" style={{width: `${optimizationJob.progress}%`}}></div>
                        </div>
                        <p className="status-text">
                            Statut: {optimizationJob.status === 'completed' ? '✅ Terminé !' : 
                                     optimizationJob.status === 'failed' ? '❌ Erreur' :
                                     optimizationJob.message || 'En cours...'}
                        </p>
                        
                        {optimizationJob.status === 'completed' && (
                            <div className="success-box">
                                <h3>✅ Optimisation Réussie !</h3>
                                <p>Taille économisée : {(optimizationJob.stats?.bytes_saved / 1024 / 1024).toFixed(2)} Mo</p>
                                <p>Fichiers supprimés : {optimizationJob.stats?.files_deleted}</p>
                                <div style={{display: 'flex', gap: '10px', marginTop: '15px', flexWrap: 'wrap'}}>
                                    <button className="download-button" onClick={handleViewReport}>
                                        <i className="fas fa-eye"></i> Voir le Rapport
                                    </button>
                                    <button className="download-button" onClick={handleDownloadReport}>
                                        <i className="fas fa-file-download"></i> Télécharger le Rapport (.html)
                                    </button>
                                    <button className="download-button" onClick={handleDownload}>
                                        <i className="fas fa-download"></i> Télécharger le Projet (.zip)
                                    </button>
                                </div>
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
