from typing import Union
from fastapi import FastAPI, Response, status, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from . import models, schemas
from .database import engine, get_db
import psycopg2
from psycopg2.extras import RealDictCursor

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.on_event("startup")
async def startup():
    while True:
        try:
            conn = psycopg2.connect(
                host='localhost', 
                database='fastapi',
                user='postgres',
                password='12345',
                cursor_factory=RealDictCursor
            )
            cursor = conn.cursor()
            print("Database successfully connected")
            break
        except Exception as error:
            print("Connection to database failed")
            print("Error", error)

my_post = [
    {"title": "title of the post 1", "content": "content of post 1", "id": 1},
    {"title": "title of the post 2", "content": "content of post 2", "id": 2}
]

def find_post(id):
    for p in my_post:
        if p["id"] == id:
            return p

def find_index_post(id):
    for i, p in enumerate(my_post):
        if p["id"] == id:
            return i

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/post")
def get_post(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts

@app.post("/createpost", status_code=status.HTTP_201_CREATED)
def get_createpost(post: schemas.Post, db: Session = Depends(get_db)):
    new_post = models.Post(**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@app.get("/post/{id}")
def get_post_by_id(id: int, db: Session = Depends(get_db)):
    post_id = db.query(models.Post).filter(models.Post.id == id)
    post = post_id.first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"id with {id} not found")
    return post

@app.delete("/post/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    post_delete = db.query(models.Post).filter(models.Post.id == id)
    post = post_delete.first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} not found")
    db.delete(post)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/post/{id}")
def update_post(id: int, updated_post: schemas.Post, db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} not found")
    post_query.update(updated_post.model_dump(), synchronize_session=False)
    db.commit()
    return post_query.first()

