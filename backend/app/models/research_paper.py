from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import uuid


class ResearchPaper(Base):
    """Research paper model for storing academic papers"""
    __tablename__ = "research_papers"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Paper metadata
    pmid = Column(String, unique=True, nullable=True)  # PubMed ID
    title = Column(Text, nullable=False)
    abstract = Column(Text)
    authors = Column(JSON)  # List of authors
    journal = Column(String)
    year = Column(String)
    doi = Column(String, nullable=True)
    pmc_id = Column(String, nullable=True)  # PubMed Central ID
    
    # Paper content
    full_text = Column(Text, nullable=True)
    has_full_text = Column(Boolean, default=False)
    
    # Classification
    fusion_type = Column(String)  # PLIF, TLIF, ALIF, LLIF, OLIF, etc.
    keywords = Column(JSON)  # List of keywords
    study_type = Column(String)  # Prospective, Retrospective, RCT, etc.
    
    # User association
    added_by = Column(String, ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="research_papers")
    
    # File paths
    abstract_file_path = Column(String, nullable=True)
    full_text_file_path = Column(String, nullable=True)
    pdf_file_path = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Additional metadata
    notes = Column(Text, nullable=True)  # User notes
    tags = Column(JSON, nullable=True)  # User-defined tags
    relevance_score = Column(Integer, nullable=True)  # 1-5 rating
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "pmid": self.pmid,
            "title": self.title,
            "abstract": self.abstract,
            "authors": self.authors,
            "journal": self.journal,
            "year": self.year,
            "doi": self.doi,
            "pmc_id": self.pmc_id,
            "full_text": self.full_text,
            "has_full_text": self.has_full_text,
            "fusion_type": self.fusion_type,
            "keywords": self.keywords,
            "study_type": self.study_type,
            "added_by": self.added_by,
            "abstract_file_path": self.abstract_file_path,
            "full_text_file_path": self.full_text_file_path,
            "pdf_file_path": self.pdf_file_path,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "notes": self.notes,
            "tags": self.tags,
            "relevance_score": self.relevance_score
        }