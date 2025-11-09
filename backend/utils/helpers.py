# backend/utils/helpers.py

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

def format_date(dt, fmt="%Y-%m-%d %H:%M:%S"):
    """
    Converts a datetime object to a formatted string.
    """
    if not dt:
        return None
    return dt.strftime(fmt)

def parse_date(date_str, fmt="%Y-%m-%d %H:%M:%S"):
    """
    Converts a formatted string to a datetime object.
    """
    try:
        return datetime.strptime(date_str, fmt)
    except (ValueError, TypeError):
        return None

def round_price(value, precision=2):
    """
    Rounds a price to 2 decimal places by default.
    """
    try:
        return float(Decimal(value).quantize(Decimal(f"1.{'0'*precision}"), rounding=ROUND_HALF_UP))
    except Exception:
        return 0.0

def calculate_order_total(order_items):
    """
    Calculates total amount for an order.
    `order_items` should be a list of dicts: [{"price_each": float, "quantity": int}, ...]
    """
    total = 0.0
    for item in order_items:
        price = float(item.get("price_each", 0))
        qty = int(item.get("quantity", 0))
        total += price * qty
    return round_price(total)

def safe_get(dct, key, default=None):
    """
    Safely gets a value from a dict, returns default if key not present.
    """
    if not isinstance(dct, dict):
        return default
    return dct.get(key, default)
