from contextlib import asynccontextmanager

from fastapi import FastAPI

from modules.main_backend.api.routes import (
    agendas,
    availability_hours,
    business_service_hours,
    calendar,
    people,
    roles,
)
from modules.main_backend.database.connection import init_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_database()
    yield


app = FastAPI(
    title="Agendalo API",
    description="Calendar API for managing working hours and schedules",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(people.router)
app.include_router(roles.router)
app.include_router(availability_hours.router)
app.include_router(calendar.router)
app.include_router(business_service_hours.router)
app.include_router(agendas.router)


@app.get("/")
def root():
    return {"message": "Agendalo API"}

