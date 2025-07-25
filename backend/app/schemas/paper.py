from typing import Optional, List
from pydantic import BaseModel, UUID4
from datetime import date, datetime
from app.models.paper import PaperType, PresentationType, SourceType, AccessType


class PaperSourceBase(BaseModel):
    name: str
    type: SourceType
    url: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    priority: int = 5
    access_type: Optional[AccessType] = None
    notes: Optional[str] = None


class PaperSourceCreate(PaperSourceBase):
    pass


class PaperSource(PaperSourceBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PaperBase(BaseModel):
    title: str
    authors: Optional[List[str]] = []
    abstract: Optional[str] = None
    doi: Optional[str] = None
    pmid: Optional[str] = None
    publication_year: Optional[int] = None
    journal_name: Optional[str] = None
    paper_type: Optional[PaperType] = None
    is_own_paper: bool = False


class PaperCreate(PaperBase):
    project_id: Optional[UUID4] = None
    source_id: Optional[UUID4] = None


class PaperUpdate(BaseModel):
    title: Optional[str] = None
    authors: Optional[List[str]] = None
    abstract: Optional[str] = None
    content: Optional[str] = None
    doi: Optional[str] = None
    publication_year: Optional[int] = None
    journal_name: Optional[str] = None


class Paper(PaperBase):
    id: UUID4
    project_id: Optional[UUID4] = None
    source_id: Optional[UUID4] = None
    content: Optional[str] = None
    publication_date: Optional[date] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    presentation_date: Optional[date] = None
    presentation_venue: Optional[str] = None
    presentation_type: Optional[PresentationType] = None
    file_path: Optional[str] = None
    url: Optional[str] = None
    citation_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True