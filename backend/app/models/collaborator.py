from sqlalchemy import Column, String, Integer, ForeignKey, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.core.database import Base


class Collaborator(Base):
    __tablename__ = "collaborators"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("research_projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255))
    institution = Column(String(255))
    department = Column(String(255))
    role = Column(String(100))
    contribution = Column(Text)
    order_index = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("ResearchProject", back_populates="collaborators")