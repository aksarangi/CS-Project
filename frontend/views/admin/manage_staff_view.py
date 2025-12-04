# frontend/views/admin/manage_staff_view.py

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from frontend.api_client import StaffClient
from frontend.views.details_popup import DetailsPopup


ROLES = ["Admin", "Manager", "Sales", "Staff", "Clerk", "Support"]


class StaffFormDialog(simpledialog.Dialog):
    """
    Dialog for adding or editing staff members.
    Includes password field for new users.
    """

    def __init__(self, parent, title="Staff", initial=None, is_edit=False):
        self.initial = initial or {}
        self.is_edit = is_edit
        super().__init__(parent, title)

    def body(self, master):
        ttk.Label(master, text="Full Name:").grid(row=0, column=0, sticky="e", padx=6, pady=6)
        self.name_var = tk.StringVar(value=self.initial.get("full_name"))
        ttk.Entry(master, textvariable=self.name_var).grid(row=0, column=1, padx=6, pady=6)

        ttk.Label(master, text="Username:").grid(row=1, column=0, sticky="e", padx=6, pady=6)
        self.username_var = tk.StringVar(value=self.initial.get("username"))
        entry = ttk.Entry(master, textvariable=self.username_var)
        entry.grid(row=1, column=1, padx=6, pady=6)
        if self.is_edit:
            entry.config(state="disabled")  # username cannot change

        if not self.is_edit:
            ttk.Label(master, text="Password:").grid(row=2, column=0, sticky="e", padx=6, pady=6)
            self.password_var = tk.StringVar()
            ttk.Entry(master, textvariable=self.password_var, show="*").grid(row=2, column=1, padx=6, pady=6)

        ttk.Label(master, text="Email:").grid(row=3, column=0, sticky="e", padx=6, pady=6)
        self.email_var = tk.StringVar(value=self.initial.get("email"))
        ttk.Entry(master, textvariable=self.email_var).grid(row=3, column=1, padx=6, pady=6)

        ttk.Label(master, text="Role:").grid(row=4, column=0, sticky="e", padx=6, pady=6)
        self.role_var = tk.StringVar(value=self.initial.get("role", "Staff"))
        ttk.Combobox(master, values=ROLES, textvariable=self.role_var, state="readonly").grid(
            row=4, column=1, padx=6, pady=6
        )

        return master

    def validate(self):
        if not self.name_var.get().strip():
            messagebox.showwarning("Validation", "Full Name is required.")
            return False
        if not self.username_var.get().strip():
            messagebox.showwarning("Validation", "Username is required.")
            return False
        if not self.is_edit and not self.password_var.get().strip():
            messagebox.showwarning("Validation", "Password is required for new staff.")
            return False
        return True

    def apply(self):
        data = {
            "full_name": self.name_var.get().strip(),
            "username": self.username_var.get().strip(),
            "email": self.email_var.get().strip() or None,
            "role": self.role_var.get()
        }
        if not self.is_edit:
            data["password"] = self.password_var.get().strip()

        self.result = {k: v for k, v in data.items() if v is not None}


class ResetPasswordDialog(simpledialog.Dialog):
    """
    Dialog to reset a staff user's password.
    """

    def body(self, master):
        ttk.Label(master, text="New Password:").grid(row=0, column=0, padx=6, pady=6)
        self.pw1 = tk.StringVar()
        ttk.Entry(master, textvariable=self.pw1, show="*").grid(row=0, column=1)

        ttk.Label(master, text="Confirm Password:").grid(row=1, column=0, padx=6, pady=6)
        self.pw2 = tk.StringVar()
        ttk.Entry(master, textvariable=self.pw2, show="*").grid(row=1, column=1)

    def validate(self):
        if self.pw1.get() != self.pw2.get():
            messagebox.showwarning("Mismatch", "Passwords do not match.")
            return False
        if not self.pw1.get().strip():
            messagebox.showwarning("Empty", "Password cannot be empty.")
            return False
        return True

    def apply(self):
        self.result = {"password": self.pw1.get().strip()}


class ManageStaffView(tk.Frame):
    """
    Admin-level UI to manage staff / employees.
    """

    def __init__(self, parent, go_back):
        super().__init__(parent)
        self.client = StaffClient()
        self.go_back = go_back
        self._row_map = {}

        self.pack(fill="both", expand=True)
        self.build_ui()
        self.load_data()

    def build_ui(self):
        header = tk.Frame(self)
        header.pack(fill="x", padx=10, pady=10)

        tk.Label(header, text="Manage Staff", font=("Arial", 18, "bold")).pack(side="left")

        btns = tk.Frame(header)
        btns.pack(side="right")

        tk.Button(btns, text="Add Staff", command=self.add_staff).pack(side="left", padx=4)
        tk.Button(btns, text="Edit Staff", command=self.edit_staff).pack(side="left", padx=4)
        tk.Button(btns, text="Reset Password", command=self.reset_password).pack(side="left", padx=4)
        tk.Button(btns, text="Delete Staff", command=self.delete_staff).pack(side="left", padx=4)
        tk.Button(btns, text="Back", command=self.go_back).pack(side="left", padx=4)

        cols = ("staff_id", "username", "full_name", "role", "email", "created_at")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")

        for col in cols:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=150)

        self.tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.tree.bind("<Double-1>", self.on_double)

        sb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.place(relx=0.985, rely=0.13, relheight=0.75)

    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        self._row_map.clear()

        records = self.client.get_all() or []
        for rec in records:
            vals = (
                rec.get("staff_id"),
                rec.get("username"),
                rec.get("full_name"),
                rec.get("role"),
                rec.get("email"),
                rec.get("created_at"),
            )
            iid = self.tree.insert("", "end", values=vals)
            self._row_map[iid] = rec

    def add_staff(self):
        dlg = StaffFormDialog(self, "Add Staff", is_edit=False)
        if getattr(dlg, "result", None):
            created = self.client.add(dlg.result)
            if created:
                messagebox.showinfo("Success", "Staff created.")
                self.load_data()
            else:
                messagebox.showerror("Error", "Failed to create.")

    def edit_staff(self):
        iid, rec = self._sel()
        if not rec:
            return

        dlg = StaffFormDialog(self, "Edit Staff", initial=rec, is_edit=True)
        if getattr(dlg, "result", None):
            updated = self.client.update(rec["staff_id"], dlg.result)
            if updated:
                messagebox.showinfo("Success", "Staff updated.")
                self.load_data()

    def reset_password(self):
        iid, rec = self._sel()
        if not rec:
            return

        dlg = ResetPasswordDialog(self, "Reset Password")
        if getattr(dlg, "result", None):
            newpw = dlg.result["password"]
            updated = self.client.update(rec["staff_id"], {"password": newpw})
            if updated:
                messagebox.showinfo("Success", "Password updated.")

    def delete_staff(self):
        iid, rec = self._sel()
        if not rec:
            return

        if not messagebox.askyesno("Confirm", f"Delete staff '{rec['username']}'?"):
            return

        deleted = self.client.delete(rec["staff_id"])
        if deleted:
            messagebox.showinfo("Deleted", "Staff deleted.")
            self.load_data()

    def on_double(self, event):
        iid = self.tree.identify_row(event.y)
        if not iid:
            return
        DetailsPopup(self, "Staff", self._row_map[iid])

    def _sel(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a staff member.")
            return None, None
        iid = sel[0]
        return iid, self._row_map.get(iid)
