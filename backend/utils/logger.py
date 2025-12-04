# backend/utils/logger.py

import logging
import os

# Ensure a logs directory exists
LOG_DIR = os.path.join(os.path.dirname(__file__), "../logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Log file path
LOG_FILE = os.path.join(LOG_DIR, "backend.log")

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,  # Change to DEBUG for more verbosity
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Create a named logger for the backend
logger = logging.getLogger("BookShopBackend")

# Optional console output for development
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Example usage for testing
if __name__ == "__main__":
    logger.info("Logger initialized successfully!")
    logger.warning("This is a test warning")
    logger.error("This is a test error")
