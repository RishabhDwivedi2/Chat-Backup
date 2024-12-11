# app/models/user.py

from sqlalchemy import Column, Integer, String, Enum, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base

class ThemeModeEnum(Enum):
    LIGHT = 'light'
    DARK = 'dark'

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    role_category = Column(Enum('Debtor', 'FI Admin', 'Resohub Admin', 'Deltabots Admin', name='role_category'), nullable=False)
    password = Column(String, nullable=False)
    color = Column(String, default='zinc')
    mode = Column(Enum('light', 'dark', name='theme_mode'), default='light')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)

    # Relationships
    chat_collections = relationship("ChatCollection", back_populates="user", cascade="all, delete-orphan")
