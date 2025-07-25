from sqlalchemy import Column, String, ForeignKey, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.core.database import Base


class StatisticalAnalysis(Base):
    __tablename__ = "statistical_analyses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("research_projects.id", ondelete="CASCADE"), nullable=False)
    analysis_name = Column(String(255), nullable=False)
    analysis_type = Column(String(100))
    software_used = Column(String(100))
    parameters = Column(JSONB)
    results = Column(JSONB)
    interpretation = Column(Text)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("ResearchProject", back_populates="statistical_analyses")
    creator = relationship("User", back_populates="statistical_analyses")