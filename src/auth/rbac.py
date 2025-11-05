import sqlite3
import logging
from functools import wraps
from typing import List, Dict

class RBAC:
    """
    Role-Based Access Control System
    Implements NIST RBAC standard with user-role-permission model [citation:2][citation:10]
    """
    
    def __init__(self, db_path=":memory:"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self.init_database()
        self.load_default_roles()
    
    def init_database(self):
        """Initialize SQLite database with RBAC tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                role TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS roles (
                role TEXT PRIMARY KEY,
                permissions TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                user_id INTEGER,
                session_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                active INTEGER DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        self.logger.info("✅ RBAC database initialized")
    
    def load_default_roles(self):
        """Load default roles and permissions following least privilege principle [citation:7]."""
        default_roles = {
            "admin": "read,write,delete,manage_users,view_logs",
            "analyst": "read,write,view_logs", 
            "operator": "read,write",
            "viewer": "read",
            "guest": "read_limited"
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for role, permissions in default_roles.items():
            cursor.execute('''
                INSERT OR REPLACE INTO roles (role, permissions) 
                VALUES (?, ?)
            ''', (role, permissions))
        
        conn.commit()
        conn.close()
        self.logger.info("✅ Default roles loaded")
    
    def assign_role(self, username: str, role: str) -> bool:
        """Assign a role to a user."""
        if role not in ["admin", "analyst", "operator", "viewer", "guest"]:
            self.logger.error(f"Invalid role assignment: {role}")
            return False
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO users (username, role) 
                VALUES (?, ?)
            ''', (username, role))
            conn.commit()
            self.logger.info(f"✅ Role '{role}' assigned to user '{username}'")
            return True
        except sqlite3.Error as e:
            self.logger.error(f"Database error in assign_role: {str(e)}")
            return False
        finally:
            conn.close()
    
    def check_permission(self, username: str, required_permission: str) -> bool:
        """Check if user has the required permission."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT r.permissions 
                FROM users u 
                JOIN roles r ON u.role = r.role 
                WHERE u.username = ?
            ''', (username,))
            
            result = cursor.fetchone()
            if result:
                permissions = result[0].split(',')
                has_permission = required_permission in permissions
                self.logger.debug(f"Permission check for {username}: {required_permission} -> {has_permission}")
                return has_permission
            
            return False
        finally:
            conn.close()
    
    def create_session(self, username: str) -> int:
        """Create a new user session and return session ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        user_result = cursor.fetchone()
        
        if not user_result:
            raise ValueError(f"User {username} not found")
        
        user_id = user_result[0]
        cursor.execute('INSERT INTO sessions (user_id) VALUES (?)', (user_id,))
        session_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        self.logger.info(f"🆕 Session {session_id} created for user '{username}'")
        return session_id
    
    def get_user_permissions(self, username: str) -> List[str]:
        """Get all permissions for a specific user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT r.permissions 
            FROM users u 
            JOIN roles r ON u.role = r.role 
            WHERE u.username = ?
        ''', (username,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return result[0].split(',')
        return []
    
    def role_required(self, required_permission: str):
        """Decorator for protecting functions with RBAC checks."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Extract username from arguments (simplified)
                username = None
                if args and hasattr(args[0], 'username'):
                    username = args[0].username
                elif 'username' in kwargs:
                    username = kwargs['username']
                
                if not username:
                    raise PermissionError("Username required for access check")
                
                if not self.check_permission(username, required_permission):
                    raise PermissionError(
                        f"User '{username}' lacks required permission: {required_permission}"
                    )
                
                return func(*args, **kwargs)
            return wrapper
        return decorator

# Example usage class for protected operations
class SecureOperations:
    def __init__(self, rbac_system, username):
        self.rbac = rbac_system
        self.username = username
    
    @rbac_required('view_logs')
    def view_security_logs(self):
        """Example protected method - requires view_logs permission."""
        return f"Displaying security logs for {self.username}"
    
    @rbac_required('manage_users')
    def create_user(self, new_username):
        """Example protected method - requires manage_users permission."""
        return f"User {new_username} created by {self.username}"
