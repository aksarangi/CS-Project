# backend/api/staff.py

from backend.database.db_connection import get_connection
from backend.utils.helpers import safe_get
from backend.utils.validators import is_non_empty_string
from backend.utils.logger import logger
import bcrypt
from backend.models.staff_model import StaffModel


class StaffAPI:
    """
    Local API class to manage staff/admin users using StaffModel.
    Provides CRUD + authentication + role management + search.
    """

    def get_all(self):
        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in get_all()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT staff_id, username, full_name, role, email, created_at FROM staff WHERE 1=1"
            cursor.execute(query)
            rows = cursor.fetchall()
            staff_list = [StaffModel.from_db_row(row).to_dict() for row in rows]
            logger.info(f"Fetched {len(staff_list)} staff users")
            return {"status": "success","message":"Fetched all staff data", "data": staff_list}
        except Exception as e:
            logger.error(f"Error fetching staff: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    def get_by_id(self, staff_id):
        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in get_by_id()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT staff_id, username, full_name, role, email, created_at FROM staff WHERE staff_id=%s", (staff_id,))
            row = cursor.fetchone()
            if row:
                staff = StaffModel.from_db_row(row).to_dict()
                logger.info(f"Staff fetched: {staff_id}")
                return {"status": "success","message":"Fetched staff data by id", "data": staff}
            else:
                logger.warning(f"Staff not found: {staff_id}")
                return {"status": "error", "message": "Staff not found"}
        except Exception as e:
            logger.error(f"Error fetching staff {staff_id}: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    def add(self, staff_data):
        username = safe_get(staff_data, "username")
        password = safe_get(staff_data, "password")
        role = safe_get(staff_data, "role", "Clerk")
        full_name = safe_get(staff_data, "full_name")
        email = safe_get(staff_data, "email")

        if not is_non_empty_string(username) or not is_non_empty_string(password):
            return {"status": "error", "message": "username and password are required"}

        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in add()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO staff (username, password_hash, full_name, role, email)
                VALUES (%s, %s, %s, %s, %s)
            """, (username, password_hash, full_name, role, email))
            conn.commit()
            staff_id = cursor.lastrowid
            staff = StaffModel(
                staff_id=staff_id, username=username, password_hash=password_hash,
                full_name=full_name, role=role, email=email
            ).to_dict()
            logger.info(f"Staff added: {staff_id} - {username}")
            return {"status": "success", "message": "Staff added", "data": staff}
        except Exception as e:
            logger.error(f"Error adding staff: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    def update(self, staff_id, staff_data):
        if not staff_data:
            return {"status": "error", "message": "No fields to update"}

        if "password" in staff_data:
            staff_data["password_hash"] = bcrypt.hashpw(staff_data["password"].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            del staff_data["password"]

        fields = ", ".join(f"{key}=%s" for key in staff_data.keys())
        values = list(staff_data.values())
        values.append(staff_id)

        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in update()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor()
        try:
            query = f"UPDATE staff SET {fields} WHERE staff_id=%s"
            cursor.execute(query, values)
            conn.commit()
            cursor.execute("SELECT staff_id, username, full_name, role, email, created_at FROM staff WHERE staff_id=%s", (staff_id,))
            row = cursor.fetchone()
            staff = StaffModel.from_db_row(row).to_dict() if row else None
            logger.info(f"Staff updated: {staff_id}")
            return {"status": "success", "message": "Staff updated", "data": staff}
        except Exception as e:
            logger.error(f"Error updating staff {staff_id}: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    def delete(self, staff_id):
        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in delete()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM staff WHERE staff_id=%s", (staff_id,))
            conn.commit()
            logger.info(f"Staff deleted: {staff_id}")
            return {"status": "success", "message": "Staff deleted"," data": staff_id}
        except Exception as e:
            logger.error(f"Error deleting staff {staff_id}: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    def authenticate(self, username, password):
        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in authenticate()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT staff_id, username, password_hash, full_name, role FROM staff WHERE username=%s", (username,))
            row = cursor.fetchone()
            if row and bcrypt.checkpw(password.encode('utf-8'), row['password_hash'].encode('utf-8')):
                logger.info(f"Staff authenticated: {username}")
                return {"status": "success", "message":"Authenticated Successfully","data":{"full_name": row['full_name'], "role": row['role']}}
            else:
                logger.warning(f"Authentication failed for: {username}")
                return {"status": "error", "message": "Invalid username or password"}
        except Exception as e:
            logger.error(f"Error authenticating staff {username}: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    def search(self, by=None, query=None):
        """
        Search staff dynamically by any valid column.
        Example: search(by='full_name', query='John')
        """
        valid_fields = ['username', 'full_name', 'role', 'email']
        if by not in valid_fields:
            return {"status": "error", "message": f"Invalid search field. Use one of: {', '.join(valid_fields)}"}

        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in search()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor(dictionary=True)
        try:
            if not query:
                cursor.execute(f"SELECT staff_id, username, full_name, role, email, created_at FROM staff")
            else:
                sql = f"SELECT staff_id, username, full_name, role, email, created_at FROM staff WHERE {by} LIKE %s"
                cursor.execute(sql, (f"%{query}%",))
            rows = cursor.fetchall()
            data = [StaffModel.from_db_row(row).to_dict() for row in rows]
            logger.info(f"Staff search: by={by}, query={query}, results={len(data)}")
            return {"status": "success","message":"Search results", "data": data}
        except Exception as e:
            logger.error(f"Error in staff search by {by}: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    def get_profile(self, full_name):
        # Just reuse get_by_id
        return self.search(by="full_name", query=full_name)

    def update_profile(self, staff_id, fields):
        # Just reuse update
        return self.update(staff_id, fields)

    def change_password(self, staff_id, old_password, new_password):
        conn = get_connection()
        if not conn:
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT password_hash FROM staff WHERE staff_id=%s", (staff_id,))
            row = cursor.fetchone()
            if not row:
                return {"status": "error", "message": "Staff not found"}
            if not bcrypt.checkpw(old_password.encode('utf-8'), row['password_hash'].encode('utf-8')):
                return {"status": "error", "message": "Old password incorrect"}

            new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute("UPDATE staff SET password_hash=%s WHERE staff_id=%s", (new_hash, staff_id))
            conn.commit()
            return {"status": "success", "message": "Password changed", "data": staff_id}
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()