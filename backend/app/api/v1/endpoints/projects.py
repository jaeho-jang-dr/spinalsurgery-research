from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.api import deps
from app.core.database import get_db
from app.models.user import User
from app.models.project import ResearchProject
from app.schemas.project import Project, ProjectCreate, ProjectUpdate

router = APIRouter()


@router.get("/", response_model=List[Project])
async def read_projects(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=100),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Get list of user's research projects"""
    query = (
        select(ResearchProject)
        .where(ResearchProject.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .options(
            selectinload(ResearchProject.papers),
            selectinload(ResearchProject.patients),
            selectinload(ResearchProject.collaborators)
        )
    )
    
    result = await db.execute(query)
    projects = result.scalars().all()
    
    # Add counts
    projects_with_counts = []
    for project in projects:
        project_dict = project.__dict__.copy()
        project_dict["papers_count"] = len(project.papers)
        project_dict["patients_count"] = len(project.patients)
        project_dict["collaborators_count"] = len(project.collaborators)
        projects_with_counts.append(Project(**project_dict))
    
    return projects_with_counts


@router.post("/", response_model=Project)
async def create_project(
    *,
    db: AsyncSession = Depends(get_db),
    project_in: ProjectCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Create new research project"""
    project = ResearchProject(
        **project_in.dict(),
        user_id=current_user.id
    )
    
    db.add(project)
    await db.commit()
    await db.refresh(project)
    
    project_dict = project.__dict__.copy()
    project_dict["papers_count"] = 0
    project_dict["patients_count"] = 0
    project_dict["collaborators_count"] = 0
    
    return Project(**project_dict)


@router.get("/{project_id}", response_model=Project)
async def read_project(
    *,
    db: AsyncSession = Depends(get_db),
    project_id: str,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Get project by ID"""
    query = (
        select(ResearchProject)
        .where(
            ResearchProject.id == project_id,
            ResearchProject.user_id == current_user.id
        )
        .options(
            selectinload(ResearchProject.papers),
            selectinload(ResearchProject.patients),
            selectinload(ResearchProject.collaborators)
        )
    )
    
    result = await db.execute(query)
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project_dict = project.__dict__.copy()
    project_dict["papers_count"] = len(project.papers)
    project_dict["patients_count"] = len(project.patients)
    project_dict["collaborators_count"] = len(project.collaborators)
    
    return Project(**project_dict)


@router.put("/{project_id}", response_model=Project)
async def update_project(
    *,
    db: AsyncSession = Depends(get_db),
    project_id: str,
    project_in: ProjectUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Update project"""
    query = select(ResearchProject).where(
        ResearchProject.id == project_id,
        ResearchProject.user_id == current_user.id
    )
    
    result = await db.execute(query)
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    update_data = project_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    
    await db.commit()
    await db.refresh(project)
    
    # Load relationships
    await db.execute(
        select(ResearchProject)
        .where(ResearchProject.id == project_id)
        .options(
            selectinload(ResearchProject.papers),
            selectinload(ResearchProject.patients),
            selectinload(ResearchProject.collaborators)
        )
    )
    
    project_dict = project.__dict__.copy()
    project_dict["papers_count"] = len(project.papers)
    project_dict["patients_count"] = len(project.patients)
    project_dict["collaborators_count"] = len(project.collaborators)
    
    return Project(**project_dict)


@router.delete("/{project_id}")
async def delete_project(
    *,
    db: AsyncSession = Depends(get_db),
    project_id: str,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Delete project"""
    query = select(ResearchProject).where(
        ResearchProject.id == project_id,
        ResearchProject.user_id == current_user.id
    )
    
    result = await db.execute(query)
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    await db.delete(project)
    await db.commit()
    
    return {"message": "Project deleted successfully"}