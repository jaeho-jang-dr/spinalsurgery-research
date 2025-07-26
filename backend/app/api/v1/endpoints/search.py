"""
Search API endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from datetime import datetime
import json
import os
from pathlib import Path

router = APIRouter()

# Search sites configuration
SEARCH_SITES = [
    {
        "id": "pubmed",
        "name": "PubMed",
        "url": "https://pubmed.ncbi.nlm.nih.gov/",
        "description": "National Library of Medicine database",
        "enabled": True
    },
    {
        "id": "pmc",
        "name": "PubMed Central",
        "url": "https://www.ncbi.nlm.nih.gov/pmc/",
        "description": "Free full-text archive",
        "enabled": True
    },
    {
        "id": "google_scholar",
        "name": "Google Scholar",
        "url": "https://scholar.google.com/",
        "description": "Academic search engine",
        "enabled": True
    },
    {
        "id": "cochrane",
        "name": "Cochrane Library",
        "url": "https://www.cochranelibrary.com/",
        "description": "Systematic reviews database",
        "enabled": False
    },
    {
        "id": "scopus",
        "name": "Scopus",
        "url": "https://www.scopus.com/",
        "description": "Abstract and citation database",
        "enabled": False
    }
]

# In-memory job storage (should be replaced with database in production)
search_jobs = {}

@router.get("/search-sites")
async def get_search_sites():
    """Get available search sites"""
    return SEARCH_SITES

@router.post("/projects/{project_id}/start-research")
async def start_research(project_id: str, data: Dict[str, Any]):
    """Start a research/search job"""
    job_id = f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{project_id}"
    
    # Create job entry
    search_jobs[job_id] = {
        "id": job_id,
        "project_id": project_id,
        "status": "running",
        "progress": 0,
        "total_expected": data.get("target_count", 100),
        "search_query": f"Project {project_id} research",
        "started_at": datetime.now().isoformat(),
        "ai_option": data.get("ai_option", "search"),
        "site_ids": data.get("site_ids", ["pubmed", "pmc"])
    }
    
    # Log search sites to file
    search_log_dir = Path(f"./research_projects/search_logs")
    search_log_dir.mkdir(parents=True, exist_ok=True)
    
    search_log = {
        "job_id": job_id,
        "project_id": project_id,
        "started_at": datetime.now().isoformat(),
        "search_sites": [site for site in SEARCH_SITES if site["id"] in data.get("site_ids", [])],
        "target_count": data.get("target_count", 100),
        "ai_option": data.get("ai_option", "search")
    }
    
    with open(search_log_dir / f"{job_id}_search_log.json", "w", encoding="utf-8") as f:
        json.dump(search_log, f, indent=2, ensure_ascii=False)
    
    return {
        "status": "success",
        "job_id": job_id,
        "message": "Research started successfully"
    }

@router.get("/jobs/{job_id}")
async def get_search_job(job_id: str):
    """Get search job status"""
    if job_id not in search_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = search_jobs[job_id]
    
    # Simulate progress
    if job["status"] == "running":
        job["progress"] = min(job["progress"] + 10, job["total_expected"])
        if job["progress"] >= job["total_expected"]:
            job["status"] = "completed"
            job["completed_at"] = datetime.now().isoformat()
    
    return job

@router.post("/jobs/{job_id}/pause")
async def pause_search_job(job_id: str):
    """Pause a search job"""
    if job_id not in search_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    search_jobs[job_id]["status"] = "paused"
    return {"status": "success", "message": "Job paused"}

@router.post("/jobs/{job_id}/resume")
async def resume_search_job(job_id: str):
    """Resume a search job"""
    if job_id not in search_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    search_jobs[job_id]["status"] = "running"
    return {"status": "success", "message": "Job resumed"}

@router.post("/jobs/{job_id}/cancel")
async def cancel_search_job(job_id: str):
    """Cancel a search job"""
    if job_id not in search_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    search_jobs[job_id]["status"] = "cancelled"
    search_jobs[job_id]["cancelled_at"] = datetime.now().isoformat()
    return {"status": "success", "message": "Job cancelled"}

@router.get("/projects/{project_id}/search-sessions")
async def get_search_sessions(project_id: str):
    """Get search sessions for a project"""
    sessions = []
    
    # Get sessions from search jobs
    for job_id, job in search_jobs.items():
        if job["project_id"] == project_id:
            sessions.append({
                "id": job_id,
                "search_query": job["search_query"],
                "started_at": job["started_at"],
                "status": job["status"],
                "total_results": job["progress"],
                "abstract_count": int(job["progress"] * 0.7),  # Mock data
                "fulltext_count": int(job["progress"] * 0.3),  # Mock data
                "job_status": job["status"],
                "result_file_path": f"./research_projects/search_logs/{job_id}_results.json"
            })
    
    return sessions