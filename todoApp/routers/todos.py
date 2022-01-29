import sys
sys.path.append('..')

from fastapi import Depends, HTTPException, APIRouter
from todoApp.schemas import Todo
from .. import models
from ..database import SessionLocal, engine
from sqlalchemy.orm import Session
from .auth import get_current_user, get_user_exception

router = APIRouter(
    prefix="/todos",
    tags=["todos"],
    responses={404: {"description": "Not Found"}}
)

models.Base.metadata.create_all(bind=engine)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@router.get('/')
async def read_all(db: Session = Depends(get_db)):
    data =  db.query(models.Todos).all()
    return {
        "data" : data
    }

@router.get('/{todo_id}')
async def read_todo(todo_id: int,
                    user: dict = Depends(get_current_user),
                    db: Session = Depends(get_db)):

    if user is None:
        raise get_user_exception()           

    todo_model =  db.query(models.Todos)\
                    .filter(models.Todos.id == todo_id)\
                    .filter(models.Todos.owner_id == user.get('id'))\
                    .first()

    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found")

@router.get('/user')
async def read_all_by_user(user: dict = Depends(get_current_user),
                           db: Session = Depends(get_db)):
    print("todo/user Request")
    if user is None:
        raise get_user_exception()
    
    todo_model =  db.query(models.Todos)\
                            .filter(models.Todos.owner_id == user.get('id'))\
                            .all()

    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found")

@router.post('/')
async def create_todo(todo: Todo,
                      user: dict = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    
    if user is None:
        raise get_user_exception()

    todo_model = models.Todos()
    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.complete = todo.complete
    todo_model.priority = todo.priority
    todo_model.owner_id = user.get('id')

    db.add(todo_model)
    db.commit()

    return {
        'status': 201,
        'transaction': 'Succesfull'
    }

@router.put('/{todo_id}')
async def update_todo(todo_id: int,todo: Todo,
                     user: dict = Depends(get_current_user),
                     db: Session = Depends(get_db)):
    
    if user is None:
        raise get_user_exception()

    todo_model = db.query(models.Todos)\
    .filter(models.Todos.id == todo_id)\
    .filter(models.Todos.owner_id == user.get('id'))\
    .first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.complete = todo.complete
    todo_model.priority = todo.priority

    db.add(todo_model)
    db.commit()

    return {
        'status': 200,
        'transaction': 'Succesfull'
    }

@router.delete('/{todo_id}')
async def delete_todo(todo_id: int,
                      user: dict = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    
    if user is None:
        raise get_user_exception()

    todo_model =  db.query(models.Todos)\
                    .filter(models.Todos.id == todo_id)\
                    .filter(models.Todos.owner_id == user.get('id'))\
                    .first()
                    
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    db.query(models.Todos).filter(models.Todos.id == todo_id).delete()
    db.commit()

    return {
        'status': 200,
        'transaction': 'Succesfull'
    }

