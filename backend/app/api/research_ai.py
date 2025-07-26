"""
Research AI API endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.services.research_ai_service import ResearchAIService

router = APIRouter(prefix="/api/research-ai", tags=["research-ai"])

class ResearchRequest(BaseModel):
    title: str
    type: str  # Clinical Study, Literature Review, Meta-Analysis, etc.
    keywords: List[str]
    objectives: Optional[str] = ""
    description: Optional[str] = ""
    
class ResearchResponse(BaseModel):
    project_id: str
    project_path: str
    status: str
    outputs: Dict[str, Any]
    created_at: str

# Initialize service
research_service = ResearchAIService()

@router.post("/start", response_model=ResearchResponse)
async def start_research(request: ResearchRequest, background_tasks: BackgroundTasks):
    """
    Start a new AI-powered research project
    """
    try:
        # Validate Claude API key
        if not os.getenv("CLAUDE_API_KEY"):
            # For demo, we'll proceed without API key
            print("Warning: CLAUDE_API_KEY not set. Using demo mode.")
        
        # Start research workflow
        result = await research_service.start_new_research({
            'title': request.title,
            'type': request.type,
            'keywords': request.keywords,
            'objectives': request.objectives,
            'description': request.description
        })
        
        return ResearchResponse(
            project_id=result['project_id'],
            project_path=result['project_path'],
            status=result['status'],
            outputs=result['outputs'],
            created_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects")
async def list_projects():
    """
    List all research projects
    """
    try:
        projects = []
        research_base = research_service.research_base_path
        
        if research_base.exists():
            for project_dir in research_base.iterdir():
                if project_dir.is_dir():
                    # Read project summary if exists
                    summary_file = project_dir / "PROJECT_SUMMARY.md"
                    if summary_file.exists():
                        projects.append({
                            'project_id': project_dir.name,
                            'path': str(project_dir),
                            'created': datetime.fromtimestamp(project_dir.stat().st_ctime).isoformat()
                        })
        
        return {"projects": projects}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}")
async def get_project(project_id: str):
    """
    Get details of a specific project
    """
    try:
        project_path = research_service.research_base_path / project_id
        
        if not project_path.exists():
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Read various outputs
        outputs = {}
        
        # Read draft
        draft_file = project_path / "drafts" / "draft_v1.md"
        if draft_file.exists():
            with open(draft_file, "r", encoding="utf-8") as f:
                outputs['draft'] = f.read()
        
        # Read consent
        consent_file = project_path / "consent_forms" / "informed_consent_v1.md"
        if consent_file.exists():
            with open(consent_file, "r", encoding="utf-8") as f:
                outputs['consent'] = f.read()
        
        # Read structure
        structure_file = project_path / "paper_structure.json"
        if structure_file.exists():
            import json
            with open(structure_file, "r", encoding="utf-8") as f:
                outputs['structure'] = json.load(f)
        
        # Read data
        data_file = project_path / "data" / "mock_data.json"
        if data_file.exists():
            import json
            with open(data_file, "r", encoding="utf-8") as f:
                outputs['data'] = json.load(f)
        
        return {
            'project_id': project_id,
            'project_path': str(project_path),
            'outputs': outputs
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/projects/{project_id}/export")
async def export_project(project_id: str, format: str = "markdown"):
    """
    Export project in various formats
    """
    try:
        project_path = research_service.research_base_path / project_id
        
        if not project_path.exists():
            raise HTTPException(status_code=404, detail="Project not found")
        
        # For now, return markdown
        draft_file = project_path / "drafts" / "draft_v1.md"
        if draft_file.exists():
            with open(draft_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            return {
                'format': format,
                'content': content,
                'filename': f"{project_id}_paper.{format}"
            }
        else:
            raise HTTPException(status_code=404, detail="Draft not found")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))