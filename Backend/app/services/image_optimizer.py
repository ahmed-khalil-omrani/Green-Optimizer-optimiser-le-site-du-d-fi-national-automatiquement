from PIL import Image
import io
from typing import Tuple, Dict, List, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ImageOptimizer:
    """Optimiseur d'images avec conversion WebP/AVIF"""
    
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
    
    @staticmethod
    async def optimize_image(image_data: bytes, target_format: str = 'webp', quality: int = 85) -> Tuple[bytes, Dict]:
        """
        Optimise une image en la convertissant au format WebP ou AVIF
        
        Returns:
            (optimized_bytes, metadata)
        """
        try:
            # Ouvrir l'image
            img = Image.open(io.BytesIO(image_data))
            original_size = len(image_data)
            
            # Convertir en RGB si nécessaire
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Optimiser
            output = io.BytesIO()
            
            if target_format.lower() == 'webp':
                img.save(output, format='WEBP', quality=quality, method=6)
            elif target_format.lower() == 'avif':
                # AVIF nécessite pillow-avif-plugin
                try:
                    img.save(output, format='AVIF', quality=quality)
                except:
                    # Fallback vers WebP si AVIF n'est pas disponible
                    img.save(output, format='WEBP', quality=quality, method=6)
                    target_format = 'webp'
            else:
                img.save(output, format='JPEG', quality=quality, optimize=True)
            
            optimized_data = output.getvalue()
            optimized_size = len(optimized_data)
            
            metadata = {
                'original_size': original_size,
                'optimized_size': optimized_size,
                'savings': original_size - optimized_size,
                'savings_percent': ((original_size - optimized_size) / original_size * 100) if original_size > 0 else 0,
                'format': target_format,
                'dimensions': f"{img.width}x{img.height}"
            }
            
            return optimized_data, metadata
            
        except Exception as e:
            logger.error(f"Image optimization failed: {str(e)}")
            return image_data, {'error': str(e)}
    
    @staticmethod
    def analyze_images(files: List[Dict]) -> Dict[str, Any]:
        """Analyse détaillée des images"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.ico', '.webp', '.avif', '.tiff'}
        images = [f for f in files if Path(f['path']).suffix.lower() in image_extensions]
        
        total_size = sum(f.get('size', 0) for f in images)
        
        # Catégorisation par format
        by_format = {}
        large_images = []
        
        for img in images:
            ext = Path(img['path']).suffix.lower()
            size = img.get('size', 0)
            
            if ext not in by_format:
                by_format[ext] = {'count': 0, 'size': 0, 'files': []}
            
            by_format[ext]['count'] += 1
            by_format[ext]['size'] += size
            by_format[ext]['files'].append(img['path'])
            
            # Images > 500KB sont considérées comme grandes
            if size > 500000:
                large_images.append({
                    'path': img['path'],
                    'size': size,
                    'size_mb': round(size / (1024 * 1024), 2)
                })
        
        # Calcul des économies potentielles
        optimizable = []
        potential_savings = 0
        
        for img in images:
            ext = Path(img['path']).suffix.lower()
            size = img.get('size', 0)
            
            if ext in ImageOptimizer.SUPPORTED_FORMATS:
                # Estimation: 40-60% d'économies avec WebP
                estimated_savings = size * 0.5
                potential_savings += estimated_savings
                
                optimizable.append({
                    'path': img['path'],
                    'current_format': ext,
                    'current_size': size,
                    'current_size_kb': round(size / 1024, 2),
                    'suggested_format': 'webp',
                    'estimated_new_size': size - estimated_savings,
                    'estimated_savings': estimated_savings,
                    'estimated_savings_kb': round(estimated_savings / 1024, 2)
                })
        
        return {
            'total_images': len(images),
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'by_format': by_format,
            'large_images': sorted(large_images, key=lambda x: x['size'], reverse=True)[:10],
            'optimizable_images': len(optimizable),
            'optimizable_list': sorted(optimizable, key=lambda x: x['estimated_savings'], reverse=True)[:20],
            'potential_savings_bytes': potential_savings,
            'potential_savings_mb': round(potential_savings / (1024 * 1024), 2),
            'savings_percent': round((potential_savings / total_size * 100) if total_size > 0 else 0, 2)
        }
