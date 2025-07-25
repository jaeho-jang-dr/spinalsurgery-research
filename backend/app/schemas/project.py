from typing import Optional, List
from pydantic import BaseModel, UUID4
from datetime import date, datetime
from app.models.project import ProjectStatus


class ProjectBase(BaseModel):
    title: str
    field: str
    keywords: Optional[List[str]] = []
    description: Optional[str] = None
    status: ProjectStatus = ProjectStatus.DRAFT
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    irb_number: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    field: Optional[str] = None
    keywords: Optional[List[str]] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    irb_number: Optional[str] = None


class ProjectInDBBase(ProjectBase):
    id: UUID4
    user_id: UUID4
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class Project(ProjectInDBBase):
    papers_count: int = 0
    patients_count: int = 0
    collaborators_count: int = 0


class ProjectInDB(ProjectInDBBase):
    pass