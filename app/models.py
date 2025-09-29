from typing import Optional, List
from datetime import date
from sqlmodel import SQLModel, Field, Relationship

# --- Task Model ---
class TaskBase(SQLModel):
    title: str
    description: Optional[str] = None
    is_done: bool = Field(default=False)
    
class Task(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: int = Field(foreign_key="event.id")
    # Define relationship back to Event
    event: "Event" = Relationship(back_populates="tasks") 

# --- Event Model ---
class EventBase(SQLModel):
    title: str
    description: str
    date: date
    location: str
    status: str = Field(default="Upcoming", max_length=15) 

class Event(EventBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="user.id")
    # Define relationships
    owner: "User" = Relationship(back_populates="events")
    tasks: List[Task] = Relationship(back_populates="event") 

# --- User Model ---
class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    role: str = Field(default="User", max_length=10) # Roles: "Admin" or "User"

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    # Define relationship to Events
    events: List["Event"] = Relationship(back_populates="owner")