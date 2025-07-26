from sqlalchemy import Column, String, Integer, ForeignKey, Numeric, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.core.database import Base


class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("research_projects.id", ondelete="CASCADE"), nullable=False)
    patient_code = Column(String(100), nullable=False)
    age = Column(Integer)
    gender = Column(String(1))
    height = Column(Numeric(5, 2))
    weight = Column(Numeric(5, 2))
    bmi = Column(Numeric(4, 2))
    diagnosis_data = Column(JSONB)
    surgery_data = Column(JSONB)
    outcome_data = Column(JSONB)
    follow_up_data = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("ResearchProject", back_populates="patients")