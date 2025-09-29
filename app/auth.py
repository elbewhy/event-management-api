from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt

from app.models import User 
from app.schemas import UserCreate, Token 
from app.deps import get_db
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Auth & Users"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

@router.post("/signup", response_model=Token)
def signup_user(user_in: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.scalar(select(User).where(User.email == user_in.email))
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = pwd_context.hash(user_in.password)
    # Professional Logic: Automatically make the first registered user an Admin
    user_role = "Admin" if not db.scalar(select(User)) else "User"

    db_user = User(
        email=user_in.email, 
        hashed_password=hashed_password, 
        role=user_role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    access_token = create_access_token(data={"sub": db_user.id, "role": db_user.role})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login_for_access_token(user_in: UserCreate, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == user_in.email))
    
    if not user or not pwd_context.verify(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.id, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}