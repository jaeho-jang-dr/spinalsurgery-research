"""
Lumbar Fusion Papers API Endpoints
"""
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from pathlib import Path
import json

from app.api import deps
from app.models.user import User

router = APIRouter()

@router.get("/list", response_model=List[dict])
async def list_lumbar_fusion_papers(
    *,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    List all downloaded lumbar fusion papers
    """
    papers_path = Path("/home/drjang00/DevEnvironments/spinalsurgery-research/research_papers/lumbar_fusion_2025")
    papers_list = []
    
    if papers_path.exists():
        for folder in papers_path.iterdir():
            if folder.is_dir():
                metadata_file = folder / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                        papers_list.append({
                            'pmid': metadata['pmid'],
                            'title': metadata['title'],
                            'korean_title': metadata.get('korean_translation', {}).get('title'),
                            'authors': metadata['authors'],
                            'journal': metadata['journal'],
                            'year': metadata['year'],
                            'doi': metadata['doi'],
                            'folder': str(folder),
                            'has_korean': bool(metadata.get('korean_translation'))
                        })
    
    # Sort by year (newest first)
    papers_list.sort(key=lambda x: x['year'], reverse=True)
    
    return papers_list

@router.get("/{pmid}", response_model=dict)
async def get_lumbar_fusion_paper(
    *,
    pmid: str,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Get detailed information about a specific lumbar fusion paper
    """
    papers_path = Path("/home/drjang00/DevEnvironments/spinalsurgery-research/research_papers/lumbar_fusion_2025")
    
    # Find the paper folder
    for folder in papers_path.iterdir():
        if folder.is_dir() and folder.name.startswith(pmid):
            metadata_file = folder / "metadata.json"
            summary_file = folder / "summary_korean.txt"
            
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                # Read Korean summary if exists
                korean_summary = None
                if summary_file.exists():
                    with open(summary_file, 'r', encoding='utf-8') as f:
                        korean_summary = f.read()
                
                return {
                    'pmid': metadata['pmid'],
                    'title': metadata['title'],
                    'authors': metadata['authors'],
                    'journal': metadata['journal'],
                    'year': metadata['year'],
                    'doi': metadata['doi'],
                    'abstract': metadata['abstract'],
                    'korean_translation': metadata.get('korean_translation'),
                    'korean_summary': korean_summary,
                    'folder': str(folder),
                    'download_date': metadata.get('download_date')
                }
    
    raise HTTPException(status_code=404, detail=f"Paper with PMID {pmid} not found")

@router.get("/summary", response_model=dict)
async def get_downloaded_papers_summary(
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Get summary of all downloaded lumbar fusion papers
    """
    papers_path = Path("/home/drjang00/DevEnvironments/spinalsurgery-research/research_papers/lumbar_fusion_2025")
    downloaded_path = Path("/home/drjang00/DevEnvironments/spinalsurgery-research/downloaded_papers")
    
    lumbar_fusion_count = 0
    other_papers_count = 0
    total_korean_translations = 0
    
    # Count lumbar fusion papers
    if papers_path.exists():
        for folder in papers_path.iterdir():
            if folder.is_dir():
                lumbar_fusion_count += 1
                metadata_file = folder / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                        if metadata.get('korean_translation'):
                            total_korean_translations += 1
    
    # Count other downloaded papers
    if downloaded_path.exists():
        for folder in downloaded_path.iterdir():
            if folder.is_dir():
                other_papers_count += 1
    
    return {
        'lumbar_fusion_papers': lumbar_fusion_count,
        'other_papers': other_papers_count,
        'total_papers': lumbar_fusion_count + other_papers_count,
        'korean_translations': total_korean_translations,
        'storage_paths': {
            'lumbar_fusion': str(papers_path),
            'other_papers': str(downloaded_path)
        }
    }