# backend/models/publisher_model.py

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class PublisherModel:
    publisher_id: Optional[int] = None
    name: str = ""
    location: Optional[str] = None
    contact_email: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self):
        """
        Returns a JSON-serializable dictionary of the Publisher.
        """
        return {
            "publisher_id": self.publisher_id,
            "name": self.name,
            "location": self.location,
            "contact_email": self.contact_email,
            "phone": self.phone,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }

    @classmethod
    def from_db_row(cls, row: dict):
        """
        Creates a PublisherModel instance from a database row.
        """
        return cls(
            publisher_id=row.get("publisher_id"),
            name=row.get("name", ""),
            location=row.get("location"),
            contact_email=row.get("contact_email"),
            phone=row.get("phone"),
            created_at=row.get("created_at") if isinstance(row.get("created_at"), datetime) else datetime.now()
        )
