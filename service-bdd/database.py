from contextlib import contextmanager

import psycopg2
from config import settings
from psycopg2.extras import RealDictCursor


def get_connection():
    """Create a new database connection."""
    return psycopg2.connect(
        host=settings.database_host,
        port=settings.database_port,
        database=settings.database_name,
        user=settings.database_user,
        password=settings.database_password,
    )


@contextmanager
def get_db_cursor():
    """Context manager for database operations."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def init_db():
    """Initialize database schema."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        with open("scripts/schema.sql", "r") as f:
            cursor.execute(f.read())
        conn.commit()
        cursor.close()
    finally:
        conn.close()
