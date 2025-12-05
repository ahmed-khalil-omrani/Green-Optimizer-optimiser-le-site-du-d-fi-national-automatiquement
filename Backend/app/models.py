from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List, Dict, Any

class GitHubRepoRequest(BaseModel):
    repo_url: HttpUrl
    branch: str = "main"
    github_token: Optional[str] = None

class AnalysisResult(BaseModel):
    repo_url: str
    analysis_id: str
    timestamp: str
    metrics: Dict[str, Any]
    optimization_plan: Dict[str, Any]
    lighthouse_score: Optional[Dict[str, Any]] = None
    status: str

class OptimizationRequest(BaseModel):
    analysis_id: str
    optimizations: List[str] = Field(
        default=["images", "css", "js", "html"],
        description="Types: images, css, js, html, dead_code"
    )
    create_pull_request: bool = False

class FileOptimization(BaseModel):
    path: str
    type: str
    original_size: int
    optimized_size: int
    savings_bytes: int
    savings_percent: float
