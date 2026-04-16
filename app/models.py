from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, declarative_base
from passlib.context import CryptContext

Base = declarative_base()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

    posts = relationship("Post", back_populates="author")
    comments = relationship("Comment", back_populates="author")

    def verify_password(self, plain_password: str) -> bool:
        return pwd_context.verify(plain_password, self.password)

class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)

    posts = relationship("Post", back_populates="category")

class Location(Base):
    __tablename__ = 'locations'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    posts = relationship("Post", back_populates="location")

class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    pub_date = Column(DateTime, nullable=True)
    image = Column(String, nullable=True)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    location_id = Column(Integer, ForeignKey('locations.id'), nullable=True)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)

    author = relationship("User", back_populates="posts")
    location = relationship("Location", back_populates="posts")
    category = relationship("Category", back_populates="posts")
    comments = relationship("Comment", back_populates="post")

class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=True)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=True)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    post = relationship('Post', back_populates='comments')
    author = relationship('User', back_populates='comments')
