from typing import Dict, Any
from pathlib import Path
import logging
from .github_analyzer import GitHubAnalyzer
from .image_optimizer import ImageOptimizer
from .code_optimizer import CodeOptimizer

logger = logging.getLogger(__name__)

# Storage for optimized files
optimized_files: Dict[str, bytes] = {}

class OptimizationEngine:
    """Moteur d'optimisation principal"""
    
    def __init__(self, analyzer: GitHubAnalyzer, analysis: Dict):
        self.analyzer = analyzer
        self.analysis = analysis
        self.optimized_files = []
        self.total_savings = 0
    
    async def optimize_images(self) -> Dict[str, Any]:
        """Optimise toutes les images"""
        logger.info("Starting image optimization...")
        
        optimizable = self.analysis['metrics']['images']['optimizable_list'][:10]  # Top 10
        results = []
        
        for img_info in optimizable:
            try:
                # Télécharger l'image
                img_data = await self.analyzer.get_file_content(img_info['path'])
                if not img_data:
                    continue
                
                # Optimiser
                optimized_data, metadata = await ImageOptimizer.optimize_image(img_data, 'webp', 85)
                
                if 'error' not in metadata:
                    # Sauvegarder temporairement
                    new_path = Path(img_info['path']).with_suffix('.webp')
                    optimized_files[str(new_path)] = optimized_data
                    
                    results.append({
                        'original_path': img_info['path'],
                        'new_path': str(new_path),
                        'original_size_kb': round(metadata['original_size'] / 1024, 2),
                        'optimized_size_kb': round(metadata['optimized_size'] / 1024, 2),
                        'savings_kb': round(metadata['savings'] / 1024, 2),
                        'savings_percent': metadata['savings_percent']
                    })
                    self.total_savings += metadata['savings']
                    
            except Exception as e:
                logger.error(f"Failed to optimize {img_info['path']}: {str(e)}")
        
        return {
            'images_processed': len(results),
            'total_savings_mb': round(self.total_savings / (1024 * 1024), 2),
            'files': results
        }
    
    async def optimize_css(self) -> Dict[str, Any]:
        """Optimise les fichiers CSS"""
        logger.info("Starting CSS optimization...")
        
        css_files = [f for f in self.analysis['metrics']['requests']['by_category']['css']['largest_files']]
        results = []
        savings = 0
        
        for css_info in css_files[:5]:  # Top 5
            try:
                content = await self.analyzer.get_file_content(css_info['path'])
                if not content:
                    continue
                
                css_text = content.decode('utf-8', errors='ignore')
                minified, metadata = CodeOptimizer.minify_css(css_text)
                
                if 'error' not in metadata:
                    results.append({
                        'path': css_info['path'],
                        'original_size_kb': round(metadata['original_size'] / 1024, 2),
                        'optimized_size_kb': round(metadata['optimized_size'] / 1024, 2),
                        'savings_kb': round(metadata['savings'] / 1024, 2),
                        'savings_percent': metadata['savings_percent']
                    })
                    savings += metadata['savings']
                    
            except Exception as e:
                logger.error(f"Failed to optimize {css_info['path']}: {str(e)}")
        
        return {
            'files_processed': len(results),
            'total_savings_kb': round(savings / 1024, 2),
            'files': results
        }
    
    async def optimize_js(self) -> Dict[str, Any]:
        """Optimise les fichiers JavaScript"""
        logger.info("Starting JS optimization...")
        
        js_files = [f for f in self.analysis['metrics']['requests']['by_category']['js']['largest_files']]
        results = []
        savings = 0
        
        for js_info in js_files[:5]:  # Top 5
            try:
                content = await self.analyzer.get_file_content(js_info['path'])
                if not content:
                    continue
                
                js_text = content.decode('utf-8', errors='ignore')
                minified, metadata = CodeOptimizer.minify_js(js_text)
                
                if 'error' not in metadata:
                    results.append({
                        'path': js_info['path'],
                        'original_size_kb': round(metadata['original_size'] / 1024, 2),
                        'optimized_size_kb': round(metadata['optimized_size'] / 1024, 2),
                        'savings_kb': round(metadata['savings'] / 1024, 2),
                        'savings_percent': metadata['savings_percent']
                    })
                    savings += metadata['savings']
                    
            except Exception as e:
                logger.error(f"Failed to optimize {js_info['path']}: {str(e)}")
        
        return {
            'files_processed': len(results),
            'total_savings_kb': round(savings / 1024, 2),
            'files': results
        }
    
    async def optimize_html(self) -> Dict[str, Any]:
        """Optimise les fichiers HTML"""
        logger.info("Starting HTML optimization...")
        
        html_files = [f for f in self.analysis['metrics']['requests']['by_category']['html']['largest_files']]
        results = []
        savings = 0
        
        for html_info in html_files[:5]:  # Top 5
            try:
                content = await self.analyzer.get_file_content(html_info['path'])
                if not content:
                    continue
                
                html_text = content.decode('utf-8', errors='ignore')
                minified, metadata = CodeOptimizer.minify_html(html_text)
                
                if 'error' not in metadata:
                    results.append({
                        'path': html_info['path'],
                        'original_size_kb': round(metadata['original_size'] / 1024, 2),
                        'optimized_size_kb': round(metadata['optimized_size'] / 1024, 2),
                        'savings_kb': round(metadata['savings'] / 1024, 2),
                        'savings_percent': metadata['savings_percent']
                    })
                    savings += metadata['savings']
                    
            except Exception as e:
                logger.error(f"Failed to optimize {html_info['path']}: {str(e)}")
        
        return {
            'files_processed': len(results),
            'total_savings_kb': round(savings / 1024, 2),
            'files': results
        }
