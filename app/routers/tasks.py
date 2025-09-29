from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List
from app.database import get_db
from app.models import Task as TaskModel, Event as EventModel, User
from app.schemas import TaskResponse, TaskCreate, TaskUpdate 
from app.deps import get_current_user

router = APIRouter(prefix="/tasks", tags=["Task Management (Bonus)"])

# --- Task Ownership Helper ---
def check_task_ownership(db: Session, task_id: int, current_user: User):
    # Retrieve the task and join to the event
    task = db.query(TaskModel).join(EventModel).filter(TaskModel.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Crucial Logic: Check ownership via the joined Event object
    if task.event.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to manage this task.")
    return task

# --- CREATE Task (Checks Event Ownership) ---
@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_in: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Before creation, ensure the user owns the event the task is tied to
    event = db.get(EventModel, task_in.event_id)
    if not event or event.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot create task for an event you don't own.")
    
    new_task = TaskModel(**task_in.model_dump())
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

# --- LIST Tasks (Only for events owned by the user) ---
@router.get("/", response_model=List[TaskResponse])
def list_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Query: Select tasks where the linked event's owner_id matches the current user's ID
    tasks = (
        db.query(TaskModel)
        .join(EventModel)
        .filter(EventModel.owner_id == current_user.id)
        .all()
    )
    return tasks

# --- UPDATE Task (Checks Task Ownership) ---
@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_in: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = check_task_ownership(db, task_id, current_user)
    
    for key, value in task_in.model_dump(exclude_unset=True).items():
        setattr(task, key, value)
    
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

# --- DELETE Task (Checks Task Ownership) ---
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = check_task_ownership(db, task_id, current_user)
    
    db.delete(task)
    db.commit()
    return