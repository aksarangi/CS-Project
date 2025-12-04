# backend/api/authors.py

from backend.database.db_connection import get_connection
from backend.utils.helpers import safe_get, format_date
from backend.utils.validators import is_valid_email
from backend.utils.logger import logger
from backend.models.author_model import AuthorModel


class AuthorsAPI:
    """
    Local API class to manage authors.
    Provides CRUD + search functionality using AuthorModel.
    """

    def get_all(self):
        """
        Returns all authors. Optionally filter by search string in name or country.
        """
        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in get_all()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT * FROM authors"
            cursor.execute(query)

            authors_rows = cursor.fetchall()
            authors = [AuthorModel.from_db_row(row).to_dict() for row in authors_rows]

            logger.info(f"Fetched {len(authors)} authors from database")
            return {"status": "success","message":"Fetched all authors", "data": authors}

        except Exception as e:
            logger.error(f"Error fetching authors: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    def get_by_id(self, author_id):
        """
        Fetch a single author by author_id
        """
        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in get_by_id()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT * FROM authors WHERE author_id=%s"
            cursor.execute(query, (author_id,))
            row = cursor.fetchone()
            if row:
                author = AuthorModel.from_db_row(row)
                logger.info(f"Author fetched: {author_id}")
                return {"status": "success", "message":"Fetched author by id", "data": author.to_dict()}
            else:
                logger.warning(f"Author not found: {author_id}")
                return {"status": "error", "message": "Author not found"}

        except Exception as e:
            logger.error(f"Error fetching author by ID {author_id}: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    def add(self, author_data):
        """
        Add a new author using AuthorModel.
        Required: full_name
        Optional: country, birth_year, death_year, bio
        """
        full_name = safe_get(author_data, "full_name")
        if not full_name:
            return {"status": "error", "message": "full_name is required"}

        country = safe_get(author_data, "country", "India")
        birth_year = safe_get(author_data, "birth_year")
        death_year = safe_get(author_data, "death_year")
        bio = safe_get(author_data, "bio")

        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in add()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor()
        try:
            query = """
                INSERT INTO authors (full_name, country, birth_year, death_year, bio)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (full_name, country, birth_year, death_year, bio))
            conn.commit()

            author_id = cursor.lastrowid
            logger.info(f"Author added: {author_id} - {full_name}")

            # Return the newly created AuthorModel instance
            new_author = AuthorModel(
                author_id=author_id,
                full_name=full_name,
                country=country,
                birth_year=birth_year,
                death_year=death_year,
                bio=bio
            )
            return {"status": "success", "message": "Author added", "data": new_author.to_dict()}

        except Exception as e:
            logger.error(f"Error adding author: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    def update(self, author_id, author_data):
        """
        Update an existing author.
        """
        if not author_data:
            return {"status": "error", "message": "No fields to update"}

        fields = ", ".join(f"{key}=%s" for key in author_data.keys())
        values = list(author_data.values())
        values.append(author_id)

        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in update()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor()
        try:
            query = f"UPDATE authors SET {fields} WHERE author_id=%s"
            cursor.execute(query, values)
            conn.commit()
            logger.info(f"Author updated: {author_id}")

            # Return updated author instance
            updated_author = self.get_by_id(author_id)
            return {"status": "success", "message": "Author updated", "data": updated_author.get("data")}

        except Exception as e:
            logger.error(f"Error updating author {author_id}: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    def delete(self, author_id):
        """
        Delete an author by ID.
        """
        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in delete()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM authors WHERE author_id=%s", (author_id,))
            conn.commit()
            logger.info(f"Author deleted: {author_id}")
            return {"status": "success", "message": "Author deleted", "data": author_id}

        except Exception as e:
            logger.error(f"Error deleting author {author_id}: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    def search(self, field=None, query=None):
        """
        Dynamically search authors by any valid field.

        Examples:
            search('country', 'India') → all Indian authors
            search('full_name', 'Vikram') → authors with 'Vikram' in name
            search(None, None) → all authors
        """
        valid_fields = ["full_name", "country", "birth_year", "death_year", "bio"]

        # Validate the field to prevent SQL injection
        if field is not None and field not in valid_fields:
            return {"status": "error", "message": f"Invalid search field '{field}'"}

        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in search()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor(dictionary=True)
        try:
            if field and query:
                # Special case: numeric fields (year-based) should not use LIKE
                if field in ["birth_year", "death_year"]:
                    sql = f"SELECT * FROM authors WHERE {field} = %s"
                    cursor.execute(sql, (query,))
                else:
                    sql = f"SELECT * FROM authors WHERE {field} LIKE %s"
                    cursor.execute(sql, (f"%{query}%",))
            elif query:
                # Universal search if only query provided (search across all text fields)
                sql = """
                    SELECT * FROM authors
                    WHERE full_name LIKE %s
                    OR country LIKE %s
                    OR bio LIKE %s
                """
                like_value = f"%{query}%"
                cursor.execute(sql, (like_value, like_value, like_value))
            else:
                # No field and no query → return all
                sql = "SELECT * FROM authors"
                cursor.execute(sql)

            rows = cursor.fetchall()
            authors = [AuthorModel.from_db_row(row).to_dict() for row in rows]
            logger.info(f"Search returned {len(authors)} authors (field={field}, query={query})")

            return {"status": "success","message": "search results", "data": authors}

        except Exception as e:
            logger.error(f"Error searching authors: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()
