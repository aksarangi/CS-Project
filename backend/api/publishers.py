from database.db_connection import get_connection
from models.book_model import BookModel
from utils.helpers import safe_get, format_date, round_price
from utils.validators import is_positive_number, is_non_negative_integer, is_valid_isbn
from utils.logger import logger


class BookAPI:
    """
    Local API for managing books in the Bookshop Management System.
    Handles CRUD operations + dynamic search.
    """

    def get_all(self):
        """
        Retrieve all books with author and publisher info.
        """
        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in get_all()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT b.*, a.full_name AS author_name, p.name AS publisher_name
                FROM books b
                LEFT JOIN authors a ON b.author_id = a.author_id
                LEFT JOIN publishers p ON b.publisher_id = p.publisher_id
            """)
            rows = cursor.fetchall()
            books = [BookModel.from_db_row(row).to_dict() for row in rows]
            logger.info(f"Fetched {len(books)} books")
            return {"status": "success", "data": books}
        except Exception as e:
            logger.error(f"Error fetching books: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    def get_by_id(self, book_id):
        """
        Retrieve a specific book by ID.
        """
        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in get_by_id()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT b.*, a.full_name AS author_name, p.name AS publisher_name
                FROM books b
                LEFT JOIN authors a ON b.author_id = a.author_id
                LEFT JOIN publishers p ON b.publisher_id = p.publisher_id
                WHERE b.book_id=%s
            """, (book_id,))
            row = cursor.fetchone()
            if not row:
                return {"status": "error", "message": "Book not found"}

            book = BookModel.from_db_row(row).to_dict()
            logger.info(f"Book fetched: {book_id}")
            return {"status": "success", "data": book}
        except Exception as e:
            logger.error(f"Error fetching book {book_id}: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    def add(self, book_data):
        """
        Add a new book.
        Required: title, author_id, publisher_id, price
        Optional: isbn, genre, publication_year, language, stock
        """
        title = safe_get(book_data, "title")
        author_id = safe_get(book_data, "author_id")
        publisher_id = safe_get(book_data, "publisher_id")
        price = safe_get(book_data, "price")

        if not title or not author_id or not publisher_id or not is_positive_number(price):
            return {"status": "error", "message": "title, author_id, publisher_id and valid price are required"}

        isbn = safe_get(book_data, "isbn")
        genre = safe_get(book_data, "genre")
        publication_year = safe_get(book_data, "publication_year")
        language = safe_get(book_data, "language", "English")
        stock = safe_get(book_data, "stock", 0)

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
            cursor.execute("""
                INSERT INTO books (title, isbn, author_id, publisher_id, genre, publication_year, language, price, stock)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                title, isbn, author_id, publisher_id, genre,
                publication_year, language, round_price(price), stock
            ))
            conn.commit()
            book_id = cursor.lastrowid
            logger.info(f"Book added: {book_id} - {title}")
            return {"status": "success", "message": "Book added", "book_id": book_id}
        except Exception as e:
            logger.error(f"Error adding book: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    def update(self, book_id, book_data):
        """
        Update a book record by ID.
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
            return {"status": "success", "message": "Book updated"}
        except Exception as e:
            logger.error(f"Error updating book {book_id}: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    def delete(self, book_id):
        """
        Delete a book by ID.
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

    def search(self, field=None, query=None):
        """
        Dynamically search books by any valid field or related entity.
        Example:
            search('title', 'Python') → books with 'Python' in title
            search('isbn', '978') → books with matching ISBN
            search(None, 'Tolkien') → all books where author/publisher contains 'Tolkien'
            search(None, None) → all books
        """
        valid_fields = ["title", "isbn", "genre", "language", "publication_year"]
        if field is not None and field not in valid_fields:
            return {"status": "error", "message": f"Invalid search field '{field}'"}

        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in search()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor(dictionary=True)
        try:
            if field and query:
                if field == "publication_year":
                    sql = f"""
                        SELECT b.*, a.full_name AS author_name, p.name AS publisher_name
                        FROM books b
                        LEFT JOIN authors a ON b.author_id = a.author_id
                        LEFT JOIN publishers p ON b.publisher_id = p.publisher_id
                        WHERE b.{field} = %s
                    """
                    cursor.execute(sql, (query,))
                else:
                    sql = f"""
                        SELECT b.*, a.full_name AS author_name, p.name AS publisher_name
                        FROM books b
                        LEFT JOIN authors a ON b.author_id = a.author_id
                        LEFT JOIN publishers p ON b.publisher_id = p.publisher_id
                        WHERE b.{field} LIKE %s
                    """
                    cursor.execute(sql, (f"%{query}%",))
            elif query:
                sql = """
                    SELECT b.*, a.full_name AS author_name, p.name AS publisher_name
                    FROM books b
                    LEFT JOIN authors a ON b.author_id = a.author_id
                    LEFT JOIN publishers p ON b.publisher_id = p.publisher_id
                    WHERE b.title LIKE %s
                    OR b.genre LIKE %s
                    OR b.language LIKE %s
                    OR b.isbn LIKE %s
                    OR a.full_name LIKE %s
                    OR p.name LIKE %s
                """
                like = f"%{query}%"
                cursor.execute(sql, (like, like, like, like, like, like))
            else:
                sql = """
                    SELECT b.*, a.full_name AS author_name, p.name AS publisher_name
                    FROM books b
                    LEFT JOIN authors a ON b.author_id = a.author_id
                    LEFT JOIN publishers p ON b.publisher_id = p.publisher_id
                """
                cursor.execute(sql)

            rows = cursor.fetchall()
            books = [BookModel.from_db_row(r).to_dict() for r in rows]
            logger.info(f"Search returned {len(books)} books (field={field}, query={query})")
            return {"status": "success", "data": books}
        except Exception as e:
            logger.error(f"Error searching books: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()
