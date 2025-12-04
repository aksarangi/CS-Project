# backend/models/staff_model.py

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class StaffModel:
    staff_id: Optional[int] = None
    username: str = ""
    password_hash: str = ""  # Store hashed passwords
    full_name: Optional[str] = None
    role: str = "Clerk"  # Admin, Manager, Clerk
    email: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self):
        """
        Returns a JSON-serializable dictionary of the Staff member.
        """
        return {
            "staff_id": self.staff_id,
            "username": self.username,
            "full_name": self.full_name,
            "role": self.role,
            "email": self.email,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }

    @classmethod
    def from_db_row(cls, row: dict):
        """
        Creates a StaffModel instance from a database row.
        """
        return cls(
            staff_id=row.get("staff_id"),
            username=row.get("username", ""),
            password_hash=row.get("password_hash", ""),
            full_name=row.get("full_name"),
            role=row.get("role", "Clerk"),
            email=row.get("email"),
            created_at=row.get("created_at") if isinstance(row.get("created_at"), datetime) else datetime.now()
        )
