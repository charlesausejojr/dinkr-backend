from sqlalchemy import Column, String, Boolean, Float, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid


class Court(Base):
    __tablename__ = "courts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    establishment_id = Column(UUID(as_uuid=True), ForeignKey("establishments.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    price_per_hour = Column(Float, nullable=False)
    surface_type = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    establishment = relationship("Establishment", back_populates="courts")
