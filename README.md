# 🌱 Green Optimizer

**Optimisez l'empreinte carbone de votre projet web** - Défi Nuit d'Info 🌙

Application web qui analyse et optimise automatiquement les projets GitHub pour réduire leur impact environnemental.

## ✨ Fonctionnalités

- 🔍 **Analyse de dépôts GitHub** : Détection des fichiers non utilisés, commentaires excessifs, espaces inutiles
- ⚡ **Optimisations automatiques** : Compression d'images (WebP), minification CSS/JS/HTML, nettoyage de code
- 📦 **Export optimisé** : Téléchargement du projet nettoyé en ZIP

## 🚀 Installation

### Backend (Python)

```bash
cd Backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**API disponible sur** : http://localhost:8000 | [Docs](http://localhost:8000/docs)

### Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

**App disponible sur** : http://localhost:5173

## 💻 Utilisation

1. Ouvrez http://localhost:5173
2. Entrez l'URL du dépôt GitHub : `https://github.com/username/repo`
3. Cliquez sur **"Analyser le Site 🚀"**
4. Consultez le rapport d'analyse
5. Lancez l'optimisation et téléchargez le projet optimisé

## 📚 API Endpoints

```python
# Analyser un dépôt
POST /api/analyze
{
  "repo_url": "https://github.com/username/repo",
  "branch": "main"
}

# Optimiser le projet
POST /api/optimize
{
  "analysis_id": "abc123...",
  "cleanup_options": {
    "remove_comments": true,
    "optimize_images": true,
    "minify_code": true
  }
}

# Vérifier le statut
GET /api/optimize/status/{job_id}

# Télécharger le résultat
GET /api/download/{job_id}
```

## 🛠️ Technologies

**Backend** : FastAPI, Pillow, BeautifulSoup4, cssutils  
**Frontend** : React 19, Vite, React Router

## 📁 Structure

```
Green-Optimizer/
├── Backend/
│   ├── app/
│   │   ├── main.py              # API FastAPI
│   │   ├── models.py            # Modèles Pydantic
│   │   └── services/            # Analyseurs et optimiseurs
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── components/          # Composants React
    │   └── App.jsx
    └── package.json
```

---

**Made with 💚 for a greener web**
