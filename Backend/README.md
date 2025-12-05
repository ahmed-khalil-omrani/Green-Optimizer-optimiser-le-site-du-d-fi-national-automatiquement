# Green Optimizer Backend

Backend API for analyzing and optimizing GitHub repositories for ecological performance.

## Project Structure

```
Backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app, CORS, Endpoints
│   ├── models.py               # Pydantic models
│   └── services/
│       ├── __init__.py
│       ├── github_analyzer.py  # GitHubAnalyzer class
│       ├── image_optimizer.py  # ImageOptimizer class
│       ├── code_optimizer.py   # CodeOptimizer class
│       ├── page_analyzer.py    # PageAnalyzer class
│       └── optimization_engine.py # OptimizationEngine class
└── requirements.txt            # Dependencies
```

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Server

```bash
# From the Backend directory
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Analysis
- `POST /api/analyze` - Analyze a GitHub repository
- `GET /api/analysis/{analysis_id}` - Get analysis results
- `GET /api/analyses` - List recent analyses
- `DELETE /api/analysis/{analysis_id}` - Delete an analysis

### Optimization
- `POST /api/optimize` - Optimize repository files
- `GET /api/optimization/{optimization_id}` - Get optimization results

### Health
- `GET /` - API information
- `GET /api/health` - Health check

## Example Usage

```python
import requests

# Analyze a repository
response = requests.post('http://localhost:8000/api/analyze', json={
    'repo_url': 'https://github.com/username/repo',
    'branch': 'main',
    'github_token': 'optional_token'
})

analysis = response.json()
print(f"EcoIndex Score: {analysis['metrics']['ecoindex']['score']}")

# Optimize the repository
response = requests.post('http://localhost:8000/api/optimize', json={
    'analysis_id': analysis['analysis_id'],
    'optimizations': ['images', 'css', 'js', 'html']
})

optimization = response.json()
print(f"Total savings: {optimization['summary']['total_savings_mb']} MB")
```

## Features

- **Image Optimization**: Convert images to WebP/AVIF format
- **Code Minification**: Minify CSS, JavaScript, and HTML
- **Dead Code Detection**: Identify unused CSS/JS files
- **EcoIndex Calculation**: Calculate environmental impact score
- **Optimization Planning**: Generate detailed optimization recommendations

## Technologies

- **FastAPI**: Modern web framework
- **Pillow**: Image processing
- **cssutils**: CSS parsing and minification
- **BeautifulSoup4**: HTML parsing
- **httpx**: Async HTTP client for GitHub API
