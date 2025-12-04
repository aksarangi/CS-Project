# frontend/views/login_view.py
import tkinter as tk
from tkinter import ttk
from frontend.utils import show_error
from frontend.api_client import StaffClient


class LoginView(tk.Frame):
    """
    Login screen that authenticates user using StaffClient.
    On success → calls provided on_success callback with user_info dict.
    """

    def __init__(self, parent, on_success=None):
        super().__init__(parent)

        self.on_success = on_success          # callback passed from main.py
        self.staff_client = StaffClient()

        self.build_ui()

    # -----------------------------------------------------
    # UI
    # -----------------------------------------------------
    def build_ui(self):
        self.grid(row=0, column=0, sticky="nsew")

        # Title on the root window (not this frame)
        self.winfo_toplevel().title("Book Shop Management — Login")

        container = tk.Frame(self)
        container.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(container, text="Login", font=("Arial", 18, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 15)
        )

        # Username
        tk.Label(container, text="Username:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.username_var = tk.StringVar()
        ttk.Entry(container, textvariable=self.username_var, width=25).grid(
            row=1, column=1, padx=5, pady=5
        )

        # Password
        tk.Label(container, text="Password:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.password_var = tk.StringVar()
        ttk.Entry(container, textvariable=self.password_var, width=25, show="*").grid(
            row=2, column=1, padx=5, pady=5
        )

        # Login button
        ttk.Button(container, text="Login", command=self.login).grid(
            row=3, column=0, columnspan=2, pady=(12, 5)
        )

    # -----------------------------------------------------
    # LOGIN LOGIC
    # -----------------------------------------------------
    def login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        if not username or not password:
            show_error("Login Failed", "Please enter both username and password.")
            return

        user_data = self.staff_client.authenticate(username, password)

        if user_data is None:
            show_error("Login Failed", "Invalid username or password.")
            return

        # When login is correct → call App.on_login_success
        if self.on_success:
            self.on_success(user_data)
