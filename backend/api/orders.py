# backend/api/orders.py

from database.db_connection import get_connection
from utils.helpers import format_date
from utils.logger import logger

class OrdersAPI:
    """
    Local API class to manage orders.
    Supports CRUD + search.
    """

    def get_all(self, customer_id=None, status=None):
        """
        Returns all orders, optionally filtered by customer_id or status.
        """
        conn = get_connection()
        if not conn:
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT * FROM orders WHERE 1=1"
            params = []

            if customer_id:
                query += " AND customer_id=%s"
                params.append(customer_id)
            if status:
                query += " AND order_status=%s"
                params.append(status)

            cursor.execute(query, tuple(params))
            orders = cursor.fetchall()
            for o in orders:
                o["order_date"] = format_date(o.get("order_date"))
            logger.info(f"Fetched {len(orders)} orders")
            return {"status": "success", "data": orders}
        except Exception as e:
            logger.error(f"Error fetching orders: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    def get_by_id(self, order_id):
        """
        Fetch a single order by ID.
        """
        conn = get_connection()
        if not conn:
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM orders WHERE order_id=%s", (order_id,))
            order = cursor.fetchone()
            if order:
                order["order_date"] = format_date(order.get("order_date"))
                return {"status": "success", "data": order}
            else:
                return {"status": "error", "message": "Order not found"}
        except Exception as e:
            logger.error(f"Error fetching order {order_id}: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    def add(self, order_data):
        """
        Add a new order.
        """
        customer_id = order_data.get("customer_id")
        total_amount = order_data.get("total_amount", 0)
        order_status = order_data.get("order_status", "Pending")

        conn = get_connection()
        if not conn:
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO orders (customer_id, total_amount, order_status)
                VALUES (%s, %s, %s)
            """, (customer_id, total_amount, order_status))
            conn.commit()
            order_id = cursor.lastrowid
            logger.info(f"Order added: {order_id}")
            return {"status": "success", "message": "Order added", "order_id": order_id}
        except Exception as e:
            logger.error(f"Error adding order: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    def update(self, order_id, updates):
        """
        Update any editable fields for an order.
        Example: update(1, {"order_status": "Completed", "total_amount": 500})
        """
        if not updates:
            return {"status": "error", "message": "No fields to update"}

        conn = get_connection()
        if not conn:
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor()
        try:
            set_clause = ", ".join(f"{key}=%s" for key in updates.keys())
            values = list(updates.values()) + [order_id]
            sql = f"UPDATE orders SET {set_clause} WHERE order_id=%s"
            cursor.execute(sql, tuple(values))
            conn.commit()
            logger.info(f"Order {order_id} updated with {updates}")
            return {"status": "success", "message": "Order updated"}
        except Exception as e:
            logger.error(f"Error updating order {order_id}: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    def delete(self, order_id):
        """
        Delete an order.
        """
        conn = get_connection()
        if not conn:
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM orders WHERE order_id=%s", (order_id,))
            conn.commit()
            logger.info(f"Order deleted: {order_id}")
            return {"status": "success", "message": "Order deleted"}
        except Exception as e:
            logger.error(f"Error deleting order {order_id}: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    def search(self, by, query):
        """
        Search orders by any allowed field.
        """
        allowed_fields = ["order_id", "customer_id", "order_status", "order_date"]
        if by not in allowed_fields:
            return {"status": "error", "message": f"Invalid search field '{by}'"}

        conn = get_connection()
        if not conn:
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor(dictionary=True)
        try:
            sql = f"SELECT * FROM orders WHERE {by} LIKE %s"
            cursor.execute(sql, (f"%{query}%",))
            results = cursor.fetchall()
            for r in results:
                r["order_date"] = format_date(r.get("order_date"))
            logger.info(f"Search '{query}' in '{by}' → {len(results)} results")
            return {"status": "success", "data": results}
        except Exception as e:
            logger.error(f"Error searching orders: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()