# backend/database/db_connection.py

import mysql.connector
from mysql.connector import Error
import os
from backend.utils.logger import logger
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

def get_connection():
    """
    Returns a MySQL connection object using credentials from .env.
    Returns None if connection fails.
    """
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASS", ""),
            database=os.getenv("DB_NAME", "bookshop_db")
        )
        return conn
    except Error as e:
        logger.error(f"[DB_CONNECTION_ERROR] Error connecting to MySQL: {e}")
        return None

# Optional helper for testing connection
if __name__ == "__main__":
    connection = get_connection()
    if connection:
        logger.info("Database connection successful!")
        connection.close()
    else:
        logger.error("Database connection failed!")
