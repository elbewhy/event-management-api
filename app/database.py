from sqlmodel import create_engine, Session, SQLModel
# Importing models here is crucial to ensure SQLModel finds the table definitions on startup
from app.models import User, Event, Task 

# Configuration
sqlite_file_name = "events.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# Engine creation (connect_args is essential for SQLite multithread safety in Uvicorn)
engine = create_engine(sqlite_url, echo=False, connect_args={"check_same_thread": False})

# The function required by app/main.py to create tables on startup
def create_db_and_tables():
    """Initializes the database and creates tables based on SQLModel definitions."""
    SQLModel.metadata.create_all(engine)

# The Dependency to get the DB session
def get_db():
    """Provides a database session for a single request."""
    with Session(engine) as session:
        yield session