"""
Green Optimizer Backend - FastAPI
Analyse et optimisation automatique de projets GitHub
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import hashlib
import logging
from typing import Dict, List, Any

from .models import GitHubRepoRequest, AnalysisResult, OptimizationRequest
from .services import (
    GitHubAnalyzer,
    ImageOptimizer,
    CodeOptimizer,
    PageAnalyzer,
    OptimizationEngine,
    generate_ecoindex_recommendations
)

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Green Optimizer API",
    version="2.0.0",
    description="Analyse et optimisation écologique de projets web"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== STORAGE ====================

analyses_storage: Dict[str, Dict] = {}
optimization_jobs: Dict[str, Dict] = {}
optimized_files: Dict[str, bytes] = {}

# ==================== API ENDPOINTS ====================

@app.get("/")
async def root():
    return {
        "name": "Green Optimizer API",
        "version": "2.0.0",
        "description": "Analyse et optimisation écologique de projets web",
        "endpoints": {
            "health": "GET /api/health",
            "analyze": "POST /api/analyze",
            "get_analysis": "GET /api/analysis/{analysis_id}",
            "optimize": "POST /api/optimize",
            "get_optimization": "GET /api/optimization/{optimization_id}",
            "download_optimized": "GET /api/optimization/{optimization_id}/download"
        },
        "documentation": "/docs"
    }

@app.get("/api/health")
async def health_check():
    """Vérification de l'état de l'API"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "analyses_count": len(analyses_storage),
        "optimizations_count": len(optimization_jobs)
    }

@app.post("/api/analyze", response_model=AnalysisResult)
async def analyze_repository(request: GitHubRepoRequest):
    """
    Analyse complète d'un repository GitHub
    
    - Analyse des images (taille, format, optimisations possibles)
    - Analyse des requêtes HTTP (nombre, taille)
    - Détection du code mort (CSS/JS non utilisé)
    - Calcul du score EcoIndex
    """
    
    logger.info(f"Starting analysis for {request.repo_url}")
    
    # Générer ID unique
    analysis_id = hashlib.md5(
        f"{request.repo_url}{request.branch}{datetime.utcnow().timestamp()}".encode()
    ).hexdigest()
    
    try:
        # Initialiser l'analyseur
        analyzer = GitHubAnalyzer(
            str(request.repo_url),
            request.branch,
            request.github_token
        )
        
        # Récupérer infos du repo
        repo_info = await analyzer.get_repo_info()
        
        # Récupérer l'arborescence
        files = await analyzer.get_repo_tree()
        
        if not files:
            raise HTTPException(status_code=400, detail="No files found in repository")
        
        # Lancer les analyses
        logger.info("Running image analysis...")
        image_analysis = ImageOptimizer.analyze_images(files)
        
        logger.info("Running request analysis...")
        request_analysis = PageAnalyzer.analyze_requests(files)
        
        logger.info("Detecting dead code...")
        dead_code_analysis = await CodeOptimizer.detect_dead_code(analyzer, files)
        
        # Compiler les métriques
        metrics = {
            'images': image_analysis,
            'requests': request_analysis,
            'dead_code': dead_code_analysis
        }
        
        # Calculer le score EcoIndex
        logger.info("Calculating EcoIndex score...")
        ecoindex = PageAnalyzer.calculate_ecoindex(metrics)
        metrics['ecoindex'] = ecoindex
        
        # Générer le plan d'optimisation
        logger.info("Generating optimization plan...")
        optimization_plan = generate_optimization_plan(metrics)
        
        # Sauvegarder les résultats
        result = {
            'repo_url': str(request.repo_url),
            'repo_name': f"{analyzer.owner}/{analyzer.repo}",
            'branch': request.branch,
            'analysis_id': analysis_id,
            'timestamp': datetime.utcnow().isoformat(),
            'repo_info': {
                'stars': repo_info.get('stargazers_count', 0),
                'forks': repo_info.get('forks_count', 0),
                'language': repo_info.get('language', 'Unknown'),
                'size_kb': repo_info.get('size', 0)
            },
            'metrics': metrics,
            'optimization_plan': optimization_plan,
            'status': 'completed'
        }
        
        analyses_storage[analysis_id] = result
        logger.info(f"Analysis completed: {analysis_id}")
        
        return AnalysisResult(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    """Récupère les résultats d'une analyse"""
    
    if analysis_id not in analyses_storage:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return analyses_storage[analysis_id]

@app.get("/api/analyses")
async def list_analyses(limit: int = 10):
    """Liste les analyses récentes"""
    
    analyses = list(analyses_storage.values())
    analyses.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return {
        'total': len(analyses),
        'analyses': analyses[:limit]
    }

@app.post("/api/optimize")
async def optimize_repository(request: OptimizationRequest, background_tasks: BackgroundTasks):
    """
    Applique les optimisations sélectionnées
    
    - images: Conversion WebP/AVIF
    - css: Minification CSS
    - js: Minification JavaScript
    - html: Minification HTML
    """
    
    if request.analysis_id not in analyses_storage:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    analysis = analyses_storage[request.analysis_id]
    
    logger.info(f"Starting optimization for analysis {request.analysis_id}")
    
    # Générer ID d'optimisation
    optimization_id = hashlib.md5(
        f"{request.analysis_id}{datetime.utcnow().timestamp()}".encode()
    ).hexdigest()
    
    try:
        # Initialiser l'analyseur
        analyzer = GitHubAnalyzer(
            analysis['repo_url'],
            analysis['branch'],
            None
        )
        
        # Créer le moteur d'optimisation
        engine = OptimizationEngine(analyzer, analysis)
        
        # Appliquer les optimisations
        results = {
            'optimization_id': optimization_id,
            'analysis_id': request.analysis_id,
            'timestamp': datetime.utcnow().isoformat(),
            'requested_optimizations': request.optimizations,
            'status': 'processing',
            'changes': []
        }
        
        total_savings_bytes = 0
        
        if 'images' in request.optimizations:
            logger.info("Optimizing images...")
            img_result = await engine.optimize_images()
            results['changes'].append({
                'type': 'images',
                'result': img_result
            })
            total_savings_bytes += img_result.get('total_savings_mb', 0) * 1024 * 1024
        
        if 'css' in request.optimizations:
            logger.info("Optimizing CSS...")
            css_result = await engine.optimize_css()
            results['changes'].append({
                'type': 'css',
                'result': css_result
            })
            total_savings_bytes += css_result.get('total_savings_kb', 0) * 1024
        
        if 'js' in request.optimizations:
            logger.info("Optimizing JavaScript...")
            js_result = await engine.optimize_js()
            results['changes'].append({
                'type': 'js',
                'result': js_result
            })
            total_savings_bytes += js_result.get('total_savings_kb', 0) * 1024
        
        if 'html' in request.optimizations:
            logger.info("Optimizing HTML...")
            html_result = await engine.optimize_html()
            results['changes'].append({
                'type': 'html',
                'result': html_result
            })
            total_savings_bytes += html_result.get('total_savings_kb', 0) * 1024
        
        # Calculer les économies totales
        results['summary'] = {
            'total_savings_mb': round(total_savings_bytes / (1024 * 1024), 2),
            'total_savings_percent': round(
                (total_savings_bytes / (analysis['metrics']['requests']['total_size_bytes'] or 1)) * 100,
                2
            ),
            'files_optimized': sum(c['result'].get('files_processed', 0) for c in results['changes'])
        }
        
        results['status'] = 'completed'
        optimization_jobs[optimization_id] = results
        
        logger.info(f"Optimization completed: {optimization_id}")
        
        return results
        
    except Exception as e:
        logger.error(f"Optimization failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")

@app.get("/api/optimization/{optimization_id}")
async def get_optimization(optimization_id: str):
    """Récupère les résultats d'une optimisation"""
    
    if optimization_id not in optimization_jobs:
        raise HTTPException(status_code=404, detail="Optimization not found")
    
    return optimization_jobs[optimization_id]

@app.delete("/api/analysis/{analysis_id}")
async def delete_analysis(analysis_id: str):
    """Supprime une analyse"""
    
    if analysis_id not in analyses_storage:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    del analyses_storage[analysis_id]
    
    return {"message": "Analysis deleted successfully"}

# ==================== HELPER FUNCTIONS ====================

def generate_optimization_plan(metrics: Dict) -> Dict[str, Any]:
    """Génère un plan d'optimisation détaillé"""
    
    plan = {
        'priority_actions': [],
        'estimated_total_savings_mb': 0,
        'estimated_performance_improvement_percent': 0,
        'implementation_difficulty': 'medium',
        'estimated_time_hours': 0
    }
    
    total_savings = 0
    
    # 1. Optimisation des images
    if metrics['images']['potential_savings_mb'] > 0.5:
        savings = metrics['images']['potential_savings_mb']
        total_savings += savings
        
        plan['priority_actions'].append({
            'priority': 1,
            'action': 'Convertir les images en WebP/AVIF',
            'impact': 'high' if savings > 2 else 'medium',
            'savings_mb': savings,
            'files_affected': metrics['images']['optimizable_images'],
            'effort': 'low',
            'estimated_time_hours': 1,
            'tools': ['Pillow', 'ImageMagick', 'Squoosh'],
            'description': f"Convertir {metrics['images']['optimizable_images']} images pour économiser {savings:.2f} MB"
        })
    
    # 2. Suppression du code mort
    if metrics['dead_code']['total_unused_size_mb'] > 0.1:
        savings = metrics['dead_code']['total_unused_size_mb']
        total_savings += savings
        
        plan['priority_actions'].append({
            'priority': 2,
            'action': 'Supprimer les fichiers CSS/JS non utilisés',
            'impact': 'medium',
            'savings_mb': savings,
            'files_affected': metrics['dead_code']['potentially_unused_css'] + metrics['dead_code']['potentially_unused_js'],
            'effort': 'medium',
            'estimated_time_hours': 2,
            'tools': ['PurgeCSS', 'UnCSS', 'Tree shaking'],
            'description': f"Supprimer {metrics['dead_code']['potentially_unused_css']} CSS et {metrics['dead_code']['potentially_unused_js']} JS inutilisés"
        })
    
    # 3. Minification
    total_code_size = (
        metrics['requests']['by_category']['css']['size_mb'] +
        metrics['requests']['by_category']['js']['size_mb'] +
        metrics['requests']['by_category']['html']['size_mb']
    )
    
    if total_code_size > 0.5:
        estimated_savings = total_code_size * 0.3  # ~30% de réduction
        total_savings += estimated_savings
        
        plan['priority_actions'].append({
            'priority': 3,
            'action': 'Minifier HTML, CSS et JavaScript',
            'impact': 'medium',
            'savings_mb': estimated_savings,
            'files_affected': (
                metrics['requests']['by_category']['css']['count'] +
                metrics['requests']['by_category']['js']['count'] +
                metrics['requests']['by_category']['html']['count']
            ),
            'effort': 'low',
            'estimated_time_hours': 1,
            'tools': ['Terser', 'UglifyJS', 'clean-css', 'html-minifier'],
            'description': 'Minifier tous les fichiers texte pour réduire leur taille'
        })
    
    # 4. Compression Gzip/Brotli
    if metrics['requests']['total_size_mb'] > 1:
        plan['priority_actions'].append({
            'priority': 4,
            'action': 'Activer la compression Gzip/Brotli',
            'impact': 'high',
            'savings_mb': metrics['requests']['total_size_mb'] * 0.7,  # ~70% de compression
            'files_affected': 'all',
            'effort': 'low',
            'estimated_time_hours': 0.5,
            'tools': ['Nginx', 'Apache', 'CDN'],
            'description': 'Configuration serveur pour compression automatique'
        })
    
    # 5. Lazy loading
    if metrics['images']['total_images'] > 10:
        plan['priority_actions'].append({
            'priority': 5,
            'action': 'Implémenter le lazy loading des images',
            'impact': 'high',
            'savings_mb': 'N/A',
            'files_affected': metrics['images']['total_images'],
            'effort': 'medium',
            'estimated_time_hours': 2,
            'tools': ['loading="lazy"', 'Intersection Observer'],
            'description': 'Charger les images uniquement quand nécessaire'
        })
    
    # Calculer les totaux
    plan['estimated_total_savings_mb'] = round(total_savings, 2)
    
    if metrics['requests']['total_size_mb'] > 0:
        plan['estimated_performance_improvement_percent'] = round(
            (total_savings / metrics['requests']['total_size_mb']) * 100,
            1
        )
    
    plan['estimated_time_hours'] = sum(
        action.get('estimated_time_hours', 0)
        for action in plan['priority_actions']
    )
    
    # Recommandations générales
    plan['general_recommendations'] = [
        '✅ Utiliser un CDN pour les ressources statiques',
        '✅ Mettre en cache les ressources (Cache-Control headers)',
        '✅ Utiliser HTTP/2 ou HTTP/3',
        '✅ Précharger les ressources critiques (preload, prefetch)',
        '✅ Différer le chargement des scripts non critiques',
        '✅ Optimiser les fonts (woff2, font-display: swap)'
    ]
    
    return plan

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
