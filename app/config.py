from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str = "your-very-strong-secret-key-change-this" 
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
settings = Settings()