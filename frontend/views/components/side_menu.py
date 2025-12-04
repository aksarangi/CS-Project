# frontend/views/components/side_menu.py

import tkinter as tk
from tkinter import ttk

class SideMenu(tk.Frame):

    def __init__(self, master, role, callback_switch_page):
        """
        master -> parent frame
        role -> "customer", "staff", "admin"
        callback_switch_page -> function to call when a menu button is clicked
        """
        super().__init__(master, bg="#e8e8e8", width=220)
        self.role = role
        self.callback = callback_switch_page

        self.build_menu()

    def build_menu(self):
        tk.Label(
            self,
            text="📚 Menu",
            bg="#e8e8e8",
            font=("Arial", 16, "bold")
        ).pack(pady=(20, 10))

        # -------- Common menu options (for Staff/Admin only) --------
        if self.role in ("staff", "admin"):
            self.add_button("Home / Search", "home")
            self.add_button("My Profile", "profile")
            self.add_button("Reports", "reports")
            self.add_button("Inventory", "inventory")
            self.add_button("Publishers", "publishers")
            self.add_button("Authors", "authors")
            self.add_button("Categories", "categories")
            self.add_button("Books", "books")

        # -------- Admin-only options --------
        if self.role == "admin":
            tk.Label(self, text="Admin Controls", bg="#e8e8e8",
                     font=("Arial", 12, "bold")).pack(pady=(25, 5))
            self.add_button("Manage Staff", "staff_mgmt")
            self.add_button("System Logs", "logs")

        # -------- Logout button --------
        self.add_button("Logout", "logout", highlight=True)

    def add_button(self, text, identifier, highlight=False):
        btn = tk.Button(
            self,
            text=text,
            anchor="w",
            relief="flat",
            bg="#dcdcdc" if highlight else "#e8e8e8",
            fg="black",
            padx=15,
            pady=8,
            font=("Arial", 12),
            command=lambda: self.callback(identifier)
        )
        btn.pack(fill="x", pady=2)
