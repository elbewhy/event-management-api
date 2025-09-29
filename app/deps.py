from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database import get_db, engine # get_db is needed by functions below
from app.models import User
from app.config import settings

# This tokenUrl must match the actual login route
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login") 

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Validates the JWT and fetches the corresponding User object."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Note: Using settings.SECRET_KEY and settings.ALGORITHM from config.py
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub") # The user ID is stored in the 'sub' claim
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Fetch User using SQLModel/SQLAlchemy
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise credentials_exception
    return user

def get_admin_user(current_user: User = Depends(get_current_user)):
    """Enforces the Admin role check (RBAC)."""
    if current_user.role != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user