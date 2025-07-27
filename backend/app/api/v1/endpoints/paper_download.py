"""
Paper Download API endpoints
"""
from typing import List, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel

from app.api import deps
from app.models.user import User
from app.services.paper_downloader_service import paper_downloader_service

router = APIRouter()

class PaperSearchRequest(BaseModel):
    query: str
    max_results: int = 5
    translate_to_korean: bool = True

class PaperSearchResponse(BaseModel):
    papers: List[Dict]
    total_found: int
    download_folder: str

@router.post("/search-and-download", response_model=PaperSearchResponse)
async def search_and_download_papers(
    request: PaperSearchRequest,
    current_user: User = Depends(deps.get_current_user)
):
    """
    실제 논문을 검색하고 다운로드합니다.
    - PubMed에서 검색
    - PDF 다운로드 (가능한 경우)
    - 텍스트 추출
    - 한글 번역
    """
    try:
        # 논문 검색 및 다운로드
        results = await paper_downloader_service.search_and_download_papers(
            query=request.query,
            max_results=request.max_results,
            translate_to_korean=request.translate_to_korean
        )
        
        if not results:
            raise HTTPException(
                status_code=404,
                detail="No papers found for the given query"
            )
            
        return PaperSearchResponse(
            papers=results,
            total_found=len(results),
            download_folder=str(paper_downloader_service.storage_path)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during paper search and download: {str(e)}"
        )

@router.get("/downloaded-papers")
async def list_downloaded_papers(
    current_user: User = Depends(deps.get_current_user)
):
    """다운로드된 논문 목록 조회 - 모든 저장 위치에서"""
    try:
        papers = []
        
        # 경로 1: 기본 다운로드 폴더
        storage_path = paper_downloader_service.storage_path
        
        # 경로 2: Lumbar fusion 논문 폴더
        lumbar_fusion_path = storage_path.parent / "research_papers" / "lumbar_fusion_2025"
        
        # 모든 경로 목록
        paths_to_check = [storage_path]
        if lumbar_fusion_path.exists():
            paths_to_check.append(lumbar_fusion_path)
        
        # 각 경로에서 논문 검색
        for path in paths_to_check:
            for folder in path.iterdir():
                if folder.is_dir():
                    metadata_file = folder / "metadata.json"
                    if metadata_file.exists():
                        import json
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                            
                        paper_info = {
                            'pmid': metadata.get('pmid'),
                            'title': metadata.get('title'),
                            'year': metadata.get('year'),
                            'folder': str(folder),
                            'has_pdf': (folder / f"{metadata.get('pmid')}.pdf").exists(),
                            'has_translation': 'korean_translation' in metadata,
                            'source': 'lumbar_fusion' if path == lumbar_fusion_path else 'general'
                        }
                        
                        # 한글 제목이 있으면 추가
                        if 'korean_translation' in metadata and metadata['korean_translation']:
                            paper_info['korean_title'] = metadata['korean_translation'].get('title')
                        
                        papers.append(paper_info)
                    
        # 연도별로 정렬 (최신 순)
        papers.sort(key=lambda x: x.get('year', ''), reverse=True)
        
        return {
            'papers': papers,
            'total': len(papers),
            'storage_paths': {
                'general': str(storage_path),
                'lumbar_fusion': str(lumbar_fusion_path) if lumbar_fusion_path.exists() else None
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing papers: {str(e)}"
        )

@router.get("/paper/{pmid}")
async def get_paper_details(
    pmid: str,
    current_user: User = Depends(deps.get_current_user)
):
    """특정 논문의 상세 정보 조회 - 모든 저장 위치에서"""
    try:
        storage_path = paper_downloader_service.storage_path
        lumbar_fusion_path = storage_path.parent / "research_papers" / "lumbar_fusion_2025"
        
        # 모든 경로 목록
        paths_to_check = [storage_path]
        if lumbar_fusion_path.exists():
            paths_to_check.append(lumbar_fusion_path)
        
        # 각 경로에서 PMID로 폴더 찾기
        for path in paths_to_check:
            for folder in path.iterdir():
                if folder.is_dir() and folder.name.startswith(pmid):
                    metadata_file = folder / "metadata.json"
                    if metadata_file.exists():
                        import json
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                            
                        # 요약 파일 읽기 (일반 요약 또는 한글 요약)
                        summary_text = ""
                        summary_file = folder / "summary.txt"
                        korean_summary_file = folder / "summary_korean.txt"
                        
                        if korean_summary_file.exists():
                            with open(korean_summary_file, 'r', encoding='utf-8') as f:
                                summary_text = f.read()
                        elif summary_file.exists():
                            with open(summary_file, 'r', encoding='utf-8') as f:
                                summary_text = f.read()
                                
                        return {
                            'metadata': metadata,
                            'summary': summary_text,
                            'folder': str(folder),
                            'files': [f.name for f in folder.iterdir()],
                            'source': 'lumbar_fusion' if path == lumbar_fusion_path else 'general'
                        }
                    
        raise HTTPException(
            status_code=404,
            detail=f"Paper with PMID {pmid} not found in any storage location"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving paper: {str(e)}"
        )