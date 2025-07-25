from sqlalchemy import Column, String, Boolean, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
import enum

from app.core.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    RESEARCHER = "researcher"
    VIEWER = "viewer"


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    institution = Column(String(255))
    department = Column(String(255))
    phone = Column(String(50))
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    research_projects = relationship("ResearchProject", back_populates="user", cascade="all, delete-orphan")
    paper_portfolio = relationship("PaperPortfolio", back_populates="user", cascade="all, delete-orphan")
    ai_logs = relationship("AIGenerationLog", back_populates="user", cascade="all, delete-orphan")
    statistical_analyses = relationship("StatisticalAnalysis", foreign_keys="StatisticalAnalysis.created_by", back_populates="creator")
    approved_consents = relationship("InformedConsent", foreign_keys="InformedConsent.approved_by", back_populates="approver")