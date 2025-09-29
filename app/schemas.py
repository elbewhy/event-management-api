from sqlmodel import SQLModel
from typing import Optional, List
from datetime import date
from app.models import EventBase, TaskBase, UserBase 

# --- Task Schemas ---
class TaskCreate(TaskBase):
    event_id: int # Required on creation
    pass

class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_done: Optional[bool] = None

class TaskResponse(TaskBase):
    id: int
    event_id: int

# --- Event Schemas ---
class EventCreate(EventBase):
    pass

class EventUpdate(EventBase):
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[date] = None
    location: Optional[str] = None

class EventResponse(EventBase):
    id: int
    owner_id: int
    tasks: List[TaskResponse] = [] # Include tasks for full response

# --- User/Auth Schemas ---
class UserCreate(UserBase):
    password: str

class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"