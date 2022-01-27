from fastapi import FastAPI, Depends, HTTPException

from todoApp.schemas import Todo
from . import models
from .database import SessionLocal, engine
from sqlalchemy.orm import Session

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@app.get('/')
async def read_all(db: Session = Depends(get_db)):
    data =  db.query(models.Todos).all()
    return {
        "data" : data
    }

@app.get('/todo/{todo_id}')
async def read_todo(todo_id: int, db: Session = Depends(get_db)):
    todo_model =  db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found")

@app.post('/')
async def create_todo(todo: Todo, db: Session = Depends(get_db)):
    todo_model = models.Todos()
    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.complete = todo.complete
    todo_model.priority = todo.priority

    db.add(todo_model)
    db.commit()

    return {
        'status': 201,
        'transaction': 'Succesfull'
    }


@app.put('/{todo_id}')
async def update_todo(todo_id: int,todo: Todo, db: Session = Depends(get_db)):
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).first()

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

@app.delete('/{todo_id}')
async def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo_model =  db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    db.query(models.Todos).filter(models.Todos.id == todo_id).delete()
    db.commit()

    return {
        'status': 200,
        'transaction': 'Succesfull'
    }

