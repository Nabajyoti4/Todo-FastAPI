from fastapi import FastAPI
from . import models
from .database import engine
from .routers import auth, todos

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router, tags=["auth"])
app.include_router(todos.router, tags=["todos"])
