from fastapi import APIRouter, HTTPException
from typing import List
from app.models import Post

router = APIRouter()
posts = []

@router.get("/", response_model=List[Post])
async def get_posts():
    return posts

@router.post("/", response_model=Post)
async def create_post(post: Post):
    posts.append(post)
    return post

@router.put("/{post_id}", response_model=Post)
async def update_post(post_id: int, updated_post: Post):
    for i, post in enumerate(posts):
        if post_id == i:
            posts[i] = updated_post
            return updated_post
    raise HTTPException(status_code=404, detail="Post not found")

@router.delete("/{post_id}")
async def delete_post(post_id: int):
    for i, post in enumerate(posts):
        if post_id == i:
            posts.pop(i)
            return {"message": "Post deleted"}
    raise HTTPException(status_code=404, detail="Post not found")
