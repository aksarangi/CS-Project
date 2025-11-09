# backend/api/books.py

from database.db_connection import get_connection
from utils.helpers import safe_get, format_date, round_price
from utils.validators import is_positive_number, is_non_negative_integer, is_valid_isbn
from utils.logger import logger
from backend.models.book_model import BookModel


class BooksAPI:
    """
    Local API class to manage books.
    Provides CRUD + search functionality using BookModel.
    """

    def get_all(self, search=None, category_id=None, author_id=None, min_price=None, max_price=None):
        """
        Returns all books with optional filters.
        """
        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in get_all()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT * FROM books WHERE 1=1"
            params = []

            if search:
                query += " AND title LIKE %s"
                params.append(f"%{search}%")
            if category_id:
                query += " AND category_id=%s"
                params.append(category_id)
            if author_id:
                query += " AND author_id=%s"
                params.append(author_id)
            if min_price:
                query += " AND price >= %s"
                params.append(min_price)
            if max_price:
                query += " AND price <= %s"
                params.append(max_price)

            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            books = [BookModel.from_db_row(row).to_dict() for row in rows]

            logger.info(f"Fetched {len(books)} books from database")
            return {"status": "success", "data": books}

        except Exception as e:
            logger.error(f"Error fetching books: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    def get_by_id(self, book_id):
        """
        Fetch a single book by book_id
        """
        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in get_by_id()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT * FROM books WHERE book_id=%s"
            cursor.execute(query, (book_id,))
            row = cursor.fetchone()
            if row:
                book = BookModel.from_db_row(row)
                logger.info(f"Book fetched: {book_id}")
                return {"status": "success", "data": book.to_dict()}
            else:
                logger.warning(f"Book not found: {book_id}")
                return {"status": "error", "message": "Book not found"}

        except Exception as e:
            logger.error(f"Error fetching book by ID {book_id}: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    def add(self, book_data):
        """
        Add a new book using BookModel.
        Required: title, author_id, price
        Optional: publisher_id, category_id, language, isbn, publication_year, stock, description
        """
        title = safe_get(book_data, "title")
        author_id = safe_get(book_data, "author_id")
        price = safe_get(book_data, "price")

        if not title or not author_id or not is_positive_number(price):
            return {"status": "error", "message": "title, author_id and valid price are required"}

        publisher_id = safe_get(book_data, "publisher_id")
        category_id = safe_get(book_data, "category_id")
        language = safe_get(book_data, "language", "English")
        isbn = safe_get(book_data, "isbn")
        publication_year = safe_get(book_data, "publication_year")
        stock = safe_get(book_data, "stock", 0)
        description = safe_get(book_data, "description")

        if isbn and not is_valid_isbn(isbn):
            return {"status": "error", "message": "Invalid ISBN format"}
        if not is_non_negative_integer(stock):
            return {"status": "error", "message": "Stock must be a non-negative integer"}

        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in add()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor()
        try:
            query = """
                INSERT INTO books
                (title, author_id, publisher_id, category_id, language, isbn, publication_year, price, stock, description)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                title, author_id, publisher_id, category_id, language, isbn, publication_year, round_price(price), stock, description
            ))
            conn.commit()
            book_id = cursor.lastrowid
            logger.info(f"Book added: {book_id} - {title}")

            new_book = BookModel(
                book_id=book_id,
                title=title,
                author_id=author_id,
                publisher_id=publisher_id,
                category_id=category_id,
                language=language,
                isbn=isbn,
                publication_year=publication_year,
                price=round_price(price),
                stock=stock,
                description=description
            )
            return {"status": "success", "message": "Book added", "data": new_book.to_dict()}

        except Exception as e:
            logger.error(f"Error adding book: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    def update(self, book_id, book_data):
        """
        Update an existing book
        """
        if not book_data:
            return {"status": "error", "message": "No fields to update"}

        if "isbn" in book_data and book_data["isbn"] and not is_valid_isbn(book_data["isbn"]):
            return {"status": "error", "message": "Invalid ISBN format"}
        if "stock" in book_data and not is_non_negative_integer(book_data["stock"]):
            return {"status": "error", "message": "Stock must be a non-negative integer"}
        if "price" in book_data and not is_positive_number(book_data["price"]):
            return {"status": "error", "message": "Price must be positive"}

        if "price" in book_data:
            book_data["price"] = round_price(book_data["price"])

        fields = ", ".join(f"{key}=%s" for key in book_data.keys())
        values = list(book_data.values())
        values.append(book_id)

        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in update()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor()
        try:
            query = f"UPDATE books SET {fields} WHERE book_id=%s"
            cursor.execute(query, values)
            conn.commit()
            logger.info(f"Book updated: {book_id}")

            # Return updated model
            updated_book = self.get_by_id(book_id)
            return {"status": "success", "message": "Book updated", "data": updated_book.get("data")}

        except Exception as e:
            logger.error(f"Error updating book {book_id}: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    def delete(self, book_id):
        """
        Delete a book by ID
        """
        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in delete()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM books WHERE book_id=%s", (book_id,))
            conn.commit()
            logger.info(f"Book deleted: {book_id}")
            return {"status": "success", "message": "Book deleted"}

        except Exception as e:
            logger.error(f"Error deleting book {book_id}: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()
