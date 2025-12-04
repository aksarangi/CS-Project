# backend/api/order_items.py

from database.db_connection import get_connection
from utils.logger import logger
from backend.models.order_model import OrderItemModel
from backend.api import books as books_module


class OrderItemsAPI:
    """
    API to manage order items individually.
    Note: when adding items, the orders table's total_amount must be updated accordingly.
    """

    def get_by_order(self, order_id):
        conn = get_connection()
        if not conn:
            return {"status": "error", "message": "DB connection failed"}
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute("""
                SELECT oi.item_id, oi.order_id, oi.book_id, oi.quantity, oi.price_each
                FROM order_items oi
                WHERE oi.order_id = %s
            """, (order_id,))
            rows = cur.fetchall()
            data = [OrderItemModel.from_db_row(r).to_dict() for r in rows]
            return {"status": "success", "message": "Items fetched", "data": data}
        except Exception as e:
            logger.error(f"Error fetching items for order {order_id}: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cur.close()
            conn.close()

    def add_item(self, order_id, item_data):
        """
        item_data: {"book_id": int, "quantity": int}
        Behavior:
         - Validate book exists and stock
         - Insert order_items row (trigger will reduce stock)
         - Update orders.total_amount
        """
        book_id = item_data.get("book_id")
        qty = int(item_data.get("quantity", 1))
        if not book_id or qty <= 0:
            return {"status": "error", "message": "book_id and positive quantity required"}

        conn = get_connection()
        if not conn:
            return {"status": "error", "message": "DB connection failed"}
        cur = conn.cursor()
        try:
            # lock the book row to check stock
            cur.execute("SELECT price, stock FROM books WHERE book_id=%s FOR UPDATE", (book_id,))
            row = cur.fetchone()
            if not row:
                return {"status": "error", "message": "Book not found"}
            price_each = float(row[0])
            current_stock = int(row[1] or 0)
            if current_stock < qty:
                return {"status": "error", "message": f"Insufficient stock (available {current_stock})"}

            # insert item
            cur.execute("""
                INSERT INTO order_items (order_id, book_id, quantity, price_each)
                VALUES (%s, %s, %s, %s)
            """, (order_id, book_id, qty, price_each))
            item_id = cur.lastrowid

            # update order total_amount
            subtotal = price_each * qty
            cur.execute("UPDATE orders SET total_amount = total_amount + %s WHERE order_id=%s", (round(subtotal, 2), order_id))

            conn.commit()
            logger.info(f"Added item {item_id} to order {order_id}")
            # return the inserted item
            cur2 = conn.cursor(dictionary=True)
            cur2.execute("SELECT * FROM order_items WHERE item_id=%s", (item_id,))
            inserted = cur2.fetchone()
            cur2.close()
            return {"status": "success", "message": "Item added", "data": OrderItemModel.from_db_row(inserted).to_dict()}
        except Exception as e:
            conn.rollback()
            logger.error(f"Error adding item to order {order_id}: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cur.close()
            conn.close()

    def update_item(self, item_id, updates):
        """
        updates: {"quantity": new_quantity} - only quantity supported here.
        Behavior:
          - Compute delta in quantity, update order.total_amount accordingly
          - Adjust books.stock accordingly (if increasing quantity -> reduce stock; if decreasing -> increase stock)
        """
        if not updates or "quantity" not in updates:
            return {"status": "error", "message": "No supported updates provided"}

        new_qty = int(updates["quantity"])
        if new_qty <= 0:
            return {"status": "error", "message": "Quantity must be positive"}

        conn = get_connection()
        if not conn:
            return {"status": "error", "message": "DB connection failed"}
        cur = conn.cursor(dictionary=True)
        try:
            # fetch existing item
            cur.execute("SELECT * FROM order_items WHERE item_id=%s", (item_id,))
            item = cur.fetchone()
            if not item:
                return {"status": "error", "message": "Item not found"}

            old_qty = int(item["quantity"])
            book_id = int(item["book_id"])
            price_each = float(item["price_each"])
            delta = new_qty - old_qty
            # handle stock: if delta >0 need to ensure enough stock; if delta <0 we will restore stock
            if delta > 0:
                # check book stock
                cur.execute("SELECT stock FROM books WHERE book_id=%s FOR UPDATE", (book_id,))
                br = cur.fetchone()
                if not br:
                    return {"status": "error", "message": "Book not found"}
                avail = int(br[0] or 0)
                if avail < delta:
                    return {"status": "error", "message": f"Insufficient stock to increase quantity by {delta}"}
                # decrement stock
                cur.execute("UPDATE books SET stock = stock - %s WHERE book_id=%s", (delta, book_id))
            elif delta < 0:
                # restore stock
                cur.execute("UPDATE books SET stock = stock + %s WHERE book_id=%s", (abs(delta), book_id))

            # update order_items.quantity
            cur.execute("UPDATE order_items SET quantity=%s WHERE item_id=%s", (new_qty, item_id))
            # update order total
            subtotal_delta = (new_qty - old_qty) * price_each
            cur.execute("UPDATE orders SET total_amount = total_amount + %s WHERE order_id=%s", (round(subtotal_delta, 2), item["order_id"]))

            conn.commit()
            logger.info(f"Updated item {item_id} quantity from {old_qty} to {new_qty}")
            # return updated item
            cur2 = conn.cursor(dictionary=True)
            cur2.execute("SELECT * FROM order_items WHERE item_id=%s", (item_id,))
            updated = cur2.fetchone()
            cur2.close()
            return {"status": "success", "message": "Item updated", "data": OrderItemModel.from_db_row(updated).to_dict()}
        except Exception as e:
            conn.rollback()
            logger.error(f"Error updating item {item_id}: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cur.close()
            conn.close()

    def delete_item(self, item_id):
        """
        Delete an order item:
         - restore books.stock by quantity
         - reduce orders.total_amount by price_each * quantity
         - delete the order_items row
        """
        conn = get_connection()
        if not conn:
            return {"status": "error", "message": "DB connection failed"}
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute("SELECT * FROM order_items WHERE item_id=%s", (item_id,))
            item = cur.fetchone()
            if not item:
                return {"status": "error", "message": "Item not found"}

            qty = int(item["quantity"])
            book_id = int(item["book_id"])
            price_each = float(item["price_each"])
            subtotal = qty * price_each

            # restore stock
            cur.execute("UPDATE books SET stock = stock + %s WHERE book_id=%s", (qty, book_id))
            # update order total
            cur.execute("UPDATE orders SET total_amount = total_amount - %s WHERE order_id=%s", (round(subtotal, 2), item["order_id"]))
            # delete item
            cur.execute("DELETE FROM order_items WHERE item_id=%s", (item_id,))

            conn.commit()
            logger.info(f"Deleted order item {item_id}")
            return {"status": "success", "message": "Item deleted", "data": item_id}
        except Exception as e:
            conn.rollback()
            logger.error(f"Error deleting item {item_id}: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cur.close()
            conn.close()
