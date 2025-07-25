from sqlalchemy import Column, String, Integer, Date, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
import enum

from app.core.database import Base


class PaperType(str, enum.Enum):
    ORIGINAL = "original"
    REVIEW = "review"
    CASE_REPORT = "case_report"
    META_ANALYSIS = "meta_analysis"
    EDITORIAL = "editorial"


class PresentationType(str, enum.Enum):
    ORAL = "oral"
    POSTER = "poster"
    KEYNOTE = "keynote"


class SourceType(str, enum.Enum):
    JOURNAL = "journal"
    INSTITUTION = "institution"
    DATABASE = "database"
    CONFERENCE = "conference"


class AccessType(str, enum.Enum):
    OPEN = "open"
    SUBSCRIPTION = "subscription"
    INSTITUTIONAL = "institutional"
    REQUEST = "request"


class PaperSource(Base):
    __tablename__ = "paper_sources"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    type = Column(Enum(SourceType), nullable=False)
    url = Column(String(500))
    contact_email = Column(String(255))
    contact_phone = Column(String(50))
    address = Column(Text)
    priority = Column(Integer, default=5)
    access_type = Column(Enum(AccessType))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    papers = relationship("Paper", back_populates="source")


class Paper(Base):
    __tablename__ = "papers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("research_projects.id", ondelete="SET NULL"))
    source_id = Column(UUID(as_uuid=True), ForeignKey("paper_sources.id", ondelete="SET NULL"))
    title = Column(String(500), nullable=False)
    authors = Column(ARRAY(Text))
    abstract = Column(Text)
    content = Column(Text)
    doi = Column(String(255))
    pmid = Column(String(50))
    publication_year = Column(Integer)
    publication_date = Column(Date)
    journal_name = Column(String(255))
    volume = Column(String(50))
    issue = Column(String(50))
    pages = Column(String(50))
    paper_type = Column(Enum(PaperType))
    is_own_paper = Column(Boolean, default=False)
    presentation_date = Column(Date)
    presentation_venue = Column(String(255))
    presentation_type = Column(Enum(PresentationType))
    file_path = Column(String(500))
    url = Column(String(500))
    citation_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("ResearchProject", back_populates="papers")
    source = relationship("PaperSource", back_populates="papers")
    portfolio_entries = relationship("PaperPortfolio", back_populates="paper", cascade="all, delete-orphan")
    citations_made = relationship("PaperReference", foreign_keys="PaperReference.citing_paper_id", back_populates="citing_paper")
    citations_received = relationship("PaperReference", foreign_keys="PaperReference.cited_paper_id", back_populates="cited_paper")


class PaperPortfolio(Base):
    __tablename__ = "paper_portfolio"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    paper_id = Column(UUID(as_uuid=True), ForeignKey("papers.id", ondelete="CASCADE"), nullable=False)
    category = Column(String(100))
    tags = Column(ARRAY(Text))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="paper_portfolio")
    paper = relationship("Paper", back_populates="portfolio_entries")


class PaperReference(Base):
    __tablename__ = "paper_references"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    citing_paper_id = Column(UUID(as_uuid=True), ForeignKey("papers.id", ondelete="CASCADE"), nullable=False)
    cited_paper_id = Column(UUID(as_uuid=True), ForeignKey("papers.id", ondelete="CASCADE"), nullable=False)
    reference_order = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    citing_paper = relationship("Paper", foreign_keys=[citing_paper_id], back_populates="citations_made")
    cited_paper = relationship("Paper", foreign_keys=[cited_paper_id], back_populates="citations_received")