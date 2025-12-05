"""
Green Optimizer Backend - Complete Advanced Version
Features:
- Detection des fichiers non utilisés
- Suppression des commentaires
- Suppression des espaces inutiles
- Clonage du projet
- Nettoyage automatique
- Compression des images
- Génération d'archive optimisée
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List, Dict, Any, Tuple, Set
import httpx
import asyncio
from pathlib import Path
import base64
import re
from datetime import datetime
import hashlib
from urllib.parse import urlparse
import json
import io
from PIL import Image
import cssutils
import jsbeautifier
from bs4 import BeautifulSoup
import logging
import tempfile
import shutil
import zipfile
import os
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
cssutils.log.setLevel(logging.CRITICAL)

app = FastAPI(
    title="Green Optimizer API - Advanced",
    version="3.0.0",
    description="Analyse, nettoyage et optimisation complète de projets web"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== MODELS ====================

class GitHubRepoRequest(BaseModel):
    repo_url: HttpUrl
    branch: str = "main"
    github_token: Optional[str] = None

class CleanupOptions(BaseModel):
    remove_comments: bool = True
    remove_whitespace: bool = True
    remove_unused_files: bool = True
    optimize_images: bool = True
    minify_code: bool = True

class FullOptimizationRequest(BaseModel):
    analysis_id: str
    cleanup_options: CleanupOptions = CleanupOptions()
    output_format: str = "zip"

# ==================== STORAGE ====================

analyses_storage: Dict[str, Dict] = {}
optimization_jobs: Dict[str, Dict] = {}
cleaned_projects: Dict[str, str] = {}

# ==================== GITHUB ANALYZER ====================

class GitHubAnalyzer:
    def __init__(self, repo_url: str, branch: str = "main", token: Optional[str] = None):
        self.repo_url = repo_url
        self.branch = branch
        self.token = token
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        
        if token:
            self.headers["Authorization"] = f"token {token}"
        
        parsed = urlparse(str(repo_url))
        path_parts = parsed.path.strip('/').split('/')
        
        if len(path_parts) < 2:
            raise ValueError("Invalid GitHub URL format")
            
        self.owner = path_parts[0]
        self.repo = path_parts[1].replace('.git', '')
        self.api_base = f"https://api.github.com/repos/{self.owner}/{self.repo}"
    
    async def get_repo_tree(self) -> List[Dict]:
        """Récupère l'arbre complet du dépôt"""
        url = f"{self.api_base}/git/trees/{self.branch}?recursive=1"
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data.get('tree', [])
    
    async def get_file_content(self, file_path: str) -> bytes:
        """Récupère le contenu d'un fichier"""
        url = f"{self.api_base}/contents/{file_path}?ref={self.branch}"
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            if 'content' in data:
                return base64.b64decode(data['content'])
            return b''

# ==================== ADVANCED ANALYZERS ====================

class AdvancedCodeAnalyzer:
    """Analyseur avancé de code pour détecter les problèmes"""
    
    @staticmethod
    def analyze_comments(content: str, file_type: str) -> Dict[str, Any]:
        """Analyse les commentaires dans un fichier"""
        
        total_lines = content.count('\n') + 1
        comment_lines = 0
        comments_found = []
        
        if file_type in ['js', 'jsx', 'ts', 'tsx', 'css']:
            # Commentaires multi-lignes
            multiline_comments = re.findall(r'/\.?\*/', content, re.DOTALL)
            for comment in multiline_comments:
                lines = comment.count('\n') + 1
                comment_lines += lines
                comments_found.append({
                    'type': 'multiline',
                    'lines': lines,
                    'preview': comment[:100] + '...' if len(comment) > 100 else comment
                })
            
            # Commentaires simples
            single_comments = re.findall(r'//.*', content)
            comment_lines += len(single_comments)
            comments_found.extend([{
                'type': 'single',
                'lines': 1,
                'preview': c[:80]
            } for c in single_comments[:5]])
        
        elif file_type in ['html', 'htm', 'xml']:
            html_comments = re.findall(r'<!--.*?-->', content, re.DOTALL)
            for comment in html_comments:
                lines = comment.count('\n') + 1
                comment_lines += lines
                comments_found.append({
                    'type': 'html',
                    'lines': lines,
                    'preview': comment[:100] + '...' if len(comment) > 100 else comment
                })
        
        elif file_type in ['py']:
            python_comments = re.findall(r'#.*', content)
            comment_lines += len(python_comments)
            
            docstrings = re.findall(r'""".?"""|\'\'\'.?\'\'\'', content, re.DOTALL)
            for doc in docstrings:
                comment_lines += doc.count('\n') + 1
        
        comment_percent = (comment_lines / total_lines * 100) if total_lines > 0 else 0
        
        return {
            'total_lines': total_lines,
            'comment_lines': comment_lines,
            'comment_percent': round(comment_percent, 2),
            'code_lines': total_lines - comment_lines,
            'comments_found': comments_found[:10],
            'has_excessive_comments': comment_percent > 30
        }
    
    @staticmethod
    def analyze_whitespace(content: str) -> Dict[str, Any]:
        """Analyse les espaces blancs inutiles"""
        
        original_size = len(content.encode('utf-8'))
        
        multiple_spaces = len(re.findall(r'  +', content))
        multiple_newlines = len(re.findall(r'\n\s*\n\s*\n', content))
        trailing_spaces = len(re.findall(r' +\n', content))
        tabs_count = content.count('\t')
        
        cleaned = content
        cleaned = re.sub(r'  +', ' ', cleaned)
        cleaned = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned)
        cleaned = re.sub(r' +\n', '\n', cleaned)
        cleaned = re.sub(r'\t', '  ', cleaned)
        
        cleaned_size = len(cleaned.encode('utf-8'))
        savings = original_size - cleaned_size
        
        return {
            'original_size': original_size,
            'cleaned_size': cleaned_size,
            'savings_bytes': savings,
            'savings_percent': round((savings / original_size * 100) if original_size > 0 else 0, 2),
            'issues': {
                'multiple_spaces': multiple_spaces,
                'multiple_newlines': multiple_newlines,
                'trailing_spaces': trailing_spaces,
                'tabs': tabs_count
            },
            'has_issues': multiple_spaces > 0 or multiple_newlines > 0 or trailing_spaces > 0
        }
    
    @staticmethod
    async def detect_unused_files_advanced(analyzer, files: List[Dict]) -> Dict[str, Any]:
        """Détection avancée des fichiers non utilisés"""
        
        html_files = [f for f in files if f['path'].endswith(('.html', '.htm')) and f['type'] == 'blob']
        css_files = [f for f in files if f['path'].endswith('.css') and f['type'] == 'blob']
        js_files = [f for f in files if f['path'].endswith(('.js', '.mjs')) and f['type'] == 'blob']
        image_files = [f for f in files if any(f['path'].endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp']) and f['type'] == 'blob']
        
        referenced_files = set()
        all_file_paths = {f['path'] for f in files}
        
        html_references = set()
        for html_file in html_files[:20]:
            try:
                content = await analyzer.get_file_content(html_file['path'])
                text = content.decode('utf-8', errors='ignore')
                
                css_refs = re.findall(r'href=["\']([^"\']+\.css)["\']', text, re.IGNORECASE)
                html_references.update(css_refs)
                
                js_refs = re.findall(r'src=["\']([^"\']+\.js)["\']', text, re.IGNORECASE)
                html_references.update(js_refs)
                
                img_refs = re.findall(r'(?:src|href)=["\']([^"\']+\.(?:jpg|jpeg|png|gif|svg|webp))["\']', text, re.IGNORECASE)
                html_references.update(img_refs)
                
                bg_imgs = re.findall(r'url\(["\']?([^"\'()]+)["\']?\)', text, re.IGNORECASE)
                html_references.update(bg_imgs)
                
            except Exception as e:
                logger.error(f"Error analyzing HTML {html_file['path']}: {str(e)}")
        
        css_references = set()
        for css_file in css_files[:20]:
            try:
                content = await analyzer.get_file_content(css_file['path'])
                text = content.decode('utf-8', errors='ignore')
                
                img_refs = re.findall(r'url\(["\']?([^"\'()]+)["\']?\)', text, re.IGNORECASE)
                css_references.update(img_refs)
                
                import_refs = re.findall(r'@import\s+["\']([^"\']+)["\']', text, re.IGNORECASE)
                css_references.update(import_refs)
                
            except Exception as e:
                logger.error(f"Error analyzing CSS {css_file['path']}: {str(e)}")
        
        js_references = set()
        for js_file in js_files[:20]:
            try:
                content = await analyzer.get_file_content(js_file['path'])
                text = content.decode('utf-8', errors='ignore')
                
                imports = re.findall(r'import\s+.*?from\s+["\']([^"\']+)["\']', text, re.IGNORECASE)
                js_references.update(imports)
                
                requires = re.findall(r'require\(["\']([^"\']+)["\']\)', text, re.IGNORECASE)
                js_references.update(requires)
                
                img_refs = re.findall(r'["\']([^"\']+\.(?:jpg|jpeg|png|gif|svg|webp))["\']', text, re.IGNORECASE)
                js_references.update(img_refs)
                
            except Exception as e:
                logger.error(f"Error analyzing JS {js_file['path']}: {str(e)}")
        
        all_references = html_references | css_references | js_references
        
        def normalize_path(ref_path: str, base_path: str) -> Set[str]:
            possible_paths = set()
            ref_path = ref_path.split('?')[0].split('#')[0]
            
            if ref_path.startswith(('http://', 'https://', '//', 'data:')):
                return possible_paths
            
            if ref_path.startswith('/'):
                possible_paths.add(ref_path[1:])
            else:
                base_dir = str(Path(base_path).parent)
                if base_dir == '.':
                    possible_paths.add(ref_path)
                else:
                    possible_paths.add(f"{base_dir}/{ref_path}")
                possible_paths.add(ref_path)
            
            possible_paths.add(Path(ref_path).name)
            return possible_paths
        
        for ref in all_references:
            for file_path in all_file_paths:
                possible_paths = normalize_path(ref, file_path)
                if any(file_path.endswith(p) or p in file_path for p in possible_paths):
                    referenced_files.add(file_path)
        
        unused_css = []
        unused_js = []
        unused_images = []
        
        for css_file in css_files:
            if css_file['path'] not in referenced_files:
                if not any(common in css_file['path'].lower() for common in ['bootstrap', 'normalize', 'reset']):
                    unused_css.append({
                        'path': css_file['path'],
                        'size': css_file.get('size', 0),
                        'size_kb': round(css_file.get('size', 0) / 1024, 2)
                    })
        
        for js_file in js_files:
            if js_file['path'] not in referenced_files:
                if not any(lib in js_file['path'].lower() for lib in ['jquery', 'bootstrap', 'react', 'vue', 'angular', 'lodash']):
                    unused_js.append({
                        'path': js_file['path'],
                        'size': js_file.get('size', 0),
                        'size_kb': round(js_file.get('size', 0) / 1024, 2)
                    })
        
        for img_file in image_files:
            if img_file['path'] not in referenced_files:
                unused_images.append({
                    'path': img_file['path'],
                    'size': img_file.get('size', 0),
                    'size_kb': round(img_file.get('size', 0) / 1024, 2)
                })
        
        total_unused = sum(f['size'] for f in unused_css + unused_js + unused_images)
        
        return {
            'analysis_method': 'advanced_dependency_graph',
            'total_files_analyzed': len(files),
            'html_files': len(html_files),
            'css_files': len(css_files),
            'js_files': len(js_files),
            'image_files': len(image_files),
            'total_references_found': len(all_references),
            'unused_css': {
                'count': len(unused_css),
                'files': sorted(unused_css, key=lambda x: x['size'], reverse=True)[:20],
                'total_size_kb': round(sum(f['size'] for f in unused_css) / 1024, 2)
            },
            'unused_js': {
                'count': len(unused_js),
                'files': sorted(unused_js, key=lambda x: x['size'], reverse=True)[:20],
                'total_size_kb': round(sum(f['size'] for f in unused_js) / 1024, 2)
            },
            'unused_images': {
                'count': len(unused_images),
                'files': sorted(unused_images, key=lambda x: x['size'], reverse=True)[:20],
                'total_size_kb': round(sum(f['size'] for f in unused_images) / 1024, 2)
            },
            'total_unused_size_bytes': total_unused,
            'total_unused_size_mb': round(total_unused / (1024 * 1024), 2),
            'confidence_level': 'high' if len(html_files) > 0 else 'medium'
        }

# ==================== CODE CLEANERS ====================

class CodeCleaner:
    """Nettoyeur de code avancé"""
    
    @staticmethod
    def remove_comments(content: str, file_type: str) -> str:
        """Supprime les commentaires d'un fichier"""
        
        if file_type in ['js', 'jsx', 'ts', 'tsx']:
            content = re.sub(r'/\.?\*/', '', content, flags=re.DOTALL)
            content = re.sub(r'//.*', '', content)
        
        elif file_type in ['css']:
            content = re.sub(r'/\.?\*/', '', content, flags=re.DOTALL)
        
        elif file_type in ['html', 'htm']:
            content = re.sub(r'<!--(?!\[if).*?-->', '', content, flags=re.DOTALL)
        
        elif file_type == 'py':
            lines = content.split('\n')
            cleaned_lines = []
            in_docstring = False
            
            for line in lines:
                if '\"\"\"' in line or "'''" in line:
                    in_docstring = not in_docstring
                    if not in_docstring:
                        continue
                
                if in_docstring:
                    continue
                
                if '#' in line:
                    code_part = line.split('#')[0]
                    if code_part.strip():
                        cleaned_lines.append(code_part.rstrip())
                else:
                    cleaned_lines.append(line)
            
            content = '\n'.join(cleaned_lines)
        
        return content
    
    @staticmethod
    def clean_whitespace(content: str, aggressive: bool = False) -> str:
        """Nettoie les espaces blancs inutiles"""
        
        content = re.sub(r' +\n', '\n', content)
        
        if aggressive:
            content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        else:
            content = re.sub(r'\n\s*\n\s*\n\s*\n+', '\n\n\n', content)
        
        content = content.replace('\t', '  ')
        
        lines = content.split('\n')
        cleaned_lines = []
        for line in lines:
            indent = len(line) - len(line.lstrip())
            rest = re.sub(r'  +', ' ', line[indent:])
            cleaned_lines.append(line[:indent] + rest)
        
        content = '\n'.join(cleaned_lines)
        content = content.strip() + '\n'
        
        return content
    
    @staticmethod
    def minify_css(content: str) -> str:
        """Minifie le CSS"""
        try:
            sheet = cssutils.parseString(content)
            minified = sheet.cssText.decode('utf-8') if isinstance(sheet.cssText, bytes) else sheet.cssText
            
            minified = re.sub(r'\s+', ' ', minified)
            minified = re.sub(r'\s*([{}:;,])\s*', r'\1', minified)
            minified = minified.strip()
            
            return minified
        except:
            return content
    
    @staticmethod
    def minify_js(content: str) -> str:
        """Minifie le JavaScript"""
        try:
            content = re.sub(r'/\.?\*/', '', content, flags=re.DOTALL)
            content = re.sub(r'//.*', '', content)
            
            content = re.sub(r'\s+', ' ', content)
            content = re.sub(r'\s*([{}();,])\s*', r'\1', content)
            content = content.strip()
            
            return content
        except:
            return content
    
    @staticmethod
    def minify_html(content: str) -> str:
        """Minifie le HTML"""
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            for comment in soup.find_all(string=lambda text: isinstance(text, str) and '<!--' in text):
                comment.extract()
            
            minified = str(soup)
            minified = re.sub(r'\s+', ' ', minified)
            minified = re.sub(r'>\s+<', '><', minified)
            
            return minified.strip()
        except:
            return content

# ==================== PROJECT OPTIMIZER ====================

class ProjectOptimizer:
    """Clone et optimise un projet complet"""
    
    def __init__(self, analyzer, analysis_data: Dict, cleanup_options: CleanupOptions):
        self.analyzer = analyzer
        self.analysis = analysis_data
        self.options = cleanup_options
        self.temp_dir = tempfile.mkdtemp(prefix='green_optimizer_')
        self.stats = {
            'files_processed': 0,
            'files_deleted': 0,
            'bytes_saved': 0,
            'comments_removed': 0,
            'whitespace_cleaned': 0,
            'images_optimized': 0
        }
    
    async def clone_and_optimize(self) -> str:
        """Clone le projet et applique toutes les optimisations"""
        
        logger.info(f"Starting project optimization in {self.temp_dir}")
        
        try:
            files = await self.analyzer.get_repo_tree()
            
            for file_info in files:
                if file_info['type'] == 'tree':
                    dir_path = Path(self.temp_dir) / file_info['path']
                    dir_path.mkdir(parents=True, exist_ok=True)
            
            files_to_delete = set()
            if self.options.remove_unused_files:
                unused_data = self.analysis['metrics'].get('unused_files_advanced', {})
                for unused_css in unused_data.get('unused_css', {}).get('files', []):
                    files_to_delete.add(unused_css['path'])
                for unused_js in unused_data.get('unused_js', {}).get('files', []):
                    files_to_delete.add(unused_js['path'])
                for unused_img in unused_data.get('unused_images', {}).get('files', []):
                    files_to_delete.add(unused_img['path'])
            
            for file_info in files:
                if file_info['type'] != 'blob':
                    continue
                
                file_path = file_info['path']
                
                if file_path in files_to_delete:
                    self.stats['files_deleted'] += 1
                    logger.info(f"Skipping unused file: {file_path}")
                    continue
                
                try:
                    content = await self.analyzer.get_file_content(file_path)
                    if not content:
                        continue
                    
                    original_size = len(content)
                    file_ext = Path(file_path).suffix.lower().replace('.', '')
                    
                    if file_ext in ['jpg', 'jpeg', 'png', 'bmp'] and self.options.optimize_images:
                        content = await self._optimize_image(content)
                        self.stats['images_optimized'] += 1
                    
                    elif file_ext in ['css', 'js', 'html', 'htm', 'py', 'jsx', 'tsx', 'ts']:
                        text_content = content.decode('utf-8', errors='ignore')
                        
                        if self.options.remove_comments:
                            original_text = text_content
                            text_content = CodeCleaner.remove_comments(text_content, file_ext)
                            if len(text_content) < len(original_text):
                                self.stats['comments_removed'] += 1
                        
                        if self.options.remove_whitespace:
                            original_text = text_content
                            text_content = CodeCleaner.clean_whitespace(text_content, aggressive=True)
                            if len(text_content) < len(original_text):
                                self.stats['whitespace_cleaned'] += 1
                        
                        if self.options.minify_code:
                            if file_ext == 'css':
                                text_content = CodeCleaner.minify_css(text_content)
                            elif file_ext in ['js', 'jsx', 'ts', 'tsx']:
                                text_content = CodeCleaner.minify_js(text_content)
                            elif file_ext in ['html', 'htm']:
                                text_content = CodeCleaner.minify_html(text_content)
                        
                        content = text_content.encode('utf-8')
                    
                    output_path = Path(self.temp_dir) / file_path
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(output_path, 'wb') as f:
                        f.write(content)
                    
                    new_size = len(content)
                    self.stats['bytes_saved'] += (original_size - new_size)
                    self.stats['files_processed'] += 1
                    
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {str(e)}")
                    continue
            
            logger.info(f"Optimization complete: {self.stats}")
            return self.temp_dir
            
        except Exception as e:
            logger.error(f"Project optimization failed: {str(e)}")
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            raise
    
    async def _optimize_image(self, image_data: bytes) -> bytes:
        """Optimise une image"""
        try:
            img = Image.open(io.BytesIO(image_data))
            
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                if img.mode in ('RGBA', 'LA'):
                    background.paste(img, mask=img.split()[-1])
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            output = io.BytesIO()
            img.save(output, format='WEBP', quality=85, method=6)
            return output.getvalue()
            
        except:
            return image_data
    
    def create_archive(self, format: str = 'zip') -> str:
        """Crée une archive du projet optimisé"""
        
        archive_name = f"optimized_project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if format == 'zip':
            archive_path = f"{self.temp_dir}.zip"
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(self.temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, self.temp_dir)
                        zipf.write(file_path, arcname)
        else:
            archive_path = f"{self.temp_dir}.tar.gz"
            import tarfile
            with tarfile.open(archive_path, 'w:gz') as tar:
                tar.add(self.temp_dir, arcname=archive_name)
        
        return archive_path

# ==================== API ENDPOINTS ====================

@app.post("/api/analyze")
async def analyze_repository(request: GitHubRepoRequest):
    """Analyse complète d'un dépôt GitHub"""
    
    analysis_id = hashlib.md5(f"{request.repo_url}{datetime.now()}".encode()).hexdigest()
    
    try:
        analyzer = GitHubAnalyzer(
            str(request.repo_url),
            request.branch,
            request.github_token
        )
        
        files = await analyzer.get_repo_tree()
        
        metrics = {
            'total_files': len(files),
            'total_size': sum(f.get('size', 0) for f in files if f['type'] == 'blob')
        }
        
        code_files = [f for f in files if f['type'] == 'blob' and any(f['path'].endswith(ext) for ext in ['.js', '.css', '.html', '.py'])]
        
        comments_analysis = []
        whitespace_analysis = []
        
        for file_info in code_files[:10]:
            try:
                content = await analyzer.get_file_content(file_info['path'])
                text = content.decode('utf-8', errors='ignore')
                file_ext = Path(file_info['path']).suffix.replace('.', '')
                
                comment_data = AdvancedCodeAnalyzer.analyze_comments(text, file_ext)
                comment_data['file'] = file_info['path']
                comments_analysis.append(comment_data)
                
                ws_data = AdvancedCodeAnalyzer.analyze_whitespace(text)
                ws_data['file'] = file_info['path']
                whitespace_analysis.append(ws_data)
                
            except Exception as e:
                logger.error(f"Error analyzing {file_info['path']}: {str(e)}")
        
        metrics['comments_analysis'] = {
            'files_analyzed': len(comments_analysis),
            'total_comment_lines': sum(c['comment_lines'] for c in comments_analysis),
            'avg_comment_percent': round(sum(c['comment_percent'] for c in comments_analysis) / len(comments_analysis), 2) if comments_analysis else 0,
            'files_with_excessive_comments': sum(1 for c in comments_analysis if c['has_excessive_comments']),
            'details': comments_analysis
        }
        
        metrics['whitespace_analysis'] = {
            'files_analyzed': len(whitespace_analysis),
            'total_savings_bytes': sum(w['savings_bytes'] for w in whitespace_analysis),
            'total_savings_kb': round(sum(w['savings_bytes'] for w in whitespace_analysis) / 1024, 2),
            'avg_savings_percent': round(sum(w['savings_percent'] for w in whitespace_analysis) / len(whitespace_analysis), 2) if whitespace_analysis else 0,
            'files_with_issues': sum(1 for w in whitespace_analysis if w['has_issues']),
            'details': whitespace_analysis
        }
        
        unused_files = await AdvancedCodeAnalyzer.detect_unused_files_advanced(analyzer, files)
        metrics['unused_files_advanced'] = unused_files
        
        analysis_result = {
            'analysis_id': analysis_id,
            'repo_url': str(request.repo_url),
            'branch': request.branch,
            'timestamp': datetime.now().isoformat(),
            'metrics': metrics,
            'analyzer': analyzer
        }
        
        analyses_storage[analysis_id] = analysis_result
        
        return {
            'success': True,
            'analysis_id': analysis_id,
            'metrics': metrics
        }
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/optimize")
async def optimize_project(request: FullOptimizationRequest, background_tasks: BackgroundTasks):
    """Optimise et nettoie un projet analysé"""
    
    if request.analysis_id not in analyses_storage:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    job_id = hashlib.md5(f"{request.analysis_id}{datetime.now()}".encode()).hexdigest()
    
    optimization_jobs[job_id] = {
        'status': 'processing',
        'progress': 0,
        'started_at': datetime.now().isoformat()
    }
    
    async def run_optimization():
        try:
            analysis = analyses_storage[request.analysis_id]
            analyzer = analysis['analyzer']
            
            optimizer = ProjectOptimizer(
                analyzer,
                analysis,
                request.cleanup_options
            )
            
            optimization_jobs[job_id]['progress'] = 30
            temp_dir = await optimizer.clone_and_optimize()
            
            optimization_jobs[job_id]['progress'] = 70
            archive_path = optimizer.create_archive(request.output_format)
            
            cleaned_projects[job_id] = archive_path
            
            optimization_jobs[job_id].update({
                'status': 'completed',
                'progress': 100,
                'completed_at': datetime.now().isoformat(),
                'stats': optimizer.stats,
                'archive_path': archive_path
            })
            
        except Exception as e:
            logger.error(f"Optimization failed: {str(e)}")
            optimization_jobs[job_id].update({
                'status': 'failed',
                'error': str(e),
                'completed_at': datetime.now().isoformat()
            })
    
    background_tasks.add_task(run_optimization)
    
    return {
        'success': True,
        'job_id': job_id,
        'message': 'Optimization started'
    }

@app.get("/api/optimize/status/{job_id}")
async def get_optimization_status(job_id: str):
    """Obtient le statut d'une optimisation"""
    
    if job_id not in optimization_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return optimization_jobs[job_id]

@app.get("/api/optimize/download/{job_id}")
async def download_optimized_project(job_id: str):
    """Télécharge le projet optimisé"""
    
    if job_id not in optimization_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = optimization_jobs[job_id]
    
    if job['status'] != 'completed':
        raise HTTPException(status_code=400, detail="Optimization not completed")
    
    archive_path = cleaned_projects.get(job_id)
    
    if not archive_path or not os.path.exists(archive_path):
        raise HTTPException(status_code=404, detail="Archive not found")
    
    return FileResponse(
        archive_path,
        media_type='application/zip' if archive_path.endswith('.zip') else 'application/gzip',
        filename=os.path.basename(archive_path)
    )

@app.get("/api/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    """Récupère les détails d'une analyse"""
    
    if analysis_id not in analyses_storage:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    analysis = analyses_storage[analysis_id].copy()
    analysis.pop('analyzer', None)
    
    return analysis

@app.delete("/api/cleanup/{job_id}")
async def cleanup_files(job_id: str):
    """Nettoie les fichiers temporaires d'une optimisation"""
    
    if job_id in cleaned_projects:
        archive_path = cleaned_projects[job_id]
        
        if os.path.exists(archive_path):
            os.remove(archive_path)
        
        temp_dir = archive_path.replace('.zip', '').replace('.tar.gz', '')
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        
        del cleaned_projects[job_id]
    
    if job_id in optimization_jobs:
        del optimization_jobs[job_id]
    
    return {'success': True, 'message': 'Cleanup completed'}

@app.get("/")
async def root():
    """Endpoint racine"""
    return {
        'name': 'Green Optimizer API',
        'version': '3.0.0',
        'endpoints': {
            'analyze': 'POST /api/analyze',
            'optimize': 'POST /api/optimize',
            'status': 'GET /api/optimize/status/{job_id}',
            'download': 'GET /api/optimize/download/{job_id}',
            'get_analysis': 'GET /api/analysis/{analysis_id}',
            'cleanup': 'DELETE /api/cleanup/{job_id}'
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)