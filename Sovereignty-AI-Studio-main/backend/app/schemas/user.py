from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
import re


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(
        ...,
        min_length=3,
        max_length=20,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="Username must be 3-20 characters and contain only letters, numbers, hyphens, and underscores"
    )
    full_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = Field(None, max_length=500)
    
    @field_validator('bio')
    @classmethod
    def sanitize_bio(cls, v: Optional[str]) -> Optional[str]:
        """Sanitize bio field to prevent XSS attacks."""
        if v is None:
            return v
        # Remove potentially dangerous characters while preserving readability
        # In production, use a proper HTML sanitizer like bleach
        dangerous_chars = ['<', '>', '"', "'", '&']
        for char in dangerous_chars:
            v = v.replace(char, '')
        return v.strip()
    
    @field_validator('avatar_url')
    @classmethod
    def validate_avatar_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate avatar URL format."""
        if v is None:
            return v
        # Basic URL validation
        if not v.startswith(('http://', 'https://')):
            raise ValueError('Avatar URL must start with http:// or https://')
        # Prevent javascript: and data: URLs
        if v.lower().startswith(('javascript:', 'data:')):
            raise ValueError('Invalid avatar URL scheme')
        return v


class UserCreate(UserBase):
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password must be at least 8 characters long"
    )
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        Validate password meets security requirements:
        - At least 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character
        """
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        
        return v


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = Field(None, max_length=500)
    
    @field_validator('bio')
    @classmethod
    def sanitize_bio(cls, v: Optional[str]) -> Optional[str]:
        """Sanitize bio field to prevent XSS attacks."""
        if v is None:
            return v
        dangerous_chars = ['<', '>', '"', "'", '&']
        for char in dangerous_chars:
            v = v.replace(char, '')
        return v.strip()
    
    @field_validator('avatar_url')
    @classmethod
    def validate_avatar_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate avatar URL format."""
        if v is None:
            return v
        if not v.startswith(('http://', 'https://')):
            raise ValueError('Avatar URL must start with http:// or https://')
        if v.lower().startswith(('javascript:', 'data:')):
            raise ValueError('Invalid avatar URL scheme')
        return v


class UserInDB(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    subscription_plan: str
    subscription_expires_at: Optional[datetime]
    total_generations: int
    monthly_generations: int
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


class User(UserInDB):
    pass


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
