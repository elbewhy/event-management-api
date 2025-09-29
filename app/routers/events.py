from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional
from datetime import date
from app.database import get_db
from app.models import Event as EventModel, User 
from app.schemas import EventResponse, EventCreate, EventUpdate 
from app.deps import get_current_user, get_admin_user

router = APIRouter(prefix="/events", tags=["Event Management"])

# --- Helper function for ownership check (required for PUT/DELETE) ---
def check_event_ownership(db: Session, event_id: int, current_user: User):
    event = db.get(EventModel, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Core Logic: User must be the owner to modify (PUT/DELETE)
    if event.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this event.")
    return event

# --- CREATE Event ---
@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(event: EventCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_event = EventModel(**event.model_dump(), owner_id=current_user.id)
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event

# --- LIST Events (Search, Filter, Pagination, RBAC) ---
@router.get("/", response_model=List[EventResponse])
def list_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    # Search & Filter Parameters
    search: Optional[str] = Query(None, description="Search by partial event title"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (e.g., Upcoming)"),
    start_date: Optional[date] = Query(None, description="Start date range (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date range (YYYY-MM-DD)"),
    # Pagination Parameters
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
):
    query = select(EventModel)
    
    # RBAC LOGIC: Admin sees all; User sees only their own
    if current_user.role != "Admin":
        query = query.where(EventModel.owner_id == current_user.id)

    # Filtering Logic
    if search:
        query = query.where(EventModel.title.ilike(f"%{search}%")) 
    if status_filter:
        query = query.where(EventModel.status == status_filter)
    if start_date and end_date:
        query = query.where(EventModel.date.between(start_date, end_date))

    # Pagination Logic
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)
    
    return db.scalars(query).all()

# --- UPDATE Event (Owner Capability) ---
@router.put("/{event_id}", response_model=EventResponse)
def update_event(
    event_id: int,
    event_in: EventUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    event = check_event_ownership(db, event_id, current_user)
    
    # Apply updates
    for key, value in event_in.model_dump(exclude_unset=True).items():
        setattr(event, key, value)
    
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

# --- DELETE Event (Owner Capability) ---
@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    event = check_event_ownership(db, event_id, current_user)
    
    db.delete(event)
    db.commit()
    return

# --- UPDATE Status (Admin Capability) ---
@router.patch("/{event_id}/status", response_model=EventResponse)
def update_event_status(
    event_id: int,
    new_status: str, 
    db: Session = Depends(get_db),
    # Crucial: Requires Admin role
    current_admin: User = Depends(get_admin_user)
):
    event = db.get(EventModel, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    event.status = new_status
    db.add(event)
    db.commit()
    db.refresh(event)
    return event