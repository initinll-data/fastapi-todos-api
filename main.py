import uvicorn
from fastapi import FastAPI

from ToDoApp.database import Base, engine
from ToDoApp.routers import admin, auth, todos, users

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/healthy")
async def health_check():
    return {"status": "Healthy"}

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
