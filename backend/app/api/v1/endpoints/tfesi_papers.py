"""
TFESI (Transforaminal Epidural Steroid Injection) Papers API
초음파 유도 경추간공 경막외 주사 논문 관리 API
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Optional
from pathlib import Path
import json
import os

router = APIRouter()

# Base path for TFESI papers
TFESI_BASE_PATH = Path("/home/drjang00/DevEnvironments/spinalsurgery-research/research_papers/ultrasound_guided_tfesi")
PROPOSED_STUDY_PATH = Path("/home/drjang00/DevEnvironments/spinalsurgery-research/research_papers/proposed_tfesi_study")

@router.get("/list")
async def list_tfesi_papers():
    """TFESI 논문 목록 조회"""
    try:
        papers = []
        
        # 다운로드된 논문들
        if TFESI_BASE_PATH.exists():
            for folder in TFESI_BASE_PATH.iterdir():
                if folder.is_dir() and folder.name.startswith("PMC"):
                    metadata_file = folder / "metadata.json"
                    if metadata_file.exists():
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                            papers.append({
                                "id": folder.name,
                                "type": "published",
                                "title": metadata.get("title", "Unknown Title"),
                                "journal": metadata.get("journal", ""),
                                "year": metadata.get("year", ""),
                                "pmid": metadata.get("pmid", ""),
                                "pmc_id": metadata.get("pmc_id", ""),
                                "folder": str(folder)
                            })
        
        # 제안된 연구
        if PROPOSED_STUDY_PATH.exists():
            papers.append({
                "id": "proposed_study",
                "type": "proposed",
                "title": "요추 신경근병증 환자에서 초음파 유도와 형광투시 유도 TFESI 비교 연구",
                "title_en": "Comparison of US-Guided and FL-Guided TFESI in Lumbar Radiculopathy",
                "folder": str(PROPOSED_STUDY_PATH)
            })
        
        return {
            "status": "success",
            "count": len(papers),
            "papers": papers
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/paper/{paper_id}")
async def get_paper_details(paper_id: str):
    """특정 논문의 상세 정보 조회"""
    try:
        if paper_id == "proposed_study":
            # 제안된 연구 정보
            files = {}
            if PROPOSED_STUDY_PATH.exists():
                for file in PROPOSED_STUDY_PATH.glob("*.md"):
                    with open(file, 'r', encoding='utf-8') as f:
                        files[file.stem] = f.read()
            
            return {
                "status": "success",
                "paper": {
                    "id": paper_id,
                    "type": "proposed",
                    "title": "요추 신경근병증 환자에서 초음파 유도와 형광투시 유도 TFESI 비교 연구",
                    "files": files
                }
            }
        
        else:
            # 다운로드된 논문 정보
            paper_folder = TFESI_BASE_PATH / paper_id
            if not paper_folder.exists():
                raise HTTPException(status_code=404, detail="Paper not found")
            
            # 메타데이터 읽기
            metadata = {}
            metadata_file = paper_folder / "metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
            
            # 파일들 읽기
            files = {}
            for file in paper_folder.iterdir():
                if file.suffix in ['.txt', '.md']:
                    with open(file, 'r', encoding='utf-8') as f:
                        files[file.stem] = f.read()
                elif file.suffix == '.pdf':
                    files[file.stem] = f"PDF file: {file.name}"
            
            return {
                "status": "success",
                "paper": {
                    "id": paper_id,
                    "type": "published",
                    "metadata": metadata,
                    "files": files
                }
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/file/{paper_id}/{filename}")
async def get_paper_file(paper_id: str, filename: str):
    """특정 논문의 파일 내용 조회"""
    try:
        if paper_id == "proposed_study":
            file_path = PROPOSED_STUDY_PATH / f"{filename}.md"
        else:
            paper_folder = TFESI_BASE_PATH / paper_id
            file_path = paper_folder / filename
            
            # 여러 확장자 시도
            if not file_path.exists():
                for ext in ['.txt', '.md', '.json']:
                    test_path = paper_folder / f"{filename}{ext}"
                    if test_path.exists():
                        file_path = test_path
                        break
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "status": "success",
            "filename": file_path.name,
            "content": content,
            "type": file_path.suffix
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_tfesi_content(
    query: str = Query(..., description="검색어"),
    lang: Optional[str] = Query("all", description="언어 필터 (all, ko, en)")
):
    """TFESI 논문 내용 검색"""
    try:
        results = []
        query_lower = query.lower()
        
        # 모든 논문 폴더 검색
        all_paths = []
        if TFESI_BASE_PATH.exists():
            all_paths.extend([p for p in TFESI_BASE_PATH.iterdir() if p.is_dir()])
        if PROPOSED_STUDY_PATH.exists():
            all_paths.append(PROPOSED_STUDY_PATH)
        
        for folder in all_paths:
            for file in folder.rglob("*"):
                if file.suffix in ['.txt', '.md', '.json']:
                    try:
                        with open(file, 'r', encoding='utf-8') as f:
                            content = f.read().lower()
                            
                        # 언어 필터
                        if lang == "ko" and not any(ord(char) >= 0xAC00 and ord(char) <= 0xD7A3 for char in content):
                            continue
                        elif lang == "en" and any(ord(char) >= 0xAC00 and ord(char) <= 0xD7A3 for char in content):
                            continue
                        
                        if query_lower in content:
                            # 매칭된 부분 찾기
                            start = max(0, content.find(query_lower) - 100)
                            end = min(len(content), content.find(query_lower) + len(query_lower) + 100)
                            snippet = content[start:end]
                            
                            results.append({
                                "paper_id": folder.name,
                                "file": file.name,
                                "path": str(file.relative_to(folder.parent)),
                                "snippet": f"...{snippet}...",
                                "match_count": content.count(query_lower)
                            })
                            
                    except Exception:
                        continue
        
        return {
            "status": "success",
            "query": query,
            "count": len(results),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary")
async def get_tfesi_summary():
    """TFESI 연구 전체 요약"""
    try:
        summary = {
            "downloaded_papers": 0,
            "proposed_studies": 0,
            "total_files": 0,
            "languages": {"korean": 0, "english": 0},
            "file_types": {}
        }
        
        # 다운로드된 논문 카운트
        if TFESI_BASE_PATH.exists():
            for folder in TFESI_BASE_PATH.iterdir():
                if folder.is_dir() and folder.name.startswith("PMC"):
                    summary["downloaded_papers"] += 1
                    
                    for file in folder.iterdir():
                        summary["total_files"] += 1
                        ext = file.suffix
                        summary["file_types"][ext] = summary["file_types"].get(ext, 0) + 1
                        
                        if "korean" in file.name or "한국" in file.name:
                            summary["languages"]["korean"] += 1
                        else:
                            summary["languages"]["english"] += 1
        
        # 제안된 연구 카운트
        if PROPOSED_STUDY_PATH.exists():
            summary["proposed_studies"] += 1
            for file in PROPOSED_STUDY_PATH.iterdir():
                summary["total_files"] += 1
                ext = file.suffix
                summary["file_types"][ext] = summary["file_types"].get(ext, 0) + 1
        
        return {
            "status": "success",
            "summary": summary
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))