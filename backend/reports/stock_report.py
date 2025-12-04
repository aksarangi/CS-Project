# backend/reports/stock_report.py

from backend.database.db_connection import get_connection
from backend.utils.logger import logger

class StockReport:
    """
    Generates inventory/stock reports for the bookshop.
    Headless: returns data only, frontend handles visualization.
    """

    def get_current_stock(self):
        """
        Returns a list of all books with current stock and related info.
        """
        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in get_current_stock()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT b.book_id, b.title, b.stock, c.name AS category,
                       p.name AS publisher, b.price
                FROM books b
                LEFT JOIN categories c ON b.category_id = c.category_id
                LEFT JOIN publishers p ON b.publisher_id = p.publisher_id
                ORDER BY b.title ASC
            """)
            rows = cursor.fetchall()
            logger.info(f"Fetched stock info for {len(rows)} books")
            return {"status": "success","message": "search results", "data":rows}
        except Exception as e:
            logger.error(f"Error fetching stock info: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    def get_low_stock(self, threshold=10):
        """
        Returns books where stock is below a threshold.
        """
        all_stock = self.get_current_stock().get("data", [])
        low_stock_books = [book for book in all_stock if book['stock'] is not None and book['stock'] < threshold]
        logger.info(f"Found {len(low_stock_books)} low stock books (threshold={threshold})")
        return {"status": "success","message": "search results", "data":low_stock_books}

    def get_category_stock_summary(self):
        """
        Returns stock summary aggregated by category.
        """
        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in get_category_stock_summary()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT c.name AS category, COUNT(b.book_id) AS num_books,
                       SUM(b.stock) AS total_stock
                FROM books b
                LEFT JOIN categories c ON b.category_id = c.category_id
                GROUP BY c.category_id
                ORDER BY total_stock DESC
            """)
            rows = cursor.fetchall()
            logger.info(f"Fetched category-wise stock summary for {len(rows)} categories")
            return {"status": "success","message": "search results", "data":[{"category": row['category'], "num_books": int(row['num_books']), "total_stock": int(row['total_stock'])} for row in rows]}
        except Exception as e:
            logger.error(f"Error fetching category stock summary: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()
