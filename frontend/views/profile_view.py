# frontend/views/profile_view.py

import tkinter as tk
from tkinter import ttk, messagebox

from frontend.api_client import UsersClient


class ProfileView(tk.Frame):
    """
    Staff/Admin Profile Page.
    Shows user info, allows profile updates, and password change.
    """

    def __init__(self, root, user, go_back):
        super().__init__(root)

        self.root = root
        self.user = user             # dict from login: {user_id, username, role, ...}
        self.go_back = go_back       # function from navigation controller
        self.users = UsersClient()   # API client

        self.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.build_header()
        self.build_profile_form()
        self.build_password_form()

        # Load profile details from backend
        self.load_profile()

    # -------------------------------------------------------------------
    # HEADER
    # -------------------------------------------------------------------
    def build_header(self):
        header = tk.Frame(self, bg="#f0f0f0", pady=10)
        header.grid(row=0, column=0, sticky="ew")

        tk.Label(
            header,
            text="My Profile",
            font=("Arial", 20, "bold"),
            bg="#f0f0f0"
        ).pack(side="left", padx=15)

        ttk.Button(
            header,
            text="Back",
            command=self.go_back
        ).pack(side="right", padx=15)

    # -------------------------------------------------------------------
    # PROFILE INFO SECTION
    # -------------------------------------------------------------------
    def build_profile_form(self):
        frame = ttk.LabelFrame(self, text="Personal Information")
        frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

        for i in range(2):
            frame.columnconfigure(i, weight=1)

        # Field variables
        self.user_id = tk.StringVar()
        self.name_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.role_var = tk.StringVar()  # Read-only (admin/staff)

        # --- Name
        ttk.Label(frame, text="ID:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        ttk.Entry(frame, textvariable=self.user_id).grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # --- Name
        ttk.Label(frame, text="Name:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        ttk.Entry(frame, textvariable=self.name_var).grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # --- Email
        ttk.Label(frame, text="Email:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        ttk.Entry(frame, textvariable=self.email_var).grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        # --- Role (disabled)
        ttk.Label(frame, text="Role:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        ttk.Entry(frame, textvariable=self.role_var, state="disabled").grid(
            row=3, column=1, padx=10, pady=10, sticky="ew"
        )

        # --- Save Button
        ttk.Button(frame, text="Save Changes", command=self.save_profile).grid(
            row=4, column=0, columnspan=2, pady=15
        )

    # -------------------------------------------------------------------
    # PASSWORD CHANGE SECTION
    # -------------------------------------------------------------------
    def build_password_form(self):
        frame = ttk.LabelFrame(self, text="Change Password")
        frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))

        frame.columnconfigure(1, weight=1)

        self.old_pw_var = tk.StringVar()
        self.new_pw_var = tk.StringVar()
        self.confirm_pw_var = tk.StringVar()

        ttk.Label(frame, text="Old Password:").grid(row=0, column=0, padx=10, pady=8)
        ttk.Entry(frame, textvariable=self.old_pw_var, show="*").grid(
            row=0, column=1, padx=10, pady=8, sticky="ew"
        )

        ttk.Label(frame, text="New Password:").grid(row=1, column=0, padx=10, pady=8)
        ttk.Entry(frame, textvariable=self.new_pw_var, show="*").grid(
            row=1, column=1, padx=10, pady=8, sticky="ew"
        )

        ttk.Label(frame, text="Confirm Password:").grid(row=2, column=0, padx=10, pady=8)
        ttk.Entry(frame, textvariable=self.confirm_pw_var, show="*").grid(
            row=2, column=1, padx=10, pady=8, sticky="ew"
        )

        ttk.Button(frame, text="Update Password", command=self.change_password).grid(
            row=3, column=0, columnspan=2, pady=10
        )

    # -------------------------------------------------------------------
    # LOAD PROFILE DATA
    # -------------------------------------------------------------------
    def load_profile(self):
        """Fetch profile details from backend."""
        data = self.users.get_profile(self.user["username"])
        if not data:
            messagebox.showerror("Error", "Failed to load profile.")
            return
        for user in data:
            self.user_id.set(user.get("staff_id", ""))
            self.name_var.set(user.get("full_name", ""))
            self.email_var.set(user.get("email", ""))
            self.role_var.set(user.get("role",""))

    # -------------------------------------------------------------------
    # SAVE PROFILE
    # -------------------------------------------------------------------
    def save_profile(self):
        updated = {
            "name": self.name_var.get().strip(),
            "email": self.email_var.get().strip(),
        }

        ok = self.users.update_profile(self.user_id, updated)
        if ok:
            messagebox.showinfo("Success", "Profile updated.")
        else:
            messagebox.showerror("Error", "Failed to update profile.")

    # -------------------------------------------------------------------
    # CHANGE PASSWORD
    # -------------------------------------------------------------------
    def change_password(self):
        old = self.old_pw_var.get().strip()
        new = self.new_pw_var.get().strip()
        confirm = self.confirm_pw_var.get().strip()

        if not old or not new:
            messagebox.showwarning("Missing fields", "Please enter all fields.")
            return

        if new != confirm:
            messagebox.showwarning("Mismatch", "New passwords do not match.")
            return

        ok = self.users.change_password(self.user_id, old, new)
        if ok:
            messagebox.showinfo("Success", "Password changed.")
            self.old_pw_var.set("")
            self.new_pw_var.set("")
            self.confirm_pw_var.set("")
        else:
            messagebox.showerror("Error", "Password change failed.")
