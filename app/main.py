from fastapi import FastAPI
from app.database import create_db_and_tables 
from app.routers import auth, events, tasks # All routers imported

app = FastAPI(
    title="Event Management API",
    version="1.0.0",
    description="A backend solution demonstrating FastAPI, Auth, and RBAC.",
    on_startup=[create_db_and_tables] 
)

# Include all API Routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(events.router, prefix="/api/v1")
app.include_router(tasks.router, prefix="/api/v1")