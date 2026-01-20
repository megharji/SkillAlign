from pydantic import BaseModel, EmailStr
from enum import Enum

# Notes-: 

# 1) EmailStr -: 
#    a) A specialized type provided by Pydantic to validate email addresses.
# 2) orm_mode = True -:
#    a) Allows Pydantic models to work seamlessly with ORM objects, enabling automatic data conversion.

class UserRole(str,Enum):
    HR="HR"
    Seeker="Seeker"

class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: UserRole

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    
    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str