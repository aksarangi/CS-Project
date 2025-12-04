# frontend/api_client.py
from backend.api import books, staff, authors, categories, publishers, customers, orders, payments, reports

# -----------------------------
# Helper to normalize API responses
# -----------------------------
def handle_response(func, *args, fields=None, **kwargs):
    """
    Call a backend API function.
    - Returns only 'data' if success, else None.
    - Filters fields if 'fields' is provided.
    """
    try:
        resp = func(*args, **kwargs)
        if resp.get("status") == "error":
            print(f"API error: {resp.get('message')}")
            return None
        data = resp.get("data")
        # Filter fields for UI
        if fields:
            if isinstance(data, list):
                data = [{k: v for k, v in item.items() if k in fields} for item in data]
            elif isinstance(data, dict):
                data = {k: v for k, v in data.items() if k in fields}
        return data
    except Exception as e:
        print(f"API exception: {e}")
        return None


# -----------------------------
# Staff / Authentication
# -----------------------------
class StaffClient:
    def __init__(self):
        self.api = staff.StaffAPI()
        self.fields = [
            "staff_id",
            "username",
            "full_name",
            "role",
            "email",
            "created_at"
        ]

    def get_all(self):
        return handle_response(self.api.get_all, fields=self.fields)

    def get_by_id(self, staff_id):
        return handle_response(self.api.get_by_id, staff_id, fields=self.fields)

    def add(self, staff_data):
        return handle_response(self.api.add, staff_data, fields=None)

    def update(self, staff_id, staff_data):
        return handle_response(self.api.update, staff_id, staff_data, fields=None)

    def delete(self, staff_id):
        return handle_response(self.api.delete, staff_id, fields=None)

    def authenticate(self, username, password):
        return handle_response(self.api.authenticate, username, password, fields=None)

    def search(self, by, query):
        return handle_response(self.api.search, by, query, fields=self.fields)


# -----------------------------
# Books
# -----------------------------
class BooksClient:
    def __init__(self):
        self.api = books.BookAPI()
        self.fields = ["book_id", "title", "description", "author", "publisher_name", "stock", "price", "genre"]

    def get_all(self):
        return handle_response(self.api.get_all, fields=self.fields)

    def get_by_id(self, book_id):
        fields = self.fields + ["description"]
        return handle_response(self.api.get_by_id, book_id, fields=fields)

    def search_by(self, field, query):
        return handle_response(self.api.search, field, query, fields=self.fields)
    # --- inside frontend/api_client.py, in BooksClient class ---

    def add(self, book_data):
        """
        book_data: dict with fields expected by backend (title, category_id, author_id, price, stock, publisher_id, description, isbn, etc.)
        Returns the created book dict on success, else None.
        """
        return handle_response(self.api.add, book_data, fields=None)  # return raw created object

    def update(self, book_id, book_data):
        """
        Update a book. Returns updated book dict on success, else None.
        """
        return handle_response(self.api.update, book_id, book_data, fields=None)

    def delete(self, book_id):
        """
        Delete a book. Returns True on success, None on failure.
        Backend per docs returns deleted id; handle_response will return that id (or None).
        We'll coerce to boolean in the view when needed.
        """
        res = handle_response(self.api.delete, book_id, fields=None)
        return res



# -----------------------------
# Authors
# -----------------------------
class AuthorsClient:
    def __init__(self):
        self.api = authors.AuthorsAPI()
        self.fields = ["author_id", "full_name", "country", "birth_year", "bio", "email"]

    def get_all(self):
        """Return list of authors (filtered to UI fields) or None."""
        return handle_response(self.api.get_all, fields=self.fields)

    def get_by_id(self, author_id):
        """Return single author dict or None."""
        return handle_response(self.api.get_by_id, author_id, fields=self.fields)
    
    def search_by(self, field, query):
        return handle_response(self.api.search, field, query, fields=self.fields)

    def add(self, author_data):
        """
        author_data example:
        { "full_name": "Vikram Seth", "country": "India", "birth_year": 1952, "bio": "...", "email": "..." }
        Returns created author dict on success, else None.
        """
        return handle_response(self.api.add, author_data, fields=None)

    def update(self, author_id, author_data):
        """Update an author; return updated dict on success, else None."""
        return handle_response(self.api.update, author_id, author_data, fields=None)

    def delete(self, author_id):
        """Delete author; return deleted id or None."""
        return handle_response(self.api.delete, author_id, fields=None)


# -----------------------------
# Categories
# -----------------------------
class CategoriesClient:
    def __init__(self):
        self.api = categories.CategoriesAPI()
        self.fields = ["category_id", "name", "description"]

    def get_all(self):
        return handle_response(self.api.get_all, fields=self.fields)

    def get_by_id(self, category_id):
        return handle_response(self.api.get_by_id, category_id, fields=self.fields)

    def add(self, category_data):
        return handle_response(self.api.add, category_data, fields=None)

    def update(self, category_id, category_data):
        return handle_response(self.api.update, category_id, category_data, fields=None)

    def delete(self, category_id):
        return handle_response(self.api.delete, category_id, fields=None)


# -----------------------------
# Publishers
# -----------------------------
class PublishersClient:
    def __init__(self):
        self.api = publishers.PublishersAPI()
        self.fields = ["publisher_id", "name", "location", "contact_email", "phone"]

    def get_all(self):
        """Return list of publishers (filtered fields) or None."""
        return handle_response(self.api.get_all, fields=self.fields)

    def get_by_id(self, publisher_id):
        """Return a single publisher dict or None."""
        return handle_response(self.api.get_by_id, publisher_id, fields=self.fields)

    def add(self, publisher_data):
        """
        publisher_data example:
        { "name": "Penguin", "location": "New York", "contact_email": "...", "phone": "..." }
        Returns created publisher dict on success, else None.
        """
        return handle_response(self.api.add, publisher_data, fields=None)

    def update(self, publisher_id, publisher_data):
        """Update a publisher; return updated dict on success, else None."""
        return handle_response(self.api.update, publisher_id, publisher_data, fields=None)

    def delete(self, publisher_id):
        """Delete publisher; return deleted id (or whatever backend returns) or None."""
        return handle_response(self.api.delete, publisher_id, fields=None)
    
    def search_by(self, field, query):
        return handle_response(self.api.search_by, field, query, fields=self.fields)


# -----------------------------
# Customers
# -----------------------------
class CustomersClient:
    def __init__(self):
        self.api = customers.CustomersAPI()
        self.fields = [
            "customer_id",
            "name",
            "email",
            "phone",
            "address",
            "joined_date"
        ]

    def get_all(self):
        return handle_response(self.api.get_all, fields=self.fields)

    def get_by_id(self, customer_id):
        return handle_response(self.api.get_by_id, customer_id, fields=self.fields)

    def add(self, customer_data):
        return handle_response(self.api.add, customer_data, fields=None)

    def update(self, customer_id, customer_data):
        return handle_response(self.api.update, customer_id, customer_data, fields=None)

    def delete(self, customer_id):
        return handle_response(self.api.delete, customer_id, fields=None)


# -----------------------------
# Orders
# -----------------------------
class OrdersClient:
    def __init__(self):
        self.api = orders.OrdersAPI()
        self.fields = ["order_id", "customer_id", "total_amount", "order_status"]

    def get_all(self):
        return handle_response(self.api.get_all, fields=self.fields)

    def get_by_id(self, order_id):
        return handle_response(self.api.get_by_id, order_id, fields=self.fields)

    def search(self, by, query):
        return handle_response(self.api.search, by, query, fields=self.fields)


# -----------------------------
# Payments
# -----------------------------
class PaymentsClient:
    def __init__(self):
        self.api = payments.PaymentsAPI()
        self.fields = ["payment_id", "order_id", "amount", "payment_method", "payment_status", "transaction_id"]

    def search(self, field=None, value=None):
        return handle_response(self.api.search, field, value, fields=self.fields)

    def add(self, payment_data):
        return handle_response(self.api.add, payment_data, fields=self.fields)

    def update_status(self, payment_id, status):
        return handle_response(self.api.update_status, payment_id, status, fields=self.fields)


# -----------------------------
# Users
# -----------------------------
class UsersClient:
    def __init__(self):
        self.api = staff.StaffAPI()

    def get_profile(self, username):
        return handle_response(self.api.get_profile, full_name=username)

    def update_profile(self, user_id, fields):
        return handle_response(self.api.update_profile, user_id, fields)

    def change_password(self, user_id, old, new):
        return handle_response(self.api.change_password, user_id, old, new)


# -----------------------------
# Reports
# -----------------------------
class ReportsClient:
    """
    Handles all analytics + stock reports.
    """

    def __init__(self):
        self.api = reports.ReportsAPI()

    def get_current_stock(self):
        # returns list of {book_id, title, author, publisher, stock, price, ...}
        return handle_response(self.api.get_current_stock, fields=None)

    def get_low_stock(self, threshold=10):
        return handle_response(self.api.get_low_stock, threshold, fields=None)

    def get_top_books(self):
        return handle_response(self.api.get_top_selling_books, fields=None)
    
    def get_summary(self):
        return handle_response(self.api.get_category_stock_summary, fields=None)

    def get_total_sales(self, date=None):
        return handle_response(self.api.get_daily_sales_plot_data, date, fields=None)

    def get_daily_sales_report(self, date=None):
        return handle_response(self.api.get_daily_sales, date, fields=None)


# -----------------------------
# Sales
# -----------------------------
class SalesClient:
    def __init__(self):
        self.api = reports.ReportsAPI()

    def get_recent_sales(self):
        return handle_response(self.api.get_daily_sales, fields=None)
