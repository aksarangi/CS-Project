# frontend/utils.py
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

# -----------------------------
# Message / Alert Helpers
# -----------------------------
def show_info(title, message):
    """Show an informational popup."""
    messagebox.showinfo(title, message)

def show_error(title, message):
    """Show an error popup."""
    messagebox.showerror(title, message)

def show_warning(title, message):
    """Show a warning popup."""
    messagebox.showwarning(title, message)

# -----------------------------
# Image Helpers
# -----------------------------
def load_image(path, size=(100, 100)):
    """
    Load an image from path and resize it.
    Returns a PhotoImage for Tkinter labels/buttons.
    """
    try:
        image = Image.open(path)
        image = image.resize(size, Image.ANTIALIAS)
        return ImageTk.PhotoImage(image)
    except Exception as e:
        print(f"Error loading image '{path}': {e}")
        return None

# -----------------------------
# Formatting Helpers
# -----------------------------
def format_currency(value):
    """Format a float as currency string."""
    try:
        return f"₹{value:,.2f}"  # Indian Rupee formatting
    except:
        return str(value)

def truncate_text(text, length=50):
    """Shorten text for table display."""
    if text and len(text) > length:
        return text[:length] + "..."
    return text
