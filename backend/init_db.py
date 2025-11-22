from sqlmodel import SQLModel, create_engine
from app.core.config import settings


def init_db():
    print(f"Initializing database at {settings.DATABASE_URL}")
    engine = create_engine(settings.DATABASE_URL)
    SQLModel.metadata.create_all(engine)
    print("Database initialized successfully.")


if __name__ == "__main__":
    init_db()
