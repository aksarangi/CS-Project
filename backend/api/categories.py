# backend/api/categories.py

from backend.database.db_connection import get_connection
from backend.utils.helpers import safe_get, format_date
from backend.utils.logger import logger
from backend.models.category_model import CategoryModel


class CategoriesAPI:
    """
    Local API class to manage book categories.
    Provides CRUD + search functionality using CategoryModel.
    """

    def get_all(self):
        """
        Returns all categories
        """
        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in get_all()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT * FROM categories"
            cursor.execute(query)
            rows = cursor.fetchall()
            categories = [CategoryModel.from_db_row(row).to_dict() for row in rows]
            logger.info(f"Fetched {len(categories)} categories")
            return {"status": "success", "data": categories}

        except Exception as e:
            logger.error(f"Error fetching categories: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    def get_by_id(self, category_id):
        """
        Fetch a single category by category_id
        """
        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in get_by_id()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT * FROM categories WHERE category_id=%s"
            cursor.execute(query, (category_id,))
            row = cursor.fetchone()
            if row:
                category = CategoryModel.from_db_row(row)
                logger.info(f"Category fetched: {category_id}")
                return {"status": "success", "data": category.to_dict()}
            else:
                logger.warning(f"Category not found: {category_id}")
                return {"status": "error", "message": "Category not found"}

        except Exception as e:
            logger.error(f"Error fetching category by ID {category_id}: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    def add(self, category_data):
        """
        Add a new category
        Required: name
        Optional: description
        """
        name = safe_get(category_data, "name")
        if not name:
            return {"status": "error", "message": "name is required"}

        description = safe_get(category_data, "description")

        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in add()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor()
        try:
            query = "INSERT INTO categories (name, description) VALUES (%s, %s)"
            cursor.execute(query, (name, description))
            conn.commit()
            category_id = cursor.lastrowid
            logger.info(f"Category added: {category_id} - {name}")

            new_category = CategoryModel(
                category_id=category_id,
                name=name,
                description=description
            )
            return {"status": "success", "message": "Category added", "data": new_category.to_dict()}

        except Exception as e:
            logger.error(f"Error adding category: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    def update(self, category_id, category_data):
        """
        Update an existing category
        """
        if not category_data:
            return {"status": "error", "message": "No fields to update"}

        fields = ", ".join(f"{key}=%s" for key in category_data.keys())
        values = list(category_data.values())
        values.append(category_id)

        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in update()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor()
        try:
            query = f"UPDATE categories SET {fields} WHERE category_id=%s"
            cursor.execute(query, values)
            conn.commit()
            logger.info(f"Category updated: {category_id}")

            updated_category = self.get_by_id(category_id)
            return {"status": "success", "message": "Category updated", "data": updated_category.get("data")}

        except Exception as e:
            logger.error(f"Error updating category {category_id}: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    def delete(self, category_id):
        """
        Delete a category by ID
        """
        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in delete()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM categories WHERE category_id=%s", (category_id,))
            conn.commit()
            logger.info(f"Category deleted: {category_id}")
            return {"status": "success", "message": "Category deleted","data": f"{category_id}"}

        except Exception as e:
            logger.error(f"Error deleting category {category_id}: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()
