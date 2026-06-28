from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    GROQ_API_KEY: str
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    GROQ_MODEL: str = "llama3-8b-8192"
    APP_ENV: str = "development"

    class Config:
        env_file = ".env"


settings = Settings()
