from pydantic import BaseModel
from pydantic import SecretStr
from datetime import datetime


class User(BaseModel):
    id: int
    name: str
    password: SecretStr


class Base(BaseModel):
    is_published: bool
    created_at: datetime


class Category(Base):
    title: str
    description: str


class Location(Base):
    name: str


class Post(Base):
    title: str
    text: str
    pub_date: datetime
    image: None
    author: User
    location: Location
    category: Category


class Comment(BaseModel):
    text: str
    post: Post
    created_at: datetime
    author: User