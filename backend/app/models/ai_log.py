from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.core.database import Base


class AIGenerationLog(Base):
    __tablename__ = "ai_generation_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("research_projects.id", ondelete="CASCADE"))
    generation_type = Column(String(50), nullable=False)
    input_data = Column(JSONB)
    output_data = Column(JSONB)
    ai_model = Column(String(50))
    processing_time = Column(Integer)
    tokens_used = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="ai_logs")
    project = relationship("ResearchProject", back_populates="ai_logs")