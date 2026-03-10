from pydantic import BaseModel, SecretStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    name: str
    id: int

class UserCreate(BaseModel):
    password: str
    name: str

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