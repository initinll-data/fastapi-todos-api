import uvicorn
from fastapi import FastAPI

from ToDoApp import models
from ToDoApp.database import engine
from ToDoApp.routers import admin, auth, todos, users

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)


@app.get("/")
async def root():
    return {"message": "Welcome To My Api!"}
