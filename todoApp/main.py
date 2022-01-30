from fastapi import FastAPI
import models
from database import engine
from routers import auth, todos
import uvicorn
from config import settings

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router, tags=["auth"])
app.include_router(todos.router, tags=["todos"])

if __name__ == "__main__":
    uvicorn.run(app, host=settings.host, port=settings.port)
