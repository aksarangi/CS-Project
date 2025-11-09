# backend/models/payment_model.py

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class PaymentModel:
    payment_id: Optional[int] = None
    order_id: int = 0
    payment_method: str = "UPI"  # UPI, Card, NetBanking, Cash
    amount: float = 0.0
    payment_status: str = "Pending"  # Success, Pending, Failed, Cancelled
    transaction_id: Optional[str] = None
    payment_date: datetime = field(default_factory=datetime.now)

    def to_dict(self):
        """
        Returns a JSON-serializable dictionary of the Payment.
        """
        return {
            "payment_id": self.payment_id,
            "order_id": self.order_id,
            "payment_method": self.payment_method,
            "amount": self.amount,
            "payment_status": self.payment_status,
            "transaction_id": self.transaction_id,
            "payment_date": self.payment_date.strftime("%Y-%m-%d %H:%M:%S")
        }

    @classmethod
    def from_db_row(cls, row: dict):
        """
        Creates a PaymentModel instance from a database row.
        """
        return cls(
            payment_id=row.get("payment_id"),
            order_id=row.get("order_id", 0),
            payment_method=row.get("payment_method", "UPI"),
            amount=float(row.get("amount", 0.0)),
            payment_status=row.get("payment_status", "Pending"),
            transaction_id=row.get("transaction_id"),
            payment_date=row.get("payment_date") if isinstance(row.get("payment_date"), datetime) else datetime.now()
        )
