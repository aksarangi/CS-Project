# backend/api/publishers.py

from backend.database.db_connection import get_connection
from backend.utils.helpers import safe_get
from backend.utils.logger import logger
from backend.models.publisher_model import PublisherModel


class PublishersAPI:
    """
    Local API class to manage publishers using PublisherModel.
    Provides CRUD + dynamic search functionality.
    """

    def get_all(self):
        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in get_all()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT * FROM publishers"
            cursor.execute(query)
            rows = cursor.fetchall()
            publishers = [PublisherModel.from_db_row(row).to_dict() for row in rows]
            logger.info(f"Fetched {len(publishers)} publishers")
            return {"status": "success","message":"Fetched all publishers", "data": publishers}
        except Exception as e:
            logger.error(f"Error fetching publishers: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    def get_by_id(self, publisher_id):
        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in get_by_id()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM publishers WHERE publisher_id=%s", (publisher_id,))
            row = cursor.fetchone()
            if row:
                publisher = PublisherModel.from_db_row(row).to_dict()
                logger.info(f"Publisher fetched: {publisher_id}")
                return {"status": "success","message":"Fetched Publisher by id", "data": publisher}
            else:
                logger.warning(f"Publisher not found: {publisher_id}")
                return {"status": "error", "message": "Publisher not found"}
        except Exception as e:
            logger.error(f"Error fetching publisher by ID {publisher_id}: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    def add(self, publisher_data):
        name = safe_get(publisher_data, "name")
        if not name:
            return {"status": "error", "message": "name is required"}

        location = safe_get(publisher_data, "location")
        contact_email = safe_get(publisher_data, "contact_email")
        phone = safe_get(publisher_data, "phone")

        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in add()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor()
        try:
            query = "INSERT INTO publishers (name, location, contact_email, phone) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (name, location, contact_email, phone))
            conn.commit()
            publisher_id = cursor.lastrowid
            publisher = PublisherModel(
                publisher_id=publisher_id,
                name=name,
                location=location,
                contact_email=contact_email,
                phone=phone
            ).to_dict()
            logger.info(f"Publisher added: {publisher_id} - {name}")
            return {"status": "success", "message": "Publisher added", "data": publisher}
        except Exception as e:
            logger.error(f"Error adding publisher: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    def update(self, publisher_id, publisher_data):
        if not publisher_data:
            return {"status": "error", "message": "No fields to update"}

        fields = ", ".join(f"{key}=%s" for key in publisher_data.keys())
        values = list(publisher_data.values())
        values.append(publisher_id)

        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in update()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor(dictionary=True)
        try:
            query = f"UPDATE publishers SET {fields} WHERE publisher_id=%s"
            cursor.execute(query, values)
            conn.commit()

            updated=self.get_by_id(publisher_id)  # Refresh data
            row = updated.get("data")
            publisher = PublisherModel.from_db_row(row).to_dict() if row else None

            logger.info(f"Publisher updated: {publisher_id}")
            return {"status": "success", "message": "Publisher updated", "data": publisher}
        except Exception as e:
            logger.error(f"Error updating publisher {publisher_id}: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    def delete(self, publisher_id):
        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in delete()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM publishers WHERE publisher_id=%s", (publisher_id,))
            conn.commit()
            logger.info(f"Publisher deleted: {publisher_id}")
            return {"status": "success", "message": "Publisher deleted", "data": publisher_id}
        except Exception as e:
            logger.error(f"Error deleting publisher {publisher_id}: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    def search_by(self, field, query):
        """
        Dynamically search publishers by any valid field.
        field: column name (e.g. 'name', 'location', 'contact_email', 'phone')
        query: search text or partial match
        """
        valid_fields = {"name", "location", "contact_email", "phone"}
        if field not in valid_fields:
            return {"status": "error", "message": f"Invalid field '{field}'"}

        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in search_by()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor(dictionary=True)
        try:
            sql = f"SELECT * FROM publishers WHERE {field} LIKE %s"
            cursor.execute(sql, (f"%{query}%",))
            rows = cursor.fetchall()
            results = [PublisherModel.from_db_row(row).to_dict() for row in rows]
            logger.info(f"Search by {field}: '{query}' → {len(results)} results")
            return {"status": "success","message":"Search results", "data": results}
        except Exception as e:
            logger.error(f"Error in dynamic search: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()
