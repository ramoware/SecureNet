import sqlite3
import logging
from contextlib import contextmanager

class DatabaseManager:
    """Manage SQLite database connections for RBAC system."""
    
    def __init__(self, db_path="securenet.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            yield conn
        except sqlite3.Error as e:
            self.logger.error(f"Database connection error: {str(e)}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
