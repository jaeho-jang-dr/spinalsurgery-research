from sqlalchemy import Column, String, Date, DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
import enum

from app.core.database import Base


class ProjectStatus(str, enum.Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PUBLISHED = "published"


class ResearchProject(Base):
    __tablename__ = "research_projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(500), nullable=False)
    field = Column(String(255), nullable=False)
    keywords = Column(ARRAY(Text))
    description = Column(Text)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.DRAFT)
    start_date = Column(Date)
    end_date = Column(Date)
    irb_number = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="research_projects")
    papers = relationship("Paper", back_populates="project", cascade="all, delete-orphan")
    patients = relationship("Patient", back_populates="project", cascade="all, delete-orphan")
    collaborators = relationship("Collaborator", back_populates="project", cascade="all, delete-orphan")
    statistical_analyses = relationship("StatisticalAnalysis", back_populates="project", cascade="all, delete-orphan")
    informed_consents = relationship("InformedConsent", back_populates="project", cascade="all, delete-orphan")
    ai_logs = relationship("AIGenerationLog", back_populates="project")