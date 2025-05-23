from src.backend.database import DatabaseService, db


def get_db() -> DatabaseService:
    return db
