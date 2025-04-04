import uvicorn
from fastapi import FastAPI
from routers import auth
from routers import activity
from routers import workout_plan
from routers import workout


app = FastAPI()


app.include_router(auth.router)
app.include_router(activity.router)
app.include_router(workout.router)
app.include_router(workout_plan.router)


@app.get("/healthcheck")
async def root():
    return {"message": "Ok!"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
