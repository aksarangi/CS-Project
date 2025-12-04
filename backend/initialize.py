# backend/initialize.py

from backend.api.publishers import PublishersAPI
from backend.api.staff import StaffAPI
from backend.api.authors import AuthorsAPI
from backend.api.books import BookAPI
from backend.api.orders import OrdersAPI
from backend.api.payments import PaymentsAPI
from backend.api.categories import CategoriesAPI
from backend.api.customers import CustomersAPI
from backend.api.reports import ReportsAPI

from backend.utils.logger import logger
from backend.database.db_connection import get_connection

class Backend:
    """
    Main backend entry point.
    Provides unified access to all local APIs.
    """
    def __init__(self):
        logger.info("Initializing backend system...")

        # Test database connection
        conn = get_connection()
        if conn:
            logger.info("Database connection successful.")
            conn.close()
        else:
            logger.error("Database connection failed on startup!")

        # Initialize all APIs
        self.publishers = PublishersAPI()
        self.staff = StaffAPI()
        self.authors = AuthorsAPI()
        self.books = BookAPI()
        self.orders = OrdersAPI()
        self.payments = PaymentsAPI()
        self.categories = CategoriesAPI()
        self.customers = CustomersAPI()
        self.reports = ReportsAPI()

        logger.info("All API modules initialized.")

    def health_check(self):
        """Simple system check for UI use."""
        conn = get_connection()
        db_status = "connected" if conn else "disconnected"
        if conn: conn.close()

        return {
            "database": db_status,
            "modules_loaded": [
                "publishers", "staff", "authors", "books",
                "orders", "payments", "categories", "customers", "reports"
            ]
        }


if __name__ == "__main__":
    backend = Backend()
    print("System Health Check:")
    print(backend.health_check())
