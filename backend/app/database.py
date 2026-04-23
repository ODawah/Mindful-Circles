from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

def build_database_url() -> str:
    if settings.TURSO_DATABASE_URL:
        turso_url = settings.TURSO_DATABASE_URL.strip()
        if turso_url.startswith("sqlite+"):
            return turso_url
        if turso_url.startswith("libsql://"):
            separator = "&" if "?" in turso_url else "?"
            return f"sqlite+{turso_url}{separator}secure=true"
        raise ValueError("TURSO_DATABASE_URL must start with libsql://")

    if settings.DATABASE_URL:
        return settings.DATABASE_URL

    raise ValueError("Set either TURSO_DATABASE_URL or DATABASE_URL")


def build_connect_args() -> dict:
    if settings.TURSO_DATABASE_URL:
        if not settings.TURSO_AUTH_TOKEN:
            raise ValueError("TURSO_AUTH_TOKEN is required when TURSO_DATABASE_URL is set")
        return {"auth_token": settings.TURSO_AUTH_TOKEN}
    return {}


engine = create_engine(build_database_url(), connect_args=build_connect_args())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
