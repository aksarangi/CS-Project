# backend/models/category_model.py

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class CategoryModel:
    category_id: Optional[int] = None
    name: str = ""
    description: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self):
        """
        Returns a JSON-serializable dictionary of the Category.
        """
        return {
            "category_id": self.category_id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }

    @classmethod
    def from_db_row(cls, row: dict):
        """
        Creates a CategoryModel instance from a database row.
        """
        return cls(
            category_id=row.get("category_id"),
            name=row.get("name", ""),
            description=row.get("description"),
            created_at=row.get("created_at") if isinstance(row.get("created_at"), datetime) else datetime.now()
        )
