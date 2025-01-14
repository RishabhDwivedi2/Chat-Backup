# app/schemas/chat_admin.py

from pydantic import BaseModel, EmailStr, constr, Field
from datetime import datetime
from enum import Enum
from typing import Optional

class CompanyType(str, Enum):
    BANK = "Bank"
    CREDIT_UNION = "Credit Union"
    FINTECH = "Fintech"
    INSURANCE = "Insurance"
    INVESTMENT_FIRM = "Investment Firm"
    OTHER = "Other"

class ChatAdminCreate(BaseModel):
    admin_first_name: str = Field(..., min_length=1, max_length=50)
    admin_last_name: str = Field(..., min_length=1, max_length=50)
    admin_email: EmailStr
    admin_password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str
    company_name: str = Field(..., min_length=1, max_length=100)
    company_type: CompanyType

class ChatAdminInDB(BaseModel):
    id: int
    admin_first_name: str
    admin_last_name: str
    admin_email: EmailStr
    company_name: str
    company_type: CompanyType
    created_at: datetime
    assistant_email: Optional[str] = None
    assistant_email_created_at: Optional[datetime] = None
    is_assistant_email_generated: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class ChatAdminLoginResponse(BaseModel):
    access_token: str
    token_type: str
    admin: ChatAdminInDB