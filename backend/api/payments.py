# backend/api/payments.py

from backend.database.db_connection import get_connection
from backend.utils.helpers import safe_get, format_date, round_price
from backend.utils.validators import is_positive_number
from backend.utils.logger import logger
from backend.models.payment_model import PaymentModel


class PaymentsAPI:
    """
    Local API class to manage payments using PaymentModel.
    Supports CRUD, validation, and flexible search.
    """

    def search(self, field=None, value=None):
        """
        Flexible search for payments.
        If no field/value provided → returns all payments.
        If field provided → filters dynamically.
        """
        allowed_fields = ["payment_id", "order_id", "payment_method", "payment_status", "transaction_id", "amount"]

        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in search()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor(dictionary=True)
        try:
            if not field or not value:
                query = "SELECT * FROM payments"
                params = ()
            else:
                if field not in allowed_fields:
                    return {"status": "error", "message": f"Invalid search field '{field}'"}
                query = f"SELECT * FROM payments WHERE {field} LIKE %s"
                params = (f"%{value}%",)

            cursor.execute(query, params)
            rows = cursor.fetchall()
            payments = [PaymentModel.from_db_row(row).to_dict() for row in rows]
            logger.info(f"Search in payments by {field or 'ALL'}='{value or ''}' → {len(payments)} results")
            return {"status": "success","message":"Search Results", "data": payments}

        except Exception as e:
            logger.error(f"Error searching payments: {e}")
            return {"status": "error", "message": str(e)}

        finally:
            cursor.close()
            conn.close()

    def add(self, payment_data):
        """
        Add a new payment.
        Required: order_id, amount
        Optional: payment_method, payment_status, transaction_id
        """
        order_id = safe_get(payment_data, "order_id")
        amount = safe_get(payment_data, "amount")
        if not order_id or not is_positive_number(amount):
            return {"status": "error", "message": "order_id and valid amount are required"}

        payment_method = safe_get(payment_data, "payment_method", "UPI")
        payment_status = safe_get(payment_data, "payment_status", "Pending")
        transaction_id = safe_get(payment_data, "transaction_id")

        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in add()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor()
        try:
            # Validate order existence
            cursor.execute("SELECT total_amount FROM orders WHERE order_id=%s", (order_id,))
            order = cursor.fetchone()
            if not order:
                return {"status": "error", "message": f"Order {order_id} not found"}

            total_amount = float(order[0])
            if amount > total_amount:
                return {"status": "error", "message": "Payment amount exceeds order total"}

            # Insert new payment
            cursor.execute("""
                INSERT INTO payments (order_id, payment_method, amount, payment_status, transaction_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (order_id, payment_method, round_price(amount), payment_status, transaction_id))
            conn.commit()
            payment_id = cursor.lastrowid
            logger.info(f"Payment added: {payment_id} for order {order_id}")

            payment = PaymentModel(payment_id=payment_id, order_id=order_id, amount=round_price(amount),
                                   payment_method=payment_method, payment_status=payment_status,
                                   transaction_id=transaction_id)
            return {"status": "success", "message": "Payment recorded", "data": payment.to_dict()}

        except Exception as e:
            logger.error(f"Error adding payment: {e}")
            return {"status": "error", "message": str(e)}

        finally:
            cursor.close()
            conn.close()

    def update_status(self, payment_id, payment_status):
        """
        Update payment status
        """
        valid_status = ['Success', 'Pending', 'Failed', 'Cancelled']
        if payment_status not in valid_status:
            return {"status": "error", "message": f"Invalid payment_status '{payment_status}'"}

        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in update_status()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE payments SET payment_status=%s WHERE payment_id=%s",
                           (payment_status, payment_id))
            conn.commit()
            logger.info(f"Payment {payment_id} status updated to {payment_status}")
            return {"status": "success", "message": "Payment status updated", "data": self.search("payment_id", payment_id).get("data",[])[0].to_dict()}

        except Exception as e:
            logger.error(f"Error updating payment {payment_id}: {e}")
            return {"status": "error", "message": str(e)}

        finally:
            cursor.close()
            conn.close()

    def delete(self, payment_id):
        """
        Delete a payment
        """
        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in delete()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM payments WHERE payment_id=%s", (payment_id,))
            conn.commit()
            logger.info(f"Payment deleted: {payment_id}")
            return {"status": "success", "message": "Payment deleted", "data":payment_id}

        except Exception as e:
            logger.error(f"Error deleting payment {payment_id}: {e}")
            return {"status": "error", "message": str(e)}

        finally:
            cursor.close()
            conn.close()
