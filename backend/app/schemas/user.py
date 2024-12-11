# app/schemas/user.py

from pydantic import BaseModel, EmailStr, constr, Field
from enum import Enum

class RoleCategory(str, Enum):
    DEBTOR = "Debtor"
    FI_ADMIN = "FI Admin"
    RESOHUB_ADMIN = "Resohub Admin"
    DELTABOTS_ADMIN = "Deltabots Admin"
    
class ThemeMode(str, Enum):
    LIGHT = 'light'
    DARK = 'dark'  
    
class ThemeUpdate(BaseModel):
    color: str
    mode: ThemeMode      

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    role_category: RoleCategory
    password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str
    color: str = 'zinc'
    mode: ThemeMode = ThemeMode.LIGHT

class Token(BaseModel):
    access_token: str
    token_type: str

class UserInDB(BaseModel):
    id: int
    name: str
    email: EmailStr
    role_category: RoleCategory
    color: str
    mode: ThemeMode

    class Config:
        from_attributes = True 
        
class UserLoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserInDB        