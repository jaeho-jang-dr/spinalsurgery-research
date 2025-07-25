from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.core.database import get_db
from app.models.user import User
from app.services.ai_service import ai_service
from app.services.scraper_service import scraper_service

router = APIRouter()


@router.post("/generate-draft")
async def generate_paper_draft(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    data: dict
) -> Any:
    """Generate paper draft using AI"""
    try:
        # Search for related papers first
        search_results = await scraper_service.search_papers(
            query=f"{data['field']} {data['title']}",
            limit=10
        )
        
        # Generate draft
        draft = await ai_service.generate_paper_draft(
            title=data['title'],
            field=data['field'],
            keywords=data['keywords'],
            details=data['details'],
            references=search_results
        )
        
        return draft
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/informed-consent/{project_id}")
async def generate_informed_consent(
    *,
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    data: dict
) -> Any:
    """Generate informed consent for project"""
    try:
        # Get project details
        # ... fetch project from DB ...
        
        consent = await ai_service.generate_informed_consent(
            project_title=data.get('project_title', 'Research Study'),
            field=data.get('field', 'Medical Research'),
            procedures=data['procedures'],
            risks=data['risks'],
            benefits=data['benefits']
        )
        
        return {"content": consent}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/statistics")
async def generate_statistics_analysis(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    data: dict
) -> Any:
    """Generate statistical analysis plan"""
    try:
        analysis = await ai_service.analyze_statistics(
            data_description=data['data_description'],
            analysis_type=data['analysis_type'],
            variables=data['variables']
        )
        
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search-papers")
async def search_papers(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    query: str,
    sources: list = ["pubmed", "scholar"],
    limit: int = 20
) -> Any:
    """Search for papers from multiple sources"""
    try:
        results = await scraper_service.search_papers(
            query=query,
            sources=sources,
            limit=limit
        )
        
        return {"results": results, "total": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))