# backend/models/author_model.py

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional

@dataclass
class AuthorModel:
    author_id: Optional[int] = None
    full_name: str = ""
    country: str = "India"
    birth_year: Optional[int] = None
    death_year: Optional[int] = None
    bio: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self):
        """
        Returns a JSON-serializable dictionary of the Author.
        """
        return {
            "author_id": self.author_id,
            "full_name": self.full_name,
            "country": self.country,
            "birth_year": self.birth_year,
            "death_year": self.death_year,
            "bio": self.bio,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }

    @classmethod
    def from_db_row(cls, row: dict):
        """
        Creates an AuthorModel instance from a database row.
        """
        return cls(
            author_id=row.get("author_id"),
            full_name=row.get("full_name", "Anonymous/Unknown"),
            country=row.get("country", "India"),
            birth_year=row.get("birth_year"),
            death_year=row.get("death_year"),
            bio=row.get("bio"),
            created_at=row.get("created_at") if isinstance(row.get("created_at"), datetime) else datetime.now()
        )
