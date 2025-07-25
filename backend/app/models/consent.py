from sqlalchemy import Column, String, Integer, ForeignKey, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.core.database import Base


class InformedConsent(Base):
    __tablename__ = "informed_consents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("research_projects.id", ondelete="CASCADE"), nullable=False)
    template_name = Column(String(255))
    content = Column(Text, nullable=False)
    version = Column(Integer, default=1)
    language = Column(String(10), default='ko')
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    approved_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("ResearchProject", back_populates="informed_consents")
    approver = relationship("User", back_populates="approved_consents")