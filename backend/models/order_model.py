# backend/models/order_model.py

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict

@dataclass
class OrderItemModel:
    item_id: Optional[int] = None
    book_id: int = 0
    quantity: int = 1
    price_each: float = 0.0

    def to_dict(self):
        return {
            "item_id": self.item_id,
            "book_id": self.book_id,
            "quantity": self.quantity,
            "price_each": self.price_each
        }

    @classmethod
    def from_db_row(cls, row: dict):
        return cls(
            item_id=row.get("item_id"),
            book_id=row.get("book_id", 0),
            quantity=row.get("quantity", 1),
            price_each=float(row.get("price_each", 0.0))
        )

@dataclass
class OrderModel:
    order_id: Optional[int] = None
    customer_id: int = 0
    order_date: datetime = field(default_factory=datetime.now)
    total_amount: float = 0.0
    status: str = "Pending"
    items: List[OrderItemModel] = field(default_factory=list)

    def to_dict(self):
        """
        Returns a JSON-serializable dictionary of the Order including items.
        """
        return {
            "order_id": self.order_id,
            "customer_id": self.customer_id,
            "order_date": self.order_date.strftime("%Y-%m-%d %H:%M:%S"),
            "total_amount": self.total_amount,
            "status": self.status,
            "items": [item.to_dict() for item in self.items]
        }

    @classmethod
    def from_db_row(cls, row: dict, items: Optional[List[Dict]] = None):
        """
        Creates an OrderModel instance from a database row and optional list of item rows.
        """
        order_items = []
        if items:
            for item_row in items:
                order_items.append(OrderItemModel.from_db_row(item_row))

        return cls(
            order_id=row.get("order_id"),
            customer_id=row.get("customer_id", 0),
            order_date=row.get("order_date") if isinstance(row.get("order_date"), datetime) else datetime.now(),
            total_amount=float(row.get("total_amount", 0.0)),
            status=row.get("status", "Pending"),
            items=order_items
        )
