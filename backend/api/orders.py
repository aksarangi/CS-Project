# backend/api/orders.py

from database.db_connection import get_connection
from utils.helpers import safe_get, format_date, round_price
from utils.validators import is_positive_number
from utils.logger import logger
from backend.models.order_model import OrderModel, OrderItemModel


class OrdersAPI:
    """
    Local API class to manage orders using OrderModel.
    Provides CRUD + search functionality.
    """

    def get_all(self, customer_id=None, status=None):
        """
        Returns all orders, optionally filtered by customer_id or status.
        """
        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in get_all()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT * FROM orders WHERE 1=1"
            params = []

            if customer_id:
                query += " AND customer_id=%s"
                params.append(customer_id)
            if status:
                query += " AND status=%s"
                params.append(status)

            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            orders = [OrderModel.from_db_row(row).to_dict() for row in rows]
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
        Fetch a single order by order_id along with its items
        """
        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in get_by_id()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM orders WHERE order_id=%s", (order_id,))
            row = cursor.fetchone()
            if not row:
                logger.warning(f"Order not found: {order_id}")
                return {"status": "error", "message": "Order not found"}

            order = OrderModel.from_db_row(row)

            # Fetch order items
            cursor.execute("""
                SELECT oi.item_id, oi.book_id, b.title AS book_title, oi.quantity, oi.price_each
                FROM order_items oi
                JOIN books b ON oi.book_id = b.book_id
                WHERE oi.order_id=%s
            """, (order_id,))
            items_rows = cursor.fetchall()
            order.items = [OrderItemModel.from_db_row(item) for item in items_rows]

            order.order_date = format_date(order.order_date)
            logger.info(f"Order fetched: {order_id} with {len(order.items)} items")
            return {"status": "success", "data": order.to_dict()}

        except Exception as e:
            logger.error(f"Error fetching order {order_id}: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    def add(self, order_data):
        """
        Add a new order.
        Required: customer_id, items (list of {book_id, quantity})
        """
        customer_id = safe_get(order_data, "customer_id")
        items = safe_get(order_data, "items")
        if not customer_id or not items or not isinstance(items, list):
            return {"status": "error", "message": "customer_id and items are required"}

        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in add()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor()
        try:
            total_amount = 0
            item_details = []

            for item in items:
                book_id = item.get("book_id")
                quantity = item.get("quantity")
                if not book_id or not is_positive_number(quantity):
                    return {"status": "error", "message": "Invalid book_id or quantity"}

                cursor.execute("SELECT price, stock FROM books WHERE book_id=%s", (book_id,))
                book = cursor.fetchone()
                if not book:
                    return {"status": "error", "message": f"Book not found: {book_id}"}

                price_each, stock = float(book[0]), int(book[1])
                if quantity > stock:
                    return {"status": "error", "message": f"Insufficient stock for book {book_id}"}

                total_amount += price_each * quantity
                item_details.append(OrderItemModel(book_id=book_id, quantity=quantity, price_each=round_price(price_each)))

            # Insert order
            cursor.execute("INSERT INTO orders (customer_id, total_amount) VALUES (%s, %s)", 
                           (customer_id, round_price(total_amount)))
            order_id = cursor.lastrowid

            # Insert order items
            for item in item_details:
                cursor.execute("""
                    INSERT INTO order_items (order_id, book_id, quantity, price_each)
                    VALUES (%s, %s, %s, %s)
                """, (order_id, item.book_id, item.quantity, item.price_each))

            conn.commit()
            logger.info(f"Order added: {order_id} for customer {customer_id}")

            order = OrderModel(order_id=order_id, customer_id=customer_id, total_amount=round_price(total_amount), items=item_details)
            return {"status": "success", "message": "Order placed", "data": order.to_dict()}

        except Exception as e:
            logger.error(f"Error adding order: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    def update_status(self, order_id, status):
        """
        Update the status of an order.
        """
        if status not in ['Pending', 'Confirmed', 'Shipped', 'Delivered', 'Cancelled']:
            return {"status": "error", "message": "Invalid status"}

        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in update_status()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE orders SET status=%s WHERE order_id=%s", (status, order_id))
            conn.commit()
            logger.info(f"Order {order_id} status updated to {status}")
            return {"status": "success", "message": "Order status updated"}

        except Exception as e:
            logger.error(f"Error updating order status {order_id}: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    def delete(self, order_id):
        """
        Delete an order (and its items via trigger).
        """
        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in delete()")
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
