from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174", "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

