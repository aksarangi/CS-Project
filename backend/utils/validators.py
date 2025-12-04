# backend/utils/validators.py

import re

def is_valid_email(email):
    """
    Validates email format.
    """
    if not email:
        return False
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

def is_valid_phone(phone):
    """
    Validates phone number format (Indian/International optional).
    Accepts digits, spaces, +, -, parentheses.
    """
    if not phone:
        return False
    pattern = r'^\+?[\d\s\-\(\)]{7,20}$'
    return bool(re.match(pattern, phone))

def is_valid_isbn(isbn):
    """
    Validates ISBN-10 or ISBN-13.
    """
    if not isbn:
        return False
    isbn = isbn.replace("-", "").replace(" ", "")
    if len(isbn) == 10:
        # ISBN-10 checksum
        total = 0
        for i, char in enumerate(isbn):
            if char.upper() == 'X' and i == 9:
                value = 10
            elif char.isdigit():
                value = int(char)
            else:
                return False
            total += value * (10 - i)
        return total % 11 == 0
    elif len(isbn) == 13:
        # ISBN-13 checksum
        total = 0
        for i, char in enumerate(isbn):
            if not char.isdigit():
                return False
            factor = 1 if i % 2 == 0 else 3
            total += int(char) * factor
        return total % 10 == 0
    else:
        return False

def is_positive_number(value):
    """
    Checks if value is a positive integer or float.
    """
    try:
        return float(value) > 0
    except (ValueError, TypeError):
        return False

def is_non_negative_integer(value):
    """
    Checks if value is an integer >= 0 (e.g., stock or quantity).
    """
    try:
        return int(value) >= 0
    except (ValueError, TypeError):
        return False

def is_valid_role(role):
    """
    Checks if the role is one of allowed roles for staff.
    """
    allowed_roles = ["Admin", "Manager", "Clerk"]
    return role in allowed_roles

def is_non_empty_string(value):
    return isinstance(value, str) and bool(value.strip())