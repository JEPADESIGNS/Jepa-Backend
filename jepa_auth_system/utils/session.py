"""
Global session context for tracking current user, project, and preferences.

Provides a singleton session object accessible throughout the application.
All views and services can access session.current_user_id, session.current_project_id, etc.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class UserSession:
    """Thread-safe session container for tracking user context."""
    
    current_user_id: Optional[int] = None
    current_username: Optional[str] = None
    current_role: Optional[str] = None
    current_project_id: Optional[int] = None
    current_project_name: Optional[str] = None
    theme: str = "dark"
    last_action: Optional[str] = None
    
    def set_user(self, user_id: int, username: str, role: str) -> None:
        """Set current user and role after login."""
        self.current_user_id = user_id
        self.current_username = username
        self.current_role = role
        self.last_action = f"Logged in as {username}"
    
    def set_project(self, project_id: int, project_name: str) -> None:
        """Set current project context."""
        self.current_project_id = project_id
        self.current_project_name = project_name
        self.last_action = f"Switched to project: {project_name}"
    
    def clear(self) -> None:
        """Clear all session data (logout)."""
        self.current_user_id = None
        self.current_username = None
        self.current_role = None
        self.current_project_id = None
        self.current_project_name = None
        self.last_action = "Logged out"
    
    def is_authenticated(self) -> bool:
        """Return True if user is logged in."""
        return self.current_user_id is not None
    
    def has_project_context(self) -> bool:
        """Return True if a project is selected."""
        return self.current_project_id is not None
    
    def __repr__(self) -> str:
        return (
            f"<UserSession user_id={self.current_user_id} "
            f"username={self.current_username} "
            f"project_id={self.current_project_id} "
            f"role={self.current_role}>"
        )


# Global singleton session object
session: UserSession = UserSession()
