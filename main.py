from fastapi import FastAPI
from routers import user
from routers import activity

app = FastAPI()


app.include_router(activity.router)
# app.include_router(ac.router)
app.include_router(user.router)



@app.get("/")
async def root():
    return {"message": "Hello World!"}