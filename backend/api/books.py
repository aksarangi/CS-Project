# backend/api/books.py

from backend.database.db_connection import get_connection
from backend.models.book_model import BookModel
from backend.utils.helpers import safe_get, round_price
from backend.utils.validators import (
    is_positive_number,
    is_non_negative_integer,
    is_valid_isbn
)
from backend.utils.logger import logger


class BookAPI:
    """
    Local API for managing books in the Bookshop Management System.
    Handles CRUD operations + dynamic search.
    """

    # -------------------------------------------------------------
    # GET ALL BOOKS
    # -------------------------------------------------------------
    def get_all(self):
        conn = get_connection()
        if not conn:
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    b.*, 
                    a.full_name AS author_name,
                    p.name AS publisher_name,
                    c.name AS genre
                FROM books b
                LEFT JOIN authors a ON b.author_id = a.author_id
                LEFT JOIN publishers p ON b.publisher_id = p.publisher_id
                LEFT JOIN categories c ON b.category_id = c.category_id
            """)

            rows = cursor.fetchall()
            books = [BookModel.from_db_row(r).to_dict() for r in rows]
            return {"status": "success", "data": books}

        except Exception as e:
            logger.error(f"Error fetching books: {e}")
            return {"status": "error", "message": str(e)}

        finally:
            cursor.close()
            conn.close()

    # -------------------------------------------------------------
    # GET BOOK BY ID
    # -------------------------------------------------------------
    def get_by_id(self, book_id):
        conn = get_connection()
        if not conn:
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    b.*, 
                    a.full_name AS author_name,
                    p.name AS publisher_name,
                    c.name AS genre
                FROM books b
                LEFT JOIN authors a ON b.author_id = a.author_id
                LEFT JOIN publishers p ON b.publisher_id = p.publisher_id
                LEFT JOIN categories c ON b.category_id = c.category_id
                WHERE b.book_id=%s
            """, (book_id,))

            row = cursor.fetchone()
            if not row:
                return {"status": "error", "message": "Book not found"}

            return {"status": "success", "data": BookModel.from_db_row(row).to_dict()}

        except Exception as e:
            logger.error(f"Error fetching book {book_id}: {e}")
            return {"status": "error", "message": str(e)}

        finally:
            cursor.close()
            conn.close()

    # -------------------------------------------------------------
    # ADD NEW BOOK
    # -------------------------------------------------------------
    def add(self, book_data):
        title = safe_get(book_data, "title")
        author_id = safe_get(book_data, "author_id")
        publisher_id = safe_get(book_data, "publisher_id")
        category_id = safe_get(book_data, "category_id")  # correct field
        price = safe_get(book_data, "price")

        if not title or not author_id or not publisher_id or not category_id:
            return {"status": "error", "message": "Missing required fields"}

        if not is_positive_number(price):
            return {"status": "error", "message": "Invalid price"}

        isbn = safe_get(book_data, "isbn")
        publication_year = safe_get(book_data, "publication_year")
        language = safe_get(book_data, "language", "English")
        stock = safe_get(book_data, "stock", 0)
        description = safe_get(book_data, "description", "")

        if isbn and not is_valid_isbn(isbn):
            return {"status": "error", "message": "Invalid ISBN"}

        if not is_non_negative_integer(stock):
            return {"status": "error", "message": "Invalid stock amount"}

        conn = get_connection()
        if not conn:
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO books 
                (title, isbn, author_id, publisher_id, category_id, publication_year, language, price, stock, description)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                title, isbn, author_id, publisher_id, category_id,
                publication_year, language, round_price(price), stock, description
            ))

            conn.commit()
            book_id = cursor.lastrowid

            return self.get_by_id(book_id)

        except Exception as e:
            logger.error(f"Error adding book: {e}")
            return {"status": "error", "message": str(e)}

        finally:
            cursor.close()
            conn.close()

    # -------------------------------------------------------------
    # UPDATE BOOK
    # -------------------------------------------------------------
    def update(self, book_id, book_data):
        if not book_data:
            return {"status": "error", "message": "No update fields"}

        if "isbn" in book_data and book_data["isbn"] and not is_valid_isbn(book_data["isbn"]):
            return {"status": "error", "message": "Invalid ISBN"}

        if "stock" in book_data and not is_non_negative_integer(book_data["stock"]):
            return {"status": "error", "message": "Invalid stock"}

        if "price" in book_data and not is_positive_number(book_data["price"]):
            return {"status": "error", "message": "Invalid price"}

        if "price" in book_data:
            book_data["price"] = round_price(book_data["price"])

        fields = ", ".join(f"{key}=%s" for key in book_data.keys())
        values = list(book_data.values()) + [book_id]

        conn = get_connection()
        if not conn:
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor()
        try:
            cursor.execute(f"UPDATE books SET {fields} WHERE book_id=%s", values)
            conn.commit()

            return self.get_by_id(book_id)

        except Exception as e:
            logger.error(f"Error updating {book_id}: {e}")
            return {"status": "error", "message": str(e)}

        finally:
            cursor.close()
            conn.close()

    # -------------------------------------------------------------
    # DELETE BOOK
    # -------------------------------------------------------------
    def delete(self, book_id):
        conn = get_connection()
        if not conn:
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM books WHERE book_id=%s", (book_id,))
            conn.commit()

            return {"status": "success", "message": "Book deleted"}

        except Exception as e:
            logger.error(f"Error deleting book {book_id}: {e}")
            return {"status": "error", "message": str(e)}

        finally:
            cursor.close()
            conn.close()

    # -------------------------------------------------------------
    # SEARCH
    # -------------------------------------------------------------
    def search(self, field=None, query=None):
        FIELD_MAP = {
            # Books table
            "title": "b.title",
            "isbn": "b.isbn",
            "language": "b.language",
            "price": "b.price",
            "description": "b.description",
            "publication_year": "b.publication_year",

            # Author
            "author": "a.full_name",
            "country": "a.country",

            # Publisher
            "publisher_name": "p.name",
            "location": "p.location",

            # Category
            "genre": "c.name",
            "category": "c.name",
            "category_name": "c.name"
        }

        conn = get_connection()
        if not conn:
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor(dictionary=True)

        try:
            base_sql = """
                SELECT 
                    b.*, 
                    a.full_name AS author_name,
                    p.name AS publisher_name,
                    c.name AS genre
                FROM books b
                JOIN authors a ON b.author_id = a.author_id
                JOIN publishers p ON b.publisher_id = p.publisher_id
                JOIN categories c ON b.category_id = c.category_id
            """

            # No query → return all
            if not query:
                cursor.execute(base_sql)
                rows = cursor.fetchall()
                return {"status": "success", "data": [BookModel.from_db_row(r).to_dict() for r in rows]}

            params = []
            where_clauses = []

            if field:
                if field not in FIELD_MAP:
                    return {"status": "error", "message": f"Invalid search field '{field}'"}

                col = FIELD_MAP[field]
                where_clauses.append(f"{col} LIKE %s")
                params.append(f"%{query}%")

            else:
                SEARCHABLE = [
                    "b.title", "b.isbn", "b.language", "b.description",
                    "a.full_name", "p.name", "c.name"
                ]

                for col in SEARCHABLE:
                    where_clauses.append(f"{col} LIKE %s")
                    params.append(f"%{query}%")

            final_sql = base_sql + " WHERE " + " OR ".join(f"({w})" for w in where_clauses)

            cursor.execute(final_sql, params)
            rows = cursor.fetchall()

            return {"status": "success", "data": [BookModel.from_db_row(r).to_dict() for r in rows]}

        except Exception as e:
            logger.error(f"Search error: {e}")
            return {"status": "error", "message": str(e)}

        finally:
            cursor.close()
            conn.close()
# backend/api/books.py

from backend.database.db_connection import get_connection
from backend.models.book_model import BookModel
from backend.utils.helpers import safe_get, round_price
from backend.utils.validators import (
    is_positive_number,
    is_non_negative_integer,
    is_valid_isbn
)
from backend.utils.logger import logger


class BookAPI:
    """
    Local API for managing books in the Bookshop Management System.
    Handles CRUD operations + dynamic search.
    """

    # -------------------------------------------------------------
    # GET ALL BOOKS
    # -------------------------------------------------------------
    def get_all(self):
        conn = get_connection()
        if not conn:
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    b.*, 
                    a.full_name AS author_name,
                    p.name AS publisher_name,
                    c.name AS genre
                FROM books b
                LEFT JOIN authors a ON b.author_id = a.author_id
                LEFT JOIN publishers p ON b.publisher_id = p.publisher_id
                LEFT JOIN categories c ON b.category_id = c.category_id
            """)

            rows = cursor.fetchall()
            books = [BookModel.from_db_row(r).to_dict() for r in rows]
            return {"status": "success", "data": books}

        except Exception as e:
            logger.error(f"Error fetching books: {e}")
            return {"status": "error", "message": str(e)}

        finally:
            cursor.close()
            conn.close()

    # -------------------------------------------------------------
    # GET BOOK BY ID
    # -------------------------------------------------------------
    def get_by_id(self, book_id):
        conn = get_connection()
        if not conn:
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    b.*, 
                    a.full_name AS author_name,
                    p.name AS publisher_name,
                    c.name AS genre
                FROM books b
                LEFT JOIN authors a ON b.author_id = a.author_id
                LEFT JOIN publishers p ON b.publisher_id = p.publisher_id
                LEFT JOIN categories c ON b.category_id = c.category_id
                WHERE b.book_id=%s
            """, (book_id,))

            row = cursor.fetchone()
            if not row:
                return {"status": "error", "message": "Book not found"}

            return {"status": "success", "data": BookModel.from_db_row(row).to_dict()}

        except Exception as e:
            logger.error(f"Error fetching book {book_id}: {e}")
            return {"status": "error", "message": str(e)}

        finally:
            cursor.close()
            conn.close()

    # -------------------------------------------------------------
    # ADD NEW BOOK
    # -------------------------------------------------------------
    def add(self, book_data):
        title = safe_get(book_data, "title")
        author_id = safe_get(book_data, "author_id")
        publisher_id = safe_get(book_data, "publisher_id")
        category_id = safe_get(book_data, "category_id")  # correct field
        price = safe_get(book_data, "price")

        if not title or not author_id or not publisher_id or not category_id:
            return {"status": "error", "message": "Missing required fields"}

        if not is_positive_number(price):
            return {"status": "error", "message": "Invalid price"}

        isbn = safe_get(book_data, "isbn")
        publication_year = safe_get(book_data, "publication_year")
        language = safe_get(book_data, "language", "English")
        stock = safe_get(book_data, "stock", 0)
        description = safe_get(book_data, "description", "")

        if isbn and not is_valid_isbn(isbn):
            return {"status": "error", "message": "Invalid ISBN"}

        if not is_non_negative_integer(stock):
            return {"status": "error", "message": "Invalid stock amount"}

        conn = get_connection()
        if not conn:
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO books 
                (title, isbn, author_id, publisher_id, category_id, publication_year, language, price, stock, description)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                title, isbn, author_id, publisher_id, category_id,
                publication_year, language, round_price(price), stock, description
            ))

            conn.commit()
            book_id = cursor.lastrowid

            return self.get_by_id(book_id)

        except Exception as e:
            logger.error(f"Error adding book: {e}")
            return {"status": "error", "message": str(e)}

        finally:
            cursor.close()
            conn.close()

    # -------------------------------------------------------------
    # UPDATE BOOK
    # -------------------------------------------------------------
    def update(self, book_id, book_data):
        if not book_data:
            return {"status": "error", "message": "No update fields"}

        if "isbn" in book_data and book_data["isbn"] and not is_valid_isbn(book_data["isbn"]):
            return {"status": "error", "message": "Invalid ISBN"}

        if "stock" in book_data and not is_non_negative_integer(book_data["stock"]):
            return {"status": "error", "message": "Invalid stock"}

        if "price" in book_data and not is_positive_number(book_data["price"]):
            return {"status": "error", "message": "Invalid price"}

        if "price" in book_data:
            book_data["price"] = round_price(book_data["price"])

        fields = ", ".join(f"{key}=%s" for key in book_data.keys())
        values = list(book_data.values()) + [book_id]

        conn = get_connection()
        if not conn:
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor()
        try:
            cursor.execute(f"UPDATE books SET {fields} WHERE book_id=%s", values)
            conn.commit()

            return self.get_by_id(book_id)

        except Exception as e:
            logger.error(f"Error updating {book_id}: {e}")
            return {"status": "error", "message": str(e)}

        finally:
            cursor.close()
            conn.close()

    # -------------------------------------------------------------
    # DELETE BOOK
    # -------------------------------------------------------------
    def delete(self, book_id):
        conn = get_connection()
        if not conn:
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM books WHERE book_id=%s", (book_id,))
            conn.commit()

            return {"status": "success", "message": "Book deleted"}

        except Exception as e:
            logger.error(f"Error deleting book {book_id}: {e}")
            return {"status": "error", "message": str(e)}

        finally:
            cursor.close()
            conn.close()

    # -------------------------------------------------------------
    # SEARCH
    # -------------------------------------------------------------
    def search(self, field=None, query=None):
        FIELD_MAP = {
            # Books table
            "title": "b.title",
            "isbn": "b.isbn",
            "language": "b.language",
            "price": "b.price",
            "description": "b.description",
            "publication_year": "b.publication_year",

            # Author
            "author": "a.full_name",
            "country": "a.country",

            # Publisher
            "publisher_name": "p.name",
            "location": "p.location",

            # Category
            "genre": "c.name",
            "category": "c.name",
            "category_name": "c.name"
        }

        conn = get_connection()
        if not conn:
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor(dictionary=True)

        try:
            base_sql = """
                SELECT 
                    b.*, 
                    a.full_name AS author_name,
                    p.name AS publisher_name,
                    c.name AS genre
                FROM books b
                LEFT JOIN authors a ON b.author_id = a.author_id
                LEFT JOIN publishers p ON b.publisher_id = p.publisher_id
                LEFT JOIN categories c ON b.category_id = c.category_id
            """

            # No query → return all
            if not query:
                cursor.execute(base_sql)
                rows = cursor.fetchall()
                return {"status": "success", "data": [BookModel.from_db_row(r).to_dict() for r in rows]}

            params = []
            where_clauses = []

            if field:
                if field not in FIELD_MAP:
                    return {"status": "error", "message": f"Invalid search field '{field}'"}

                col = FIELD_MAP[field]
                where_clauses.append(f"{col} LIKE %s")
                params.append(f"%{query}%")

            else:
                SEARCHABLE = [
                    "b.title", "b.isbn", "b.language", "b.description",
                    "a.full_name", "p.name", "c.name"
                ]

                for col in SEARCHABLE:
                    where_clauses.append(f"{col} LIKE %s")
                    params.append(f"%{query}%")

            final_sql = base_sql + " WHERE (" + " OR ".join(f"({w})" for w in where_clauses) + ")"

            cursor.execute(final_sql, params)
            rows = cursor.fetchall()
            print(len(rows))
            results = [BookModel.from_db_row(r).to_dict() for r in rows]
            logger.info(f"Search by {field}: '{query}' → {len(results)} results")
            return {"status": "success", "message":"Search results", "data": results}

        except Exception as e:
            logger.error(f"Search error: {e}")
            return {"status": "error", "message": str(e)}

        finally:
            cursor.close()
            conn.close()
