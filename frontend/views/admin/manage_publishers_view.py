# frontend/views/admin/manage_publishers_view.py

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from frontend.api_client import PublishersClient
from frontend.views.details_popup import DetailsPopup  # optional: show details on double-click


class PublisherFormDialog(simpledialog.Dialog):
    """
    Modal dialog for Add / Edit Publisher.
    After OK, `self.result` contains the publisher data dict.
    """

    def __init__(self, parent, title="Publisher", initial=None):
        self.initial = initial or {}
        super().__init__(parent, title)

    def body(self, master):
        ttk.Label(master, text="Name:").grid(row=0, column=0, sticky="e", padx=6, pady=6)
        self.name_var = tk.StringVar(value=self.initial.get("name", ""))
        ttk.Entry(master, textvariable=self.name_var, width=48).grid(row=0, column=1, padx=6, pady=6)

        ttk.Label(master, text="Location:").grid(row=1, column=0, sticky="e", padx=6, pady=6)
        self.location_var = tk.StringVar(value=self.initial.get("location", ""))
        ttk.Entry(master, textvariable=self.location_var).grid(row=1, column=1, padx=6, pady=6)

        ttk.Label(master, text="Contact Email:").grid(row=2, column=0, sticky="e", padx=6, pady=6)
        self.email_var = tk.StringVar(value=self.initial.get("contact_email", ""))
        ttk.Entry(master, textvariable=self.email_var).grid(row=2, column=1, padx=6, pady=6)

        ttk.Label(master, text="Phone:").grid(row=3, column=0, sticky="e", padx=6, pady=6)
        self.phone_var = tk.StringVar(value=self.initial.get("phone", ""))
        ttk.Entry(master, textvariable=self.phone_var).grid(row=3, column=1, padx=6, pady=6)

        ttk.Label(master, text="Notes / Description:").grid(row=4, column=0, sticky="ne", padx=6, pady=6)
        self.notes_text = tk.Text(master, width=40, height=6)
        self.notes_text.grid(row=4, column=1, padx=6, pady=6)
        self.notes_text.insert("1.0", self.initial.get("notes", ""))

        return master

    def validate(self):
        if not self.name_var.get().strip():
            messagebox.showwarning("Validation", "Publisher name is required.")
            return False
        # email/phone validation optional
        return True

    def apply(self):
        data = {
            "name": self.name_var.get().strip(),
            "location": self.location_var.get().strip() or None,
            "contact_email": self.email_var.get().strip() or None,
            "phone": self.phone_var.get().strip() or None,
            "notes": self.notes_text.get("1.0", "end").strip() or None
        }
        # remove None values
        self.result = {k: v for k, v in data.items() if v is not None}


class ManagePublishersView(tk.Frame):
    """
    Admin UI to manage publishers: list / add / edit / delete.
    """

    def __init__(self, parent, go_back=None):
        super().__init__(parent)
        self.parent = parent
        self.go_back = go_back
        self.client = PublishersClient()

        self.pack(fill="both", expand=True)
        self._row_map = {}
        self.build_ui()
        self.load_publishers()

    def build_ui(self):
        header = tk.Frame(self)
        header.pack(fill="x", padx=10, pady=8)

        tk.Label(header, text="Manage Publishers", font=("Arial", 16, "bold")).pack(side="left")

        btn_frame = tk.Frame(header)
        btn_frame.pack(side="right")
        tk.Button(btn_frame, text="Add Publisher", command=self.add_publisher).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Edit Publisher", command=self.edit_selected).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Delete Publisher", command=self.delete_selected).pack(side="left", padx=4)
        if self.go_back:
            tk.Button(btn_frame, text="Back", command=self.go_back).pack(side="left", padx=4)

        # Treeview columns
        cols = ("publisher_id", "name", "location", "contact_email", "phone")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c.replace("_", " ").title())
            self.tree.column(c, width=160, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # bind double click to details
        self.tree.bind("<Double-1>", self.on_double)

        # vertical scrollbar
        sy = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        sy.place(relx=0.985, rely=0.12, relheight=0.75)
        self.tree.configure(yscrollcommand=sy.set)

    def load_publishers(self):
        self.tree.delete(*self.tree.get_children())
        self._row_map.clear()
        pubs = self.client.get_all() or []
        for p in pubs:
            vals = (
                p.get("publisher_id"),
                p.get("name", ""),
                p.get("location", ""),
                p.get("contact_email", ""),
                p.get("phone", "")
            )
            iid = self.tree.insert("", "end", values=vals)
            self._row_map[iid] = p

    def get_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No selection", "Please select a publisher.")
            return None, None
        iid = sel[0]
        return iid, self._row_map.get(iid)

    def add_publisher(self):
        dlg = PublisherFormDialog(self, title="Add Publisher")
        if getattr(dlg, "result", None):
            created = self.client.add(dlg.result)
            if created:
                messagebox.showinfo("Success", "Publisher added.")
                self.load_publishers()
            else:
                messagebox.showerror("Error", "Failed to add publisher.")

    def edit_selected(self):
        iid, record = self.get_selected()
        if not record:
            return
        initial = {
            "name": record.get("name"),
            "location": record.get("location"),
            "contact_email": record.get("contact_email"),
            "phone": record.get("phone"),
            "notes": record.get("notes", "")
        }
        dlg = PublisherFormDialog(self, title="Edit Publisher", initial=initial)
        if getattr(dlg, "result", None):
            updated = self.client.update(record.get("publisher_id"), dlg.result)
            if updated:
                messagebox.showinfo("Success", "Publisher updated.")
                self.load_publishers()
            else:
                messagebox.showerror("Error", "Failed to update publisher.")

    def delete_selected(self):
        iid, record = self.get_selected()
        if not record:
            return
        if not messagebox.askyesno("Confirm", f"Delete publisher '{record.get('name')}'?"):
            return
        res = self.client.delete(record.get("publisher_id"))
        if res:
            messagebox.showinfo("Deleted", "Publisher deleted.")
            self.load_publishers()
        else:
            messagebox.showerror("Error", "Failed to delete publisher.")

    def on_double(self, event):
        iid = self.tree.identify_row(event.y)
        if not iid:
            return
        record = self._row_map.get(iid)
        if not record:
            return
        # show details popup if available, else fallback to edit
        try:
            DetailsPopup(self, "Publishers", record)
        except Exception:
            self.edit_selected()
# frontend/views/admin/manage_publishers_view.py

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from frontend.api_client import PublishersClient
from frontend.views.details_popup import DetailsPopup  # optional: show details on double-click


class PublisherFormDialog(simpledialog.Dialog):
    """
    Modal dialog for Add / Edit Publisher.
    After OK, `self.result` contains the publisher data dict.
    """

    def __init__(self, parent, title="Publisher", initial=None):
        self.initial = initial or {}
        super().__init__(parent, title)

    def body(self, master):
        ttk.Label(master, text="Name:").grid(row=0, column=0, sticky="e", padx=6, pady=6)
        self.name_var = tk.StringVar(value=self.initial.get("name", ""))
        ttk.Entry(master, textvariable=self.name_var, width=48).grid(row=0, column=1, padx=6, pady=6)

        ttk.Label(master, text="Location:").grid(row=1, column=0, sticky="e", padx=6, pady=6)
        self.location_var = tk.StringVar(value=self.initial.get("location", ""))
        ttk.Entry(master, textvariable=self.location_var).grid(row=1, column=1, padx=6, pady=6)

        ttk.Label(master, text="Contact Email:").grid(row=2, column=0, sticky="e", padx=6, pady=6)
        self.email_var = tk.StringVar(value=self.initial.get("contact_email", ""))
        ttk.Entry(master, textvariable=self.email_var).grid(row=2, column=1, padx=6, pady=6)

        ttk.Label(master, text="Phone:").grid(row=3, column=0, sticky="e", padx=6, pady=6)
        self.phone_var = tk.StringVar(value=self.initial.get("phone", ""))
        ttk.Entry(master, textvariable=self.phone_var).grid(row=3, column=1, padx=6, pady=6)

        ttk.Label(master, text="Notes / Description:").grid(row=4, column=0, sticky="ne", padx=6, pady=6)
        self.notes_text = tk.Text(master, width=40, height=6)
        self.notes_text.grid(row=4, column=1, padx=6, pady=6)
        self.notes_text.insert("1.0", self.initial.get("notes", ""))

        return master

    def validate(self):
        if not self.name_var.get().strip():
            messagebox.showwarning("Validation", "Publisher name is required.")
            return False
        # email/phone validation optional
        return True

    def apply(self):
        data = {
            "name": self.name_var.get().strip(),
            "location": self.location_var.get().strip() or None,
            "contact_email": self.email_var.get().strip() or None,
            "phone": self.phone_var.get().strip() or None,
            "notes": self.notes_text.get("1.0", "end").strip() or None
        }
        # remove None values
        self.result = {k: v for k, v in data.items() if v is not None}


class ManagePublishersView(tk.Frame):
    """
    Admin UI to manage publishers: list / add / edit / delete.
    """

    def __init__(self, parent, go_back=None):
        super().__init__(parent)
        self.parent = parent
        self.go_back = go_back
        self.client = PublishersClient()

        self.pack(fill="both", expand=True)
        self._row_map = {}
        self.build_ui()
        self.load_publishers()

    def build_ui(self):
        header = tk.Frame(self)
        header.pack(fill="x", padx=10, pady=8)

        tk.Label(header, text="Manage Publishers", font=("Arial", 16, "bold")).pack(side="left")

        btn_frame = tk.Frame(header)
        btn_frame.pack(side="right")
        tk.Button(btn_frame, text="Add Publisher", command=self.add_publisher).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Edit Publisher", command=self.edit_selected).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Delete Publisher", command=self.delete_selected).pack(side="left", padx=4)
        if self.go_back:
            tk.Button(btn_frame, text="Back", command=self.go_back).pack(side="left", padx=4)

        # Treeview columns
        cols = ("publisher_id", "name", "location", "contact_email", "phone")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c.replace("_", " ").title())
            self.tree.column(c, width=160, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # bind double click to details
        self.tree.bind("<Double-1>", self.on_double)

        # vertical scrollbar
        sy = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        sy.place(relx=0.985, rely=0.12, relheight=0.75)
        self.tree.configure(yscrollcommand=sy.set)

    def load_publishers(self):
        self.tree.delete(*self.tree.get_children())
        self._row_map.clear()
        pubs = self.client.get_all() or []
        for p in pubs:
            vals = (
                p.get("publisher_id"),
                p.get("name", ""),
                p.get("location", ""),
                p.get("contact_email", ""),
                p.get("phone", "")
            )
            iid = self.tree.insert("", "end", values=vals)
            self._row_map[iid] = p

    def get_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No selection", "Please select a publisher.")
            return None, None
        iid = sel[0]
        return iid, self._row_map.get(iid)

    def add_publisher(self):
        dlg = PublisherFormDialog(self, title="Add Publisher")
        if getattr(dlg, "result", None):
            created = self.client.add(dlg.result)
            if created:
                messagebox.showinfo("Success", "Publisher added.")
                self.load_publishers()
            else:
                messagebox.showerror("Error", "Failed to add publisher.")

    def edit_selected(self):
        iid, record = self.get_selected()
        if not record:
            return
        initial = {
            "name": record.get("name"),
            "location": record.get("location"),
            "contact_email": record.get("contact_email"),
            "phone": record.get("phone"),
            "notes": record.get("notes", "")
        }
        dlg = PublisherFormDialog(self, title="Edit Publisher", initial=initial)
        if getattr(dlg, "result", None):
            updated = self.client.update(record.get("publisher_id"), dlg.result)
            if updated:
                messagebox.showinfo("Success", "Publisher updated.")
                self.load_publishers()
            else:
                messagebox.showerror("Error", "Failed to update publisher.")

    def delete_selected(self):
        iid, record = self.get_selected()
        if not record:
            return
        if not messagebox.askyesno("Confirm", f"Delete publisher '{record.get('name')}'?"):
            return
        res = self.client.delete(record.get("publisher_id"))
        if res:
            messagebox.showinfo("Deleted", "Publisher deleted.")
            self.load_publishers()
        else:
            messagebox.showerror("Error", "Failed to delete publisher.")

    def on_double(self, event):
        iid = self.tree.identify_row(event.y)
        if not iid:
            return
        record = self._row_map.get(iid)
        if not record:
            return
        # show details popup if available, else fallback to edit
        try:
            DetailsPopup(self, "Publishers", record)
        except Exception:
            self.edit_selected()
