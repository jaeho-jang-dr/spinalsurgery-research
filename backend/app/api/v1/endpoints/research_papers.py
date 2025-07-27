from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.api import deps
from app.models.user import User
from app.models.research_paper import ResearchPaper
from app.services.sample_papers_generator import sample_generator
import json
import os

router = APIRouter()


@router.get("/", response_model=List[Dict[str, Any]])
async def get_research_papers(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    fusion_type: Optional[str] = None,
    year: Optional[str] = None,
    has_full_text: Optional[bool] = None,
    search_query: Optional[str] = None,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Get research papers with optional filtering"""
    
    # For now, load from generated sample papers
    papers_metadata_path = "/home/drjang00/DevEnvironments/spinalsurgery-research/research_papers/lumbar_fusion_2year_outcomes/papers_metadata.json"
    
    if os.path.exists(papers_metadata_path):
        with open(papers_metadata_path, 'r', encoding='utf-8') as f:
            all_papers = json.load(f)
    else:
        # Generate papers if not exist
        folder_path, papers = sample_generator.save_papers_to_folder()
        all_papers = papers
    
    # Apply filters
    filtered_papers = all_papers
    
    if fusion_type:
        filtered_papers = [p for p in filtered_papers if fusion_type.lower() in p['fusion_type'].lower()]
    
    if year:
        filtered_papers = [p for p in filtered_papers if p['year'] == year]
    
    if has_full_text is not None:
        filtered_papers = [p for p in filtered_papers if p['has_full_text'] == has_full_text]
    
    if search_query:
        search_lower = search_query.lower()
        filtered_papers = [
            p for p in filtered_papers 
            if search_lower in p['title'].lower() or 
               search_lower in p['abstract'].lower() or
               any(search_lower in author.lower() for author in p['authors']) or
               any(search_lower in keyword.lower() for keyword in p.get('keywords', []))
        ]
    
    # Apply pagination
    papers = filtered_papers[skip:skip + limit]
    
    return papers


@router.get("/{paper_id}", response_model=Dict[str, Any])
async def get_research_paper(
    paper_id: str,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Get a specific research paper by PMID"""
    
    # Load papers
    papers_metadata_path = "/home/drjang00/DevEnvironments/spinalsurgery-research/research_papers/lumbar_fusion_2year_outcomes/papers_metadata.json"
    
    if os.path.exists(papers_metadata_path):
        with open(papers_metadata_path, 'r', encoding='utf-8') as f:
            all_papers = json.load(f)
        
        # Find paper by PMID
        paper = next((p for p in all_papers if p['pmid'] == paper_id), None)
        
        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")
        
        # Add file content if requested
        paper_folder = "/home/drjang00/DevEnvironments/spinalsurgery-research/research_papers/lumbar_fusion_2year_outcomes"
        fusion_folder = os.path.join(paper_folder, paper['fusion_type'].replace('/', '_'))
        
        # Find abstract file
        for file in os.listdir(fusion_folder):
            if paper_id in file and "_abstract.txt" in file:
                abstract_path = os.path.join(fusion_folder, file)
                with open(abstract_path, 'r', encoding='utf-8') as f:
                    paper['abstract_content'] = f.read()
                break
        
        # Find full text file if available
        if paper['has_full_text']:
            for file in os.listdir(fusion_folder):
                if paper_id in file and "_full_text.txt" in file:
                    full_text_path = os.path.join(fusion_folder, file)
                    with open(full_text_path, 'r', encoding='utf-8') as f:
                        paper['full_text_content'] = f.read()
                    break
        
        return paper
    
    raise HTTPException(status_code=404, detail="Papers not found")


@router.get("/fusion-types/list", response_model=List[str])
async def get_fusion_types(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Get list of available fusion types"""
    
    papers_metadata_path = "/home/drjang00/DevEnvironments/spinalsurgery-research/research_papers/lumbar_fusion_2year_outcomes/papers_metadata.json"
    
    if os.path.exists(papers_metadata_path):
        with open(papers_metadata_path, 'r', encoding='utf-8') as f:
            all_papers = json.load(f)
        
        fusion_types = sorted(list(set(p['fusion_type'] for p in all_papers)))
        return fusion_types
    
    return []


@router.get("/years/list", response_model=List[str])
async def get_years(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Get list of available years"""
    
    papers_metadata_path = "/home/drjang00/DevEnvironments/spinalsurgery-research/research_papers/lumbar_fusion_2year_outcomes/papers_metadata.json"
    
    if os.path.exists(papers_metadata_path):
        with open(papers_metadata_path, 'r', encoding='utf-8') as f:
            all_papers = json.load(f)
        
        years = sorted(list(set(p['year'] for p in all_papers)), reverse=True)
        return years
    
    return []


@router.post("/import-from-pubmed")
async def import_from_pubmed(
    search_query: str,
    year_start: int = 2020,
    year_end: int = 2025,
    max_results: int = 50,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Import papers from PubMed (currently returns mock data)"""
    
    # For now, return existing sample papers
    return {
        "message": "Import completed (using sample data)",
        "papers_imported": 10,
        "search_query": search_query,
        "year_range": f"{year_start}-{year_end}"
    }