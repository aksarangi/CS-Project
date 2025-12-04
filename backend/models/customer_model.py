# backend/models/customer_model.py

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class CustomerModel:
    customer_id: Optional[int] = None
    full_name: str = ""
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: str = "India"
    postal_code: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self):
        """
        Returns a JSON-serializable dictionary of the Customer.
        """
        return {
            "customer_id": self.customer_id,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "country": self.country,
            "postal_code": self.postal_code,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }

    @classmethod
    def from_db_row(cls, row: dict):
        """
        Creates a CustomerModel instance from a database row.
        """
        return cls(
            customer_id=row.get("customer_id"),
            full_name=row.get("full_name", ""),
            email=row.get("email"),
            phone=row.get("phone"),
            address=row.get("address"),
            city=row.get("city"),
            state=row.get("state"),
            country=row.get("country", "India"),
            postal_code=row.get("postal_code"),
            created_at=row.get("created_at") if isinstance(row.get("created_at"), datetime) else datetime.now()
        )
