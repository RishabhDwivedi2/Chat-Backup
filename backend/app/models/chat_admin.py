# app/models/chat_admin.py 

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum
from sqlalchemy.sql import func
from .base import Base
import enum

class CompanyType(str, enum.Enum):  
    BANK = "Bank"
    CREDIT_UNION = "Credit Union"
    FINTECH = "Fintech"
    INSURANCE = "Insurance"
    INVESTMENT_FIRM = "Investment Firm"
    OTHER = "Other"

class ChatAdmin(Base):
    __tablename__ = "chat_admins"
    
    id = Column(Integer, primary_key=True, index=True)
    admin_first_name = Column(String, nullable=False)
    admin_last_name = Column(String, nullable=False)
    admin_email = Column(String, unique=True, index=True, nullable=False)
    admin_password = Column(String, nullable=False)
    company_name = Column(String, nullable=False)
    company_type = Column(String, nullable=False)  
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    assistant_email = Column(String, nullable=True)
    assistant_email_created_at = Column(DateTime(timezone=True), nullable=True)
    is_assistant_email_generated = Column(Boolean, default=False)