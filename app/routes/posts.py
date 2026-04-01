from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from sqlalchemy.orm import Session

from app.models import Post, User, Category, Location  # Импортируем ORM-модели
from app.schemas import PostCreate, PostRead, UserCreate, UserRead, CategoryRead, CategoryCreate, LocationRead, LocationCreate  # Импортируем Pydantic-схемы
from app.database import get_db  # Импортируем зависимость для БД

router = APIRouter()

# Эндпоинт для создания поста
@router.post("/", response_model=PostRead, status_code=status.HTTP_201_CREATED)
async def create_post(post: PostCreate, db: Session = Depends(get_db)):
    # Проверяем существование автора, категории и локации
    db_author = db.query(User).filter(User.id == post.author_id).first()
    if not db_author:
        raise HTTPException(status_code=404, detail="Author not found")

    db_category = db.query(Category).filter(Category.id == post.category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")

    db_location = db.query(Location).filter(Location.id == post.location_id).first()
    if not db_location:
        raise HTTPException(status_code=404, detail="Location not found")

    db_post = Post(**post.dict())  # Создаем ORM-объект из Pydantic-схемы
    db.add(db_post)
    db.commit()
    db.refresh(db_post)  # Обновляем объект, чтобы получить ID и другие сгенерированные поля
    return db_post


# Эндпоинт для получения всех постов
@router.get("/", response_model=List[PostRead])
async def get_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    posts = db.query(Post).offset(skip).limit(limit).all()
    return posts


# Эндпоинт для получения одного поста по ID
@router.get("/{post_id}", response_model=PostRead)
async def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


# Эндпоинт для обновления поста
@router.put("/{post_id}", response_model=PostRead)
async def update_post(post_id: int, updated_post_data: PostCreate, db: Session = Depends(get_db)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    # Обновляем поля поста
    for key, value in updated_post_data.dict(exclude_unset=True).items():
        setattr(db_post, key, value)

    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


# Эндпоинт для удаления поста
@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db: Session = Depends(get_db)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    db.delete(db_post)
    db.commit()
    return {"message": "Post deleted successfully"}

@router.post("/users/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/categories/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    db_category = Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.post("/locations/", response_model=LocationRead, status_code=status.HTTP_201_CREATED)
def create_location(location: LocationCreate, db: Session = Depends(get_db)):
    db_location = Location(**location.dict())
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location