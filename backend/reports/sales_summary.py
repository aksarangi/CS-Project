# backend/reports/sales_summary.py

from backend.database.db_connection import get_connection
from backend.utils.helpers import format_date
from backend.utils.logger import logger
from collections import defaultdict

class SalesSummaryReport:
    """
    Generates sales summary reports for the bookshop.
    Headless: returns data only, GUI should handle visualization.
    """

    def get_daily_sales(self):
        """
        Returns a dictionary with date -> total sales amount and number of orders.
        """
        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in get_daily_sales()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT DATE(order_date) AS order_day,
                       COUNT(order_id) AS num_orders,
                       SUM(total_amount) AS total_sales
                FROM orders
                WHERE status IN ('Confirmed', 'Shipped', 'Delivered')
                GROUP BY DATE(order_date)
                ORDER BY DATE(order_date) ASC
            """)
            rows = cursor.fetchall()
            daily_sales = {}
            for row in rows:
                daily_sales[str(row['order_day'])] = {
                    "num_orders": row['num_orders'],
                    "total_sales": float(row['total_sales'])
                }
            logger.info(f"Daily sales data fetched: {len(daily_sales)} days")
            return {"status": "success","message": "search results", "data":daily_sales}
        except Exception as e:
            logger.error(f"Error fetching daily sales: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    def get_daily_sales_plot_data(self):
        """
        Returns data suitable for plotting: (dates list, sales list)
        Frontend can use these to plot charts.
        """
        daily_sales = self.get_daily_sales()
        if not daily_sales:
            return {"status": "error", "message": "No daily sales data"}

        dates = list(daily_sales.keys())
        sales = [daily_sales[date]['total_sales'] for date in dates]
        return {"status": "success","message": "search results", "data":[dates, sales]}

    def top_selling_books(self, limit=10):
        """
        Returns top-selling books based on order_items quantity.
        """
        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in top_selling_books()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT b.title, SUM(oi.quantity) AS total_sold, full_name as author_name, b.book_id
                FROM order_items oi
                JOIN books b ON oi.book_id = b.book_id
                JOIN orders o ON oi.order_id = o.order_id
                JOIN authors a ON b.author_id = a.author_id
                WHERE o.status IN ('Confirmed', 'Shipped', 'Delivered')
                GROUP BY b.book_id
                ORDER BY total_sold DESC
                LIMIT %s
            """, (limit,))
            rows = cursor.fetchall()
            logger.info(f"Fetched top {limit} selling books")
            return {"status": "success","message": "search results", "data":[{"book_id": row['book_id'],"author_name": row['author_name'],"title": row['title'], "total_sold": int(row['total_sold'])} for row in rows]}
        except Exception as e:
            logger.error(f"Error fetching top-selling books: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()
