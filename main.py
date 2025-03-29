from fastapi import FastAPI
from routers import user
from routers import activity
from routers import workout_plan
from routers import workout

app = FastAPI()


app.include_router(user.router)
app.include_router(activity.router)
app.include_router(workout.router)
app.include_router(workout_plan.router)


@app.get("/healthcheck")
async def root():
    return {"message": "Ok!"}
