# backend/api/customers.py

from backend.database.db_connection import get_connection
from backend.utils.helpers import safe_get, format_date
from backend.utils.validators import is_valid_email, is_non_empty_string
from backend.utils.logger import logger
from backend.models.customer_model import CustomerModel


class CustomersAPI:
    """
    Local API class to manage customers using CustomerModel.
    Provides CRUD + search functionality.
    """

    def get_all(self):
        """
        Returns all customers
        """
        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in get_all()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT * FROM customers WHERE 1=1"
            cursor.execute(query)
            rows = cursor.fetchall()
            customers = [CustomerModel.from_db_row(row).to_dict() for row in rows]
            logger.info(f"Fetched {len(customers)} customers")
            return {"status": "success","message":"Fetched all customers", "data": customers}

        except Exception as e:
            logger.error(f"Error fetching customers: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    def get_by_id(self, customer_id):
        """
        Fetch a single customer by ID
        """
        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in get_by_id()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT * FROM customers WHERE customer_id=%s"
            cursor.execute(query, (customer_id,))
            row = cursor.fetchone()
            if row:
                customer = CustomerModel.from_db_row(row)
                logger.info(f"Customer fetched: {customer_id}")
                return {"status": "success","message":"Fetched customer by id", "data": customer.to_dict()}
            else:
                logger.warning(f"Customer not found: {customer_id}")
                return {"status": "error", "message": "Customer not found"}

        except Exception as e:
            logger.error(f"Error fetching customer by ID {customer_id}: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    def add(self, customer_data):
        """
        Add a new customer.
        Required: full_name
        Optional: email, phone, address, city, state, country, postal_code
        """
        full_name = safe_get(customer_data, "full_name")
        if not is_non_empty_string(full_name):
            return {"status": "error", "message": "full_name is required"}

        email = safe_get(customer_data, "email")
        if email and not is_valid_email(email):
            return {"status": "error", "message": "Invalid email format"}

        phone = safe_get(customer_data, "phone")
        address = safe_get(customer_data, "address")
        city = safe_get(customer_data, "city")
        state = safe_get(customer_data, "state")
        country = safe_get(customer_data, "country", "India")
        postal_code = safe_get(customer_data, "postal_code")

        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in add()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor()
        try:
            query = """
                INSERT INTO customers (full_name, email, phone, address, city, state, country, postal_code)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (full_name, email, phone, address, city, state, country, postal_code))
            conn.commit()
            customer_id = cursor.lastrowid
            logger.info(f"Customer added: {customer_id} - {full_name}")

            new_customer = CustomerModel(
                customer_id=customer_id,
                full_name=full_name,
                email=email,
                phone=phone,
                address=address,
                city=city,
                state=state,
                country=country,
                postal_code=postal_code
            )
            return {"status": "success", "message": "Customer added", "data": new_customer.to_dict()}

        except Exception as e:
            logger.error(f"Error adding customer: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    def update(self, customer_id, customer_data):
        """
        Update an existing customer
        """
        if not customer_data:
            return {"status": "error", "message": "No fields to update"}

        if "email" in customer_data and customer_data["email"] and not is_valid_email(customer_data["email"]):
            return {"status": "error", "message": "Invalid email format"}

        fields = ", ".join(f"{key}=%s" for key in customer_data.keys())
        values = list(customer_data.values())
        values.append(customer_id)

        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in update()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor()
        try:
            query = f"UPDATE customers SET {fields} WHERE customer_id=%s"
            cursor.execute(query, values)
            conn.commit()
            logger.info(f"Customer updated: {customer_id}")

            updated_customer = self.get_by_id(customer_id)
            return {"status": "success", "message": "Customer updated", "data": updated_customer.get("data")}

        except Exception as e:
            logger.error(f"Error updating customer {customer_id}: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    def delete(self, customer_id):
        """
        Delete a customer by ID
        """
        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in delete()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM customers WHERE customer_id=%s", (customer_id,))
            conn.commit()
            logger.info(f"Customer deleted: {customer_id}")
            return {"status": "success", "message": "Customer deleted", "data":customer_id}

        except Exception as e:
            logger.error(f"Error deleting customer {customer_id}: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    # ==========================================================
    # 🔍 New: Flexible smart search (for universal search router)
    # ==========================================================
    def search_customers(self, by="any", value=None):
        """
        Flexible search by field or universal match.
        `by` can be: 'full_name', 'email', 'city', 'state', 'any'
        """
        if not value:
            return self.get_all()

        allowed_fields = ["full_name", "email", "city", "state"]

        conn = get_connection()
        if not conn:
            logger.error("DB connection failed in search_customers()")
            return {"status": "error", "message": "DB connection failed"}

        cursor = conn.cursor(dictionary=True)
        try:
            if by == "any":
                query = "SELECT * FROM customers WHERE "
                query += " OR ".join(f"{field} LIKE %s" for field in allowed_fields)
                params = tuple(f"%{value}%" for _ in allowed_fields)
            elif by in allowed_fields:
                query = f"SELECT * FROM customers WHERE {by} LIKE %s"
                params = (f"%{value}%",)
            else:
                return {"status": "error", "message": f"Invalid field '{by}'"}

            cursor.execute(query, params)
            rows = cursor.fetchall()
            customers = [CustomerModel.from_db_row(r).to_dict() for r in rows]
            logger.info(f"Search '{value}' in '{by}': {len(customers)} results")
            return {"status": "success", "message":"Search results", "data": customers}

        except Exception as e:
            logger.error(f"Error in search_customers(by={by}, value={value}): {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()
            