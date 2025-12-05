import cssutils
import jsbeautifier
from bs4 import BeautifulSoup
import re
import logging
from typing import Tuple, Dict, List, Any
from pathlib import Path
from .github_analyzer import GitHubAnalyzer

logger = logging.getLogger(__name__)

# Suppression des warnings cssutils
cssutils.log.setLevel(logging.CRITICAL)

class CodeOptimizer:
    """Optimiseur de code CSS/JS/HTML"""
    
    @staticmethod
    def minify_css(css_content: str) -> Tuple[str, Dict]:
        """Minifie du CSS"""
        try:
            original_size = len(css_content.encode('utf-8'))
            
            # Parse et minify avec cssutils
            sheet = cssutils.parseString(css_content)
            minified = sheet.cssText.decode('utf-8') if isinstance(sheet.cssText, bytes) else sheet.cssText
            
            # Compression supplémentaire
            minified = re.sub(r'\s+', ' ', minified)
            minified = re.sub(r'\s*([{}:;,])\s*', r'\1', minified)
            minified = minified.strip()
            
            optimized_size = len(minified.encode('utf-8'))
            
            return minified, {
                'original_size': original_size,
                'optimized_size': optimized_size,
                'savings': original_size - optimized_size,
                'savings_percent': round((original_size - optimized_size) / original_size * 100, 2) if original_size > 0 else 0
            }
        except Exception as e:
            logger.error(f"CSS minification failed: {str(e)}")
            return css_content, {'error': str(e)}
    
    @staticmethod
    def minify_js(js_content: str) -> Tuple[str, Dict]:
        """Minifie du JavaScript"""
        try:
            original_size = len(js_content.encode('utf-8'))
            
            # Utiliser jsbeautifier en mode minify
            opts = jsbeautifier.default_options()
            opts.indent_size = 0
            
            # Simple minification
            minified = js_content
            # Supprimer les commentaires
            minified = re.sub(r'//.*?\n', '\n', minified)
            minified = re.sub(r'/\.?\*/', '', minified, flags=re.DOTALL)
            # Supprimer les espaces multiples
            minified = re.sub(r'\s+', ' ', minified)
            minified = minified.strip()
            
            optimized_size = len(minified.encode('utf-8'))
            
            return minified, {
                'original_size': original_size,
                'optimized_size': optimized_size,
                'savings': original_size - optimized_size,
                'savings_percent': round((original_size - optimized_size) / original_size * 100, 2) if original_size > 0 else 0
            }
        except Exception as e:
            logger.error(f"JS minification failed: {str(e)}")
            return js_content, {'error': str(e)}
    
    @staticmethod
    def minify_html(html_content: str) -> Tuple[str, Dict]:
        """Minifie du HTML"""
        try:
            original_size = len(html_content.encode('utf-8'))
            
            # Parse avec BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Supprimer les commentaires
            for comment in soup.find_all(string=lambda text: isinstance(text, str) and text.strip().startswith('<!--')):
                comment.extract()
            
            # Minifier
            minified = str(soup)
            minified = re.sub(r'\s+', ' ', minified)
            minified = re.sub(r'>\s+<', '><', minified)
            minified = minified.strip()
            
            optimized_size = len(minified.encode('utf-8'))
            
            return minified, {
                'original_size': original_size,
                'optimized_size': optimized_size,
                'savings': original_size - optimized_size,
                'savings_percent': round((original_size - optimized_size) / original_size * 100, 2) if original_size > 0 else 0
            }
        except Exception as e:
            logger.error(f"HTML minification failed: {str(e)}")
            return html_content, {'error': str(e)}
    
    @staticmethod
    async def detect_dead_code(analyzer: GitHubAnalyzer, files: List[Dict]) -> Dict[str, Any]:
        """Détecte le CSS/JS potentiellement non utilisé"""
        
        css_files = [f for f in files if f['path'].endswith('.css') and f['type'] == 'blob']
        js_files = [f for f in files if f['path'].endswith('.js') and f['type'] == 'blob']
        html_files = [f for f in files if f['path'].endswith(('.html', '.htm')) and f['type'] == 'blob']
        
        # Récupérer les références dans les fichiers HTML
        html_references = set()
        html_inline_css = 0
        html_inline_js = 0
        
        for html_file in html_files[:10]:  # Limite à 10 fichiers HTML
            try:
                content = await analyzer.get_file_content(html_file['path'])
                text = content.decode('utf-8', errors='ignore')
                
                # Trouver les références CSS
                css_refs = re.findall(r'href=["\']([^"\']+\.css)["\']', text, re.IGNORECASE)
                html_references.update(css_refs)
                
                # Trouver les références JS
                js_refs = re.findall(r'src=["\']([^"\']+\.js)["\']', text, re.IGNORECASE)
                html_references.update(js_refs)
                
                # CSS/JS inline
                html_inline_css += len(re.findall(r'<style[^>]>.?</style>', text, re.DOTALL | re.IGNORECASE))
                html_inline_js += len(re.findall(r'<script[^>]>(?!.*src=).?</script>', text, re.DOTALL | re.IGNORECASE))
                
            except Exception as e:
                logger.error(f"Error analyzing {html_file['path']}: {str(e)}")
                continue
        
        # Identifier les fichiers non référencés
        unused_css = []
        unused_js = []
        
        for css_file in css_files:
            filename = Path(css_file['path']).name
            referenced = any(filename in ref or css_file['path'] in ref for ref in html_references)
            
            if not referenced:
                unused_css.append({
                    'path': css_file['path'],
                    'size': css_file.get('size', 0),
                    'size_kb': round(css_file.get('size', 0) / 1024, 2)
                })
        
        for js_file in js_files:
            filename = Path(js_file['path']).name
            # Exclure les fichiers communs (libraries, frameworks)
            if any(lib in filename.lower() for lib in ['jquery', 'bootstrap', 'react', 'vue', 'angular']):
                continue
                
            referenced = any(filename in ref or js_file['path'] in ref for ref in html_references)
            
            if not referenced:
                unused_js.append({
                    'path': js_file['path'],
                    'size': js_file.get('size', 0),
                    'size_kb': round(js_file.get('size', 0) / 1024, 2)
                })
        
        total_unused_size = sum(f['size'] for f in unused_css + unused_js)
        
        return {
            'css_files_total': len(css_files),
            'js_files_total': len(js_files),
            'html_files_analyzed': len(html_files[:10]),
            'html_inline_css_blocks': html_inline_css,
            'html_inline_js_blocks': html_inline_js,
            'potentially_unused_css': len(unused_css),
            'potentially_unused_js': len(unused_js),
            'unused_css_files': sorted(unused_css, key=lambda x: x['size'], reverse=True)[:15],
            'unused_js_files': sorted(unused_js, key=lambda x: x['size'], reverse=True)[:15],
            'total_unused_size_bytes': total_unused_size,
            'total_unused_size_kb': round(total_unused_size / 1024, 2),
            'total_unused_size_mb': round(total_unused_size / (1024 * 1024), 2),
            'note': 'Analyse basique. Vérification manuelle recommandée avant suppression.'
        }
