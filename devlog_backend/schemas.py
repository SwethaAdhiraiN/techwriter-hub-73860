from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    username: str = Field(..., description="Unique username")
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserRead(UserBase):
    id: int
    bio: str = ""
    avatar_url: str = ""
    created_at: datetime

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Post schemas
class PostBase(BaseModel):
    title: str
    content: str
    tags: Optional[str] = ""

class PostCreate(PostBase):
    pass

class PostRead(PostBase):
    id: int
    slug: str
    author_id: int
    published: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Comment schemas
class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    pass

class CommentRead(CommentBase):
    id: int
    post_id: int
    author_id: int
    created_at: datetime

    class Config:
        orm_mode = True

# Reaction schemas
class ReactionBase(BaseModel):
    type: str = Field(..., description="Type of reaction")

class ReactionCreate(ReactionBase):
    pass

class ReactionRead(ReactionBase):
    id: int
    user_id: int
    post_id: int
    created_at: datetime

    class Config:
        orm_mode = True

# Profile
class ProfileUpdate(BaseModel):
    bio: Optional[str]
    avatar_url: Optional[str]

# Search
class SearchQuery(BaseModel):
    query: str
    tags: Optional[str]
    author: Optional[str]
