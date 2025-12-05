from .github_analyzer import GitHubAnalyzer
from .image_optimizer import ImageOptimizer
from .code_optimizer import CodeOptimizer
from .page_analyzer import PageAnalyzer, generate_ecoindex_recommendations
from .optimization_engine import OptimizationEngine

__all__ = [
    'GitHubAnalyzer',
    'ImageOptimizer',
    'CodeOptimizer',
    'PageAnalyzer',
    'OptimizationEngine',
    'generate_ecoindex_recommendations'
]
