from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional

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
    def validate_name(cls, password):
        if len(password) < 8:
            raise ValueError("Password is too short, please include 8 or more symbols")
        return password

class UserRead(BaseModel):
    id: int

class CategoryBase(BaseModel):
    title: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryRead(CategoryBase):
    id: int

    class Config:
        orm_mode = True


class LocationBase(BaseModel):
    name: str

class LocationCreate(LocationBase):
    pass

class LocationRead(LocationBase):
    id: int

    class Config:
        orm_mode = True

class PostBase(BaseModel):
    title: str
    text: str
    pub_date: Optional[datetime]
    image: Optional[str]


class PostCreate(PostBase):
    author_id: int
    location_id: int
    category_id: int


class PostRead(PostBase):
    id: int
    author: UserRead
    location: LocationBase
    category: CategoryBase


class CommentBase(BaseModel):
    text: str
    created_at: Optional[datetime]


class CommentRead(CommentBase):
    id: int
    author: UserRead
    post_id: int