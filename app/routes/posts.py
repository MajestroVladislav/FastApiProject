import os
from fastapi import APIRouter, HTTPException, Depends, status, File, Form, UploadFile
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from starlette.responses import FileResponse
from typing import Optional
from datetime import datetime

from app.models import Post, User, Category, Location  # Импортируем ORM-модели
from app.schemas import PostCreate, PostRead, UserCreate, UserRead, CategoryRead, CategoryCreate, LocationRead, LocationCreate  # Импортируем Pydantic-схемы
from app.database import get_db  # Импортируем зависимость для БД
from app.routes.auth import get_current_user, get_password_hash
from exeptions import Domain as domain, Infrastructure as database

router = APIRouter()

IMAGE_DIR = "images"
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

IMAGE_URL_PREFIX = "/static/images"

async def save_image(file: UploadFile, post_id: int):
    if not file:
        return None

    filename = f"{post_id}_{file.filename}"
    filepath = os.path.join(IMAGE_DIR, filename)

    try:
        with open(filepath, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        return f"{IMAGE_URL_PREFIX}/{filename}"
    except Exception as e:
        print(f"Ошибка при сохранении изображения!")


def delete_image(image_url: Optional[str]):
    if not image_url:
        return

    filename = image_url.split(IMAGE_URL_PREFIX + "/")[-1]
    filepath = os.path.join(IMAGE_DIR, filename)

    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except Exception as e:
            print(f"Ошибка при удалении изображения!")


# Эндпоинт для создания поста (защищен авторизацией)
@router.post("/", response_model=PostRead, status_code=status.HTTP_201_CREATED)
async def create_post(title: str = Form(...),
                      text: str = Form(...),
                      pub_date: Optional[datetime] = Form(None),
                      author_id: int = Form(...),
                      location_id: int = Form(...),
                      category_id: int = Form(...),
                      image: Optional[UploadFile] = File(None),
                      db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        # Проверяем, что автор поста совпадает с текущим авторизованным пользователем
        if author_id != current_user.id:
            raise domain.WrongUserError()  # Исключение 0: попытка создать пост от имени иного пользователя

        # Проверяем существование автора, категории и локации
        db_author = db.query(User).filter(User.id == author_id).first()
        if not db_author:
            raise domain.UserNotFoundError(user_id=author_id)  # Исключение 1: пользователь не найден

        db_category = db.query(Category).filter(Category.id == category_id).first()
        if not db_category:
            raise domain.CategoryNotFoundError(category_id=category_id)  # Исключение 2: категория не найдена

        db_location = db.query(Location).filter(Location.id == location_id).first()
        if not db_location:
            raise domain.LocationNotFoundError(location_id=location_id)  # Исключение 3: локация не найдена

        db_post = Post(
            title=title,
            text=text,
            pub_date=pub_date,
            author_id=author_id,
            category_id=category_id,
            location_id=location_id,
            image=None
        )  # Создаем объект из Pydantic-схемы
        db.add(db_post)
        db.commit()
        db.refresh(db_post)  # Обновляем объект, чтобы получить ID и другие сгенерированные поля

        if image:
            image_url = await save_image(image, db_post.id)
            if image_url:
                db_post.image = image_url
        db.commit()
        db.refresh(db_post)
        return db_post
    except domain.WrongUserError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e)+": Вы не можете создавать посты от имени другого пользователя.")
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
        if 'db_post' in locals() and db_post.id:
            db.rollback()
            delete_image(db_post.image)
            db.delete(db_post)
            db.commit()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Internal server error: {str(e)}")  # Ловим какую-либо ошибку

# Эндпоинт для получения всех постов (публичный)
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

# Эндпоинт для получения одного поста по ID (публичный)
@router.get("/{post_id}", response_model=PostRead)
async def get_post(post_id: int, db: Session = Depends(get_db)):
    try:
        post = db.query(Post).filter(Post.id == post_id).first()
        if post is None:
            raise domain.PostNotFoundError(post_id)  # Исключение 1: пост не найден
        return post
    except domain.PostNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))  # Ловим исключение 1
    except database.DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")  # Ловим какую-либо ошибку базы данных
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Internal server error: {str(e)}")  # Ловим какую-либо ошибку

# Эндпоинт для обновления поста (защищен авторизацией)
@router.put("/{post_id}", response_model=PostRead)
async def update_post(
    post_id: int,
    title: Optional[str] = Form(None),
    text: Optional[str] = Form(None),
    pub_date: Optional[datetime] = Form(None),
    image: Optional[UploadFile] = File(None),
    delete_image_flag: bool = Form(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        db_post = db.query(Post).filter(Post.id == post_id).first()
        if db_post is None:
            raise domain.PostNotFoundError(post_id)

        if db_post.author_id != current_user.id:
            raise domain.WrongUserError()

        if title is not None:
            db_post.title = title
        if text is not None:
            db_post.text = text
        if pub_date is not None:
            db_post.pub_date = pub_date

        if delete_image_flag:
            delete_image(db_post.image)
            db_post.image = None
        elif image is not None and image.filename:
            old_image_url = db_post.image
            new_image_url = await save_image(image, post_id)
            if new_image_url:
                db_post.image = new_image_url
                if old_image_url:
                    delete_image(old_image_url)

        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        return db_post

    except domain.PostNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except domain.WrongUserError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e) + ": Вы не можете редактировать чужой пост.",
        )
    except database.DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )
    except Exception as e:
        db.rollback()
        if delete_image_flag and 'new_image_url' in locals() and new_image_url:
            delete_image(new_image_url)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )

# Эндпоинт для удаления поста
@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        db_post = db.query(Post).filter(Post.id == post_id).first()
        if db_post is None:
            raise domain.PostNotFoundError(post_id)  # Исключение 1: пост не найден
        # Проверяем, что текущий пользователь является автором поста
        if db_post.author_id != current_user.id:
            raise domain.WrongUserError()  # Исключение 2: пользователь не является автором поста

        if db_post.image:
            delete_image(db_post.image)
        db.delete(db_post)
        db.commit()
        return {"message": "Post deleted successfully"}
    except domain.PostNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))  # Ловим исключение 1
    except domain.WrongUserError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e)+": Вы не можете удалять чужой пост.")  # Ловим исключение 2
    except database.DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")  # Ловим какую-либо ошибку базы данных
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Internal server error: {str(e)}")  # Ловим какую-либо ошибку


@router.post("/users/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        hashed_password = get_password_hash(user.password)

        # Создаем словарь для модели User, используя хешированный пароль
        user_data_for_db = user.dict()
        user_data_for_db['password'] = hashed_password

        db_user = User(**user_data_for_db)  # Используем словарь с хешированным паролем

        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Integrity error: {str(e)}")
    except database.DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Internal server error: {str(e)}")


@router.post("/categories/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(category: CategoryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
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
def create_location(location: LocationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
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