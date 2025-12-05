import httpx
from typing import List, Dict, Optional
from urllib.parse import urlparse
from fastapi import HTTPException
import logging
import base64

logger = logging.getLogger(__name__)

class GitHubAnalyzer:
    """Gestionnaire d'interactions avec l'API GitHub"""
    
    def __init__(self, repo_url: str, branch: str = "main", token: Optional[str] = None):
        self.repo_url = repo_url
        self.branch = branch
        self.token = token
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        
        if token:
            self.headers["Authorization"] = f"token {token}"
        
        # Parse repo info
        parsed = urlparse(str(repo_url))
        path_parts = parsed.path.strip('/').split('/')
        
        if len(path_parts) < 2:
            raise ValueError("Invalid GitHub URL format")
            
        self.owner = path_parts[0]
        self.repo = path_parts[1].replace('.git', '')
        self.api_base = f"https://api.github.com/repos/{self.owner}/{self.repo}"
        
        logger.info(f"Initialized analyzer for {self.owner}/{self.repo}")
    
    async def get_repo_tree(self) -> List[Dict]:
        """Récupère l'arborescence complète du repository"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = f"{self.api_base}/git/trees/{self.branch}?recursive=1"
            response = await client.get(url, headers=self.headers)
            
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Repository or branch not found")
            elif response.status_code == 403:
                raise HTTPException(status_code=403, detail="API rate limit exceeded. Please provide a GitHub token")
            elif response.status_code != 200:
                raise HTTPException(status_code=400, detail=f"GitHub API error: {response.text}")
            
            data = response.json()
            tree = data.get("tree", [])
            logger.info(f"Retrieved {len(tree)} files from repository")
            return tree
    
    async def get_file_content(self, path: str) -> bytes:
        """Télécharge le contenu d'un fichier"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = f"{self.api_base}/contents/{path}?ref={self.branch}"
            response = await client.get(url, headers=self.headers)
            
            if response.status_code != 200:
                logger.warning(f"Failed to fetch {path}: {response.status_code}")
                return b""
            
            data = response.json()
            if data.get("encoding") == "base64":
                return base64.b64decode(data["content"])
            return b""
    
    async def get_repo_info(self) -> Dict:
        """Récupère les informations du repository"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(self.api_base, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            return {}
