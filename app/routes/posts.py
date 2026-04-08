from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models import Post, User, Category, Location  # Импортируем ORM-модели
from app.schemas import PostCreate, PostRead, UserCreate, UserRead, CategoryRead, CategoryCreate, LocationRead, LocationCreate  # Импортируем Pydantic-схемы
from app.database import get_db  # Импортируем зависимость для БД
from exeptions import Domain as domain, Infrastructure as database

router = APIRouter()

# Эндпоинт для создания поста
@router.post("/", response_model=PostRead, status_code=status.HTTP_201_CREATED)
async def create_post(post: PostCreate, db: Session = Depends(get_db)):
    try:
        # Проверяем существование автора, категории и локации
        db_author = db.query(User).filter(User.id == post.author_id).first()
        if not db_author:
            raise domain.UserNotFoundError(user_id=post.author_id)  # Исключение 1: пользователь не найден

        db_category = db.query(Category).filter(Category.id == post.category_id).first()
        if not db_category:
            raise domain.CategoryNotFoundError(category_id=post.category_id)  # Исключение 2: категория не найдена

        db_location = db.query(Location).filter(Location.id == post.location_id).first()
        if not db_location:
            raise domain.LocationNotFoundError(location_id=post.location_id)  # Исключение 3: локация не найдена

        db_post = Post(**post.dict())  # Создаем объект из Pydantic-схемы
        db.add(db_post)
        db.commit()
        db.refresh(db_post)  # Обновляем объект, чтобы получить ID и другие сгенерированные поля
        return db_post
    except domain.UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))  # Ловим исключение 1
    except domain.CategoryNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))  # Ловим исключение 2
    except domain.LocationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))  # Ловим исключение 3
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Integrity error: {str(e)}")  # Ловим непредусмотренное исключение, вдруг что-то не так введено
    except database.DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")  # Ловим какую-либо ошибку базы данных
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Internal server error: {str(e)}")  # Ловим какую-либо ошибку

# Эндпоинт для получения всех постов
@router.get("/", response_model=List[PostRead])
async def get_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        posts = db.query(Post).offset(skip).limit(limit).all()
        return posts
    except database.DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")  # Ловим непредусмотренное исключение, вдруг что-то не так
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Internal server error: {str(e)}")  # Ловим какую-либо ошибку

# Эндпоинт для получения одного поста по ID
@router.get("/{post_id}", response_model=PostRead)
async def get_post(post_id: int, db: Session = Depends(get_db)):
    try:
        post = db.query(Post).filter(Post.id == post_id).first()
        if post is None:
            raise HTTPException(status_code=404, detail="Post not found")  # Исключение 1: пост не найден
        return post
    except HTTPException:
        raise HTTPException(status_code=404, detail="Post not found")  # Ловим исключение 1
    except database.DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")  # Ловим какую-либо ошибку базы данных
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Internal server error: {str(e)}")  # Ловим какую-либо ошибку

# Эндпоинт для обновления поста
@router.put("/{post_id}", response_model=PostRead)
async def update_post(post_id: int, updated_post_data: PostCreate, db: Session = Depends(get_db)):
    try:
        db_post = db.query(Post).filter(Post.id == post_id).first()
        if db_post is None:
            raise HTTPException(status_code=404, detail="Post not found")  # Исключение 1: пост не найден

        # Обновляем поля поста
        for key, value in updated_post_data.dict(exclude_unset=True).items():
            setattr(db_post, key, value)

        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        return db_post
    except HTTPException:
        raise HTTPException(status_code=404, detail="Post not found")  # Ловим исключение 1
    except database.DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")  # Ловим какую-либо ошибку базы данных
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Internal server error: {str(e)}")  # Ловим какую-либо ошибку

# Эндпоинт для удаления поста
@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db: Session = Depends(get_db)):
    try:
        db_post = db.query(Post).filter(Post.id == post_id).first()
        if db_post is None:
            raise HTTPException(status_code=404, detail="Post not found")  # Исключение 1: пост не найден

        db.delete(db_post)
        db.commit()
        return {"message": "Post deleted successfully"}

    except database.DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")  # Ловим какую-либо ошибку базы данных
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Internal server error: {str(e)}")  # Ловим какую-либо ошибку


@router.post("/users/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = User(**user.dict())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Integrity error: {str(e)}")  # Ловим непредусмотренное исключение, вдруг что-то не так введено
    except database.DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")  # Ловим какую-либо ошибку базы данных
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Internal server error: {str(e)}")  # Ловим какую-либо ошибку


@router.post("/categories/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    try:
        db_category = Category(**category.dict())
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Integrity error: {str(e)}")  # Ловим непредусмотренное исключение, вдруг что-то не так введено
    except database.DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")  # Ловим какую-либо ошибку базы данных
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Internal server error: {str(e)}")  # Ловим какую-либо ошибку


@router.post("/locations/", response_model=LocationRead, status_code=status.HTTP_201_CREATED)
def create_location(location: LocationCreate, db: Session = Depends(get_db)):
    try:
        db_location = Location(**location.dict())
        db.add(db_location)
        db.commit()
        db.refresh(db_location)
        return db_location
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Integrity error: {str(e)}")  # Ловим непредусмотренное исключение, вдруг что-то не так введено
    except database.DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")  # Ловим какую-либо ошибку базы данных
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Internal server error: {str(e)}")  # Ловим какую-либо ошибку