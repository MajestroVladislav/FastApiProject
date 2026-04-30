from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime
from typing import Optional
from fastapi import UploadFile

class UserBase(BaseModel):
    name: str
    id: int

class UserCreate(BaseModel):
    password: str
    name: str

    @field_validator('name')
    def validate_name(cls, name):
        if not name.isalpha():
            raise ValueError("Name must contain only letters")
        return name

    @field_validator('password')
    def validate_password(cls, password):
        if len(password) < 8:
            raise ValueError("Password is too short, please include 8 or more symbols")
        return password

class UserRead(BaseModel):
    id: int

class UserLogin(BaseModel):
    username: str = Field(..., alias="username")
    password: str

# Модель токена, в которой возвращается JWT
class Token(BaseModel):
    access_token: str = Field(..., description="JWT токен доступа")
    token_type: str = "bearer"

class CategoryBase(BaseModel):
    title: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryRead(CategoryBase):
    id: int

    class Config:
        from_attributes = True


class LocationBase(BaseModel):
    name: str

class LocationCreate(LocationBase):
    pass

class LocationRead(LocationBase):
    id: int

    class Config:
        from_attributes = True

class PostBase(BaseModel):
    title: str
    text: str
    pub_date: Optional[datetime]
    image: Optional[str] = Field(None, description="URL изображение у поста")
    

class PostCreate(PostBase):
    author_id: int
    location_id: int
    category_id: int


class PostRead(PostBase):
    id: int
    author: UserRead
    location: LocationBase
    category: CategoryBase
    
    model_config = ConfigDict(from_attributes=True)


class CommentBase(BaseModel):
    text: str
    created_at: Optional[datetime]


class CommentRead(CommentBase):
    id: int
    author: UserRead
    post_id: int