# config.py
from pydantic import PostgresDsn, Field, ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # Database Configuration
    POSTGRES_USER: str = Field(..., alias="DB_USER")
    POSTGRES_PASSWORD: str = Field(..., alias="DB_PASSWORD")
    POSTGRES_HOST: str = Field("localhost", alias="DB_HOST")
    POSTGRES_PORT: int = Field(5432, alias="DB_PORT")
    POSTGRES_DB: str = Field(..., alias="DB_NAME")
    
    # JWT Configuration
    SECRET_KEY: str = Field(..., min_length=32)
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    
    # Environment Configuration
    ENV: str = Field(default="development")
    DEBUG: bool = Field(default=False)
    
    # CORS Configuration
    ALLOWED_ORIGINS: list[str] = Field(default=["*"])
    
    # Build database URL dynamically
    @property
    def DATABASE_URL(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    # Configuration for Pydantic settings
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Optional: Add validation for environment-specific settings
    @classmethod
    def validate(cls, values: ValidationInfo):
        if values.get("ENV") == "production":
            if values.get("DEBUG") is True:
                raise ValueError("Debug mode should be False in production")
        return values

# Create settings instance
settings = Settings()