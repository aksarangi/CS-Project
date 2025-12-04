# backend/api/orders.py

from backend.database.db_connection import get_connection
from backend.utils.helpers import format_date
from backend.utils.logger import logger
from backend.models.order_model import OrderModel, OrderItemModel
from backend.api import books as books_module  # for price lookup and stock checks


class OrdersAPI:
    """
    OrdersAPI — supports creating orders with items, fetching orders with items,
    updating order-level fields, deleting, and searching.
    """

    def _fetch_items_for_order(self, conn, order_id):
        """
        Helper: return list of item rows (dicts) for the given order_id
        """
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute("""
                SELECT oi.item_id, oi.order_id, oi.book_id, oi.quantity, oi.price_each
                FROM order_items oi
                WHERE oi.order_id = %s
            """, (order_id,))
            items = cur.fetchall()
            return items
        finally:
            cur.close()

    def get_all(self):
        conn = get_connection()
        if not conn:
            return {"status": "error", "message": "DB connection failed"}

        cur = conn.cursor(dictionary=True)
        try:
            cur.execute("SELECT * FROM orders WHERE 1=1")
            orders = cur.fetchall()

            result = []
            for o in orders:
                # fetch items for each order
                items = self._fetch_items_for_order(conn, o["order_id"])
                order_model = OrderModel.from_db_row(o, items)
                d = order_model.to_dict()
                # format date already in model but ensure consistent formatting
                d["order_date"] = format_date(o.get("order_date"))
                result.append(d)

            logger.info(f"Fetched {len(result)} orders")
            return {"status": "success", "message": "Fetched all orders", "data": result}
        except Exception as e:
            logger.error(f"Error fetching orders: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cur.close()
            conn.close()

    def get_by_id(self, order_id):
        conn = get_connection()
        if not conn:
            return {"status": "error", "message": "DB connection failed"}

        cur = conn.cursor(dictionary=True)
        try:
            cur.execute("SELECT * FROM orders WHERE order_id=%s", (order_id,))
            order = cur.fetchone()
            if not order:
                return {"status": "error", "message": "Order not found"}

            items = self._fetch_items_for_order(conn, order_id)
            order_model = OrderModel.from_db_row(order, items)
            data = order_model.to_dict()
            data["order_date"] = format_date(order.get("order_date"))
            return {"status": "success", "message": "Fetched order by id", "data": data}
        except Exception as e:
            logger.error(f"Error fetching order {order_id}: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cur.close()
            conn.close()

    def add(self, order_data):
        """
        Add a new order along with its items.
        order_data: {
            "customer_id": int,
            "total_amount": float,
            "order_status": str,
            "items": [
                {"book_id": int, "quantity": int, "price_each": float}, ...
            ]
        }
        """
        customer_id = order_data.get("customer_id")
        total_amount = order_data.get("total_amount", 0)
        order_status = order_data.get("order_status", "Pending")
        items = order_data.get("items", [])

        if not customer_id or not items:
            return {"status": "error", "message": "Customer ID and order items required"}

        conn = get_connection()
        if not conn:
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor()
        try:
            # Begin transaction
            cursor.execute("""
                INSERT INTO orders (customer_id, total_amount, status)
                VALUES (%s, %s, %s)
            """, (customer_id, total_amount, order_status))
            order_id = cursor.lastrowid

            # Insert order items
            for item in items:
                cursor.execute("""
                    INSERT INTO order_items (order_id, book_id, quantity, price_each)
                    VALUES (%s, %s, %s, %s)
                """, (order_id, item["book_id"], item["quantity"], item["price_each"]))

            conn.commit()
            logger.info(f"Order {order_id} added with {len(items)} items")
            
            # Fetch full order with items
            cursor.execute("SELECT * FROM order_items WHERE order_id=%s", (order_id,))
            item_rows = cursor.fetchall()
            cursor.execute("SELECT * FROM orders WHERE order_id=%s", (order_id,))
            order_row = cursor.fetchone()
            return {
                "status": "success",
                "message": "Order added successfully",
                "data": OrderModel.from_db_row(order_row, items=item_rows).to_dict()
            }

        except Exception as e:
            conn.rollback()
            logger.error(f"Error adding order: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    def update(self, order_id, updates):
        """
        Update order-level fields OR if updates contains 'items' we won't handle item-level edits here.
        Keep this to update order status or total_amount (rare).
        Use OrderItemsAPI for item-level operations.
        """
        if not updates:
            return {"status": "error", "message": "No fields to update"}

        # Prevent updating protected fields accidentally
        allowed_order_fields = {"customer_id", "total_amount", "status"}
        order_updates = {k: v for k, v in updates.items() if k in allowed_order_fields}

        if not order_updates:
            return {"status": "error", "message": "No valid order fields to update"}

        conn = get_connection()
        if not conn:
            return {"status": "error", "message": "DB connection failed"}

        cur = conn.cursor()
        try:
            set_clause = ", ".join(f"{k}=%s" for k in order_updates.keys())
            values = list(order_updates.values()) + [order_id]
            sql = f"UPDATE orders SET {set_clause} WHERE order_id=%s"
            cur.execute(sql, tuple(values))
            conn.commit()
            logger.info(f"Order {order_id} updated with {order_updates}")
            return self.get_by_id(order_id)
        except Exception as e:
            conn.rollback()
            logger.error(f"Error updating order {order_id}: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cur.close()
            conn.close()

    def delete(self, order_id):
        """
        Delete order. Cascading FK will delete order_items as well.
        We must restore stock for deleted order items because trigger only subtracts on insert.
        So before deleting we will fetch items and add their quantities back to books.stock.
        """
        conn = get_connection()
        if not conn:
            return {"status": "error", "message": "DB connection failed"}

        cur = conn.cursor(dictionary=True)
        try:
            # Fetch items to restore stock
            cur.execute("SELECT book_id, quantity FROM order_items WHERE order_id=%s", (order_id,))
            items = cur.fetchall()

            # restore stock for each item
            for it in items:
                cur.execute("UPDATE books SET stock = stock + %s WHERE book_id=%s", (it["quantity"], it["book_id"]))

            # delete the order (cascade will remove order_items)
            cur.execute("DELETE FROM orders WHERE order_id=%s", (order_id,))
            conn.commit()
            logger.info(f"Order deleted: {order_id}")
            return {"status": "success", "message": "Order deleted", "data": order_id}
        except Exception as e:
            conn.rollback()
            logger.error(f"Error deleting order {order_id}: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cur.close()
            conn.close()

    def record_payment(self, order_id, amount, method="UPI", status="Success", transaction_id=None):
        """
        Record a payment for an order.
        - order_id: int
        - amount: float
        - method: str (UPI, Card, NetBanking, Cash)
        - status: str (Success, Pending, Failed, Cancelled)
        - transaction_id: str (optional, fake id)
        """
        if not order_id or amount is None:
            return {"status": "error", "message": "Order ID and amount are required"}

        conn = get_connection()
        if not conn:
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor()
        try:
            # Check if order exists
            cursor.execute("SELECT * FROM orders WHERE order_id=%s", (order_id,))
            order = cursor.fetchone()
            if not order:
                return {"status": "error", "message": f"Order {order_id} not found"}

            # Insert payment
            cursor.execute("""
                INSERT INTO payments (order_id, payment_method, amount, payment_status, transaction_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (order_id, method, amount, status, transaction_id))
            conn.commit()
            payment_id = cursor.lastrowid
            logger.info(f"Payment {payment_id} recorded for Order {order_id}")

            return {
                "status": "success",
                "message": "Payment recorded successfully",
                "data": {
                    "payment_id": payment_id,
                    "order_id": order_id,
                    "amount": amount,
                    "method": method,
                    "status": status,
                    "transaction_id": transaction_id
                }
            }

        except Exception as e:
            conn.rollback()
            logger.error(f"Error recording payment for order {order_id}: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    def search(self, by, query):
        allowed_fields = ["order_id", "customer_id", "status", "order_date"]
        if by not in allowed_fields:
            return {"status": "error", "message": f"Invalid search field '{by}'"}

        conn = get_connection()
        if not conn:
            return {"status": "error", "message": "DB connection failed"}

        cur = conn.cursor(dictionary=True)
        try:
            sql = f"SELECT * FROM orders WHERE {by} LIKE %s"
            cur.execute(sql, (f"%{query}%",))
            results = cur.fetchall()

            data = []
            for r in results:
                items = self._fetch_items_for_order(conn, r["order_id"])
                order_model = OrderModel.from_db_row(r, items)
                d = order_model.to_dict()
                d["order_date"] = format_date(r.get("order_date"))
                data.append(d)

            logger.info(f"Search '{query}' in '{by}' → {len(data)} results")
            return {"status": "success", "message": "Search results", "data": data}
        except Exception as e:
            logger.error(f"Error searching orders: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cur.close()
            conn.close()
