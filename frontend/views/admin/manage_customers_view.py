# frontend/views/admin/manage_customers_view.py

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from frontend.api_client import CustomersClient
from frontend.views.details_popup import DetailsPopup


class CustomerFormDialog(simpledialog.Dialog):
    """
    Dialog used for Add/Edit customer.
    """

    def __init__(self, parent, title="Customer", initial=None):
        self.initial = initial or {}
        super().__init__(parent, title)

    def body(self, master):
        ttk.Label(master, text="Name:").grid(row=0, column=0, sticky="e", padx=6, pady=6)
        self.name_var = tk.StringVar(value=self.initial.get("name", ""))
        ttk.Entry(master, textvariable=self.name_var, width=45).grid(row=0, column=1, padx=6, pady=6)

        ttk.Label(master, text="Email:").grid(row=1, column=0, sticky="e", padx=6, pady=6)
        self.email_var = tk.StringVar(value=self.initial.get("email", ""))
        ttk.Entry(master, textvariable=self.email_var).grid(row=1, column=1, padx=6, pady=6)

        ttk.Label(master, text="Phone:").grid(row=2, column=0, sticky="e", padx=6, pady=6)
        self.phone_var = tk.StringVar(value=self.initial.get("phone", ""))
        ttk.Entry(master, textvariable=self.phone_var).grid(row=2, column=1, padx=6, pady=6)

        ttk.Label(master, text="Address:").grid(row=3, column=0, sticky="ne", padx=6, pady=6)
        self.address_text = tk.Text(master, width=40, height=4)
        self.address_text.grid(row=3, column=1, padx=6, pady=6)
        self.address_text.insert("1.0", self.initial.get("address", ""))

        return master

    def validate(self):
        if not self.name_var.get().strip():
            messagebox.showwarning("Validation", "Name is required.")
            return False
        # optionally validate email/phone
        return True

    def apply(self):
        data = {
            "name": self.name_var.get().strip(),
            "email": self.email_var.get().strip() or None,
            "phone": self.phone_var.get().strip() or None,
            "address": self.address_text.get("1.0", "end").strip() or None
        }
        self.result = {k: v for k, v in data.items() if v is not None}


class ManageCustomersView(tk.Frame):
    """
    Admin UI for customer management.
    """

    def __init__(self, parent, go_back=None):
        super().__init__(parent)
        self.parent = parent
        self.go_back = go_back
        self.client = CustomersClient()

        self.pack(fill="both", expand=True)
        self._row_map = {}

        self.build_ui()
        self.load_customers()

    def build_ui(self):
        header = tk.Frame(self)
        header.pack(fill="x", padx=10, pady=8)

        tk.Label(header, text="Manage Customers", font=("Arial", 16, "bold")).pack(side="left")

        btns = tk.Frame(header)
        btns.pack(side="right")

        tk.Button(btns, text="Add Customer", command=self.add_customer).pack(side="left", padx=4)
        tk.Button(btns, text="Edit Customer", command=self.edit_customer).pack(side="left", padx=4)
        tk.Button(btns, text="Delete Customer", command=self.delete_customer).pack(side="left", padx=4)

        if self.go_back:
            tk.Button(btns, text="Back", command=self.go_back).pack(side="left", padx=4)

        cols = ("customer_id", "name", "email", "phone", "address", "joined_date")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")

        for c in cols:
            self.tree.heading(c, text=c.replace("_", " ").title())
            self.tree.column(c, width=160, anchor="w")

        self.tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.tree.bind("<Double-1>", self.on_double_click)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        scrollbar.place(relx=0.985, rely=0.12, relheight=0.75)
        self.tree.configure(yscrollcommand=scrollbar.set)

    def load_customers(self):
        self.tree.delete(*self.tree.get_children())
        self._row_map.clear()

        customers = self.client.get_all() or []
        for c in customers:
            vals = (
                c.get("customer_id"),
                c.get("name", ""),
                c.get("email", ""),
                c.get("phone", ""),
                c.get("address", ""),
                c.get("joined_date", "")
            )
            iid = self.tree.insert("", "end", values=vals)
            self._row_map[iid] = c

    def add_customer(self):
        dlg = CustomerFormDialog(self, "Add Customer")
        if getattr(dlg, "result", None):
            created = self.client.add(dlg.result)
            if created:
                messagebox.showinfo("Success", "Customer added.")
                self.load_customers()
            else:
                messagebox.showerror("Error", "Failed to add customer.")

    def edit_customer(self):
        iid, record = self._get_selected()
        if not record:
            return

        initial = {
            "name": record.get("name"),
            "email": record.get("email"),
            "phone": record.get("phone"),
            "address": record.get("address", "")
        }

        dlg = CustomerFormDialog(self, "Edit Customer", initial=initial)
        if getattr(dlg, "result", None):
            updated = self.client.update(record.get("customer_id"), dlg.result)
            if updated:
                messagebox.showinfo("Success", "Customer updated.")
                self.load_customers()
            else:
                messagebox.showerror("Error", "Update failed.")

    def delete_customer(self):
        iid, record = self._get_selected()
        if not record:
            return

        if not messagebox.askyesno("Confirm", f"Delete customer '{record.get('name')}'?"):
            return

        deleted = self.client.delete(record.get("customer_id"))
        if deleted:
            messagebox.showinfo("Deleted", "Customer deleted.")
            self.load_customers()
        else:
            messagebox.showerror("Error", "Delete failed.")

    def _get_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No selection", "Select a customer.")
            return None, None
        iid = sel[0]
        return iid, self._row_map.get(iid)

    def on_double_click(self, event):
        iid = self.tree.identify_row(event.y)
        if not iid:
            return
        record = self._row_map.get(iid)
        if not record:
            return

        try:
            DetailsPopup(self, "Customer", record)
        except Exception:
            self.edit_customer()
