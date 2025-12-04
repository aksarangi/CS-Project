# backend/models/book_model.py

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class BookModel:
    book_id: Optional[int] = None
    title: str = ""
    author_id: int = 0
    author: str = ""
    publisher_id: Optional[int] = None
    publisher_name: str = ""
    category_id: Optional[int] = None
    genre: str = ""
    language: str = "English"
    isbn: Optional[str] = None
    publication_year: Optional[int] = None
    price: float = 0.0
    stock: int = 0
    description: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self):
        """
        Returns a JSON-serializable dictionary of the Book.
        """
        return {
            "book_id": self.book_id,
            "title": self.title,
            "author_id": self.author_id,
            "author": self.author,
            "publisher_id": self.publisher_id,
            "publisher_name": self.publisher_name,
            "category_id": self.category_id,
            "genre": self.genre,
            "language": self.language,
            "isbn": self.isbn,
            "publication_year": self.publication_year,
            "price": self.price,
            "stock": self.stock,
            "description": self.description,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        }

    @classmethod
    def from_db_row(cls, row: dict):
        """
        Creates a BookModel instance from a database row.
        """
        return cls(
            book_id=row.get("book_id"),
            title=row.get("title", ""),
            author_id=row.get("author_id", 0),
            author=row.get("author_name", ""),
            publisher_id=row.get("publisher_id"),
            publisher_name=row.get("publisher_name", ""),
            category_id=row.get("category_id"),
            genre=row.get("genre", ""),
            language=row.get("language", "English"),
            isbn=row.get("isbn"),
            publication_year=row.get("publication_year"),
            price=float(row.get("price", 0.0)),
            stock=row.get("stock", 0),
            description=row.get("description"),
            created_at=row.get("created_at") if isinstance(row.get("created_at"), datetime) else datetime.now(),
            updated_at=row.get("updated_at") if isinstance(row.get("updated_at"), datetime) else datetime.now()
        )
