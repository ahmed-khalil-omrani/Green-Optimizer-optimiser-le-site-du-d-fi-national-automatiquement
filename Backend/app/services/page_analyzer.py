from typing import List, Dict, Any
from pathlib import Path

class PageAnalyzer:
    """Analyseur principal de pages web"""
    
    @staticmethod
    def analyze_requests(files: List[Dict]) -> Dict[str, Any]:
        """Analyse le nombre et la taille des requêtes"""
        
        categories = {
            'html': ['.html', '.htm'],
            'css': ['.css'],
            'js': ['.js', '.mjs', '.jsx', '.ts', '.tsx'],
            'images': ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.avif', '.ico', '.bmp'],
            'fonts': ['.woff', '.woff2', '.ttf', '.otf', '.eot'],
            'videos': ['.mp4', '.webm', '.ogg', '.avi'],
            'data': ['.json', '.xml', '.csv'],
            'other': []
        }
        
        categorized = {cat: [] for cat in categories.keys()}
        
        for f in files:
            if f['type'] != 'blob':
                continue
                
            ext = Path(f['path']).suffix.lower()
            categorized_flag = False
            
            for category, extensions in categories.items():
                if category == 'other':
                    continue
                if ext in extensions:
                    categorized[category].append(f)
                    categorized_flag = True
                    break
            
            if not categorized_flag:
                categorized['other'].append(f)
        
        # Calculer les statistiques
        summary = {}
        total_requests = 0
        total_size = 0
        
        for category, items in categorized.items():
            count = len(items)
            size = sum(item.get('size', 0) for item in items)
            total_requests += count
            total_size += size
            
            summary[category] = {
                'count': count,
                'size_bytes': size,
                'size_kb': round(size / 1024, 2),
                'size_mb': round(size / (1024 * 1024), 2),
                'largest_files': sorted(
                    [{'path': i['path'], 'size_kb': round(i.get('size', 0) / 1024, 2)} for i in items],
                    key=lambda x: x['size_kb'],
                    reverse=True
                )[:5] if items else []
            }
        
        # Recommandations
        recommendations = []
        if summary['js']['count'] > 10:
            recommendations.append(f"⚠ {summary['js']['count']} fichiers JS détectés. Envisagez le bundling.")
        if summary['css']['count'] > 5:
            recommendations.append(f"⚠ {summary['css']['count']} fichiers CSS détectés. Envisagez le bundling.")
        if total_requests > 50:
            recommendations.append(f"⚠ {total_requests} requêtes HTTP. Activez HTTP/2 ou HTTP/3.")
        if summary['images']['size_mb'] > 5:
            recommendations.append(f"⚠ Images totalisent {summary['images']['size_mb']} MB. Optimisation recommandée.")
        
        return {
            'total_requests': total_requests,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'by_category': summary,
            'recommendations': recommendations,
            'avg_file_size_kb': round((total_size / total_requests / 1024) if total_requests > 0 else 0, 2)
        }
    
    @staticmethod
    def calculate_ecoindex(metrics: Dict) -> Dict[str, Any]:
        """Calcule un score EcoIndex simplifié"""
        
        total_size_mb = metrics['requests']['total_size_mb']
        total_requests = metrics['requests']['total_requests']
        total_images = metrics['images']['total_images']
        
        # Calcul des scores (0-100, plus c'est haut mieux c'est)
        size_score = max(0, 100 - (total_size_mb * 8))
        requests_score = max(0, 100 - (total_requests * 1.5))
        images_score = max(0, 100 - (total_images * 1))
        
        # Score global pondéré
        overall_score = (size_score * 0.4 + requests_score * 0.35 + images_score * 0.25)
        
        # Attribution du grade
        if overall_score >= 80:
            grade, rating, color = 'A', 'Excellent', 'green'
        elif overall_score >= 65:
            grade, rating, color = 'B', 'Très Bon', 'lightgreen'
        elif overall_score >= 50:
            grade, rating, color = 'C', 'Bon', 'yellow'
        elif overall_score >= 35:
            grade, rating, color = 'D', 'Moyen', 'orange'
        elif overall_score >= 20:
            grade, rating, color = 'E', 'Faible', 'red'
        else:
            grade, rating, color = 'F', 'Très Faible', 'darkred'
        
        # Estimation CO2 (formule simplifiée)
        co2_grams = total_size_mb * 0.6  # ~0.6g CO2 par MB
        
        return {
            'score': round(overall_score, 1),
            'grade': grade,
            'rating': rating,
            'color': color,
            'components': {
                'size_score': round(size_score, 1),
                'requests_score': round(requests_score, 1),
                'images_score': round(images_score, 1)
            },
            'co2_estimate': {
                'grams_per_visit': round(co2_grams, 2),
                'trees_to_offset_1000_visits': round((co2_grams * 1000) / 21000, 2)  # 1 arbre absorbe ~21kg CO2/an
            },
            'recommendations': generate_ecoindex_recommendations(overall_score, metrics)
        }

def generate_ecoindex_recommendations(score: float, metrics: Dict) -> List[str]:
    """Génère des recommandations basées sur le score"""
    recs = []
    
    if metrics['requests']['total_size_mb'] > 3:
        recs.append("📦 Réduire le poids total (> 3 MB)")
    if metrics['requests']['total_requests'] > 40:
        recs.append("🔗 Réduire le nombre de requêtes (> 40)")
    if metrics['images']['total_size_mb'] > 2:
        recs.append("🖼 Optimiser les images (> 2 MB)")
    if metrics['dead_code']['total_unused_size_kb'] > 100:
        recs.append("🗑 Supprimer le code non utilisé")
    
    if score >= 80:
        recs.append("✅ Excellent travail ! Continuez ainsi.")
    elif score >= 50:
        recs.append("💡 Bon début. Quelques optimisations possibles.")
    else:
        recs.append("⚠ Optimisations importantes recommandées.")
    
    return recs
