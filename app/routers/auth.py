from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app import models, schemas
from app.database import get_db

# ---------------------------
# CONFIGURATION
# ---------------------------

SECRET_KEY = "lby_super_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# FIXED: Added leading slash to tokenUrl
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

router = APIRouter()

# ---------------------------
# UTILITY FUNCTIONS
# ---------------------------

def verify_password(plain_password, hashed_password):
    """Verify plain password against hashed password"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Hash password securely"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Create JWT token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_user(db: Session, username: str):
    """Fetch user by username"""
    return db.query(models.User).filter(models.User.username == username).first()

def authenticate_user(db: Session, username: str, password: str):
    """Check if user exists and password is correct"""
    user = get_user(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

# ---------------------------
# ROUTES
# ---------------------------

@router.post("/signup", response_model=schemas.Token)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user account
    """
    db_user = get_user(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = get_password_hash(user.password)
    new_user = models.User(username=user.username, hashed_password=hashed_password, role=user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token(data={"sub": new_user.username, "role": new_user.role})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    User login to get access token
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}


# ---------------------------
# PROTECTED ROUTES
# ---------------------------

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """
    Verify JWT token and return current user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user(db, username=username)
    if user is None:
        raise credentials_exception
    return user


@router.get("/me")
def read_users_me(current_user: models.User = Depends(get_current_user)):
    """
    Return current logged-in user details
    """
    return {
        "username": current_user.username,
        "role": current_user.role
    }
