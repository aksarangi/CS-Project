# frontend/views/admin/manage_categories_view.py

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from frontend.api_client import CategoriesClient
from frontend.views.details_popup import DetailsPopup  # optional popup


class CategoryFormDialog(simpledialog.Dialog):
    """Dialog for Add/Edit Category."""

    def __init__(self, parent, title="Category", initial=None):
        self.initial = initial or {}
        super().__init__(parent, title)

    def body(self, master):
        ttk.Label(master, text="Category Name:").grid(row=0, column=0, sticky="e", padx=6, pady=6)
        self.name_var = tk.StringVar(value=self.initial.get("name", ""))
        ttk.Entry(master, textvariable=self.name_var, width=40).grid(row=0, column=1, padx=6, pady=6)

        ttk.Label(master, text="Description:").grid(row=1, column=0, sticky="ne", padx=6, pady=6)
        self.desc_text = tk.Text(master, width=38, height=5)
        self.desc_text.grid(row=1, column=1, padx=6, pady=6)
        self.desc_text.insert("1.0", self.initial.get("description", ""))

        return master

    def validate(self):
        if not self.name_var.get().strip():
            messagebox.showwarning("Validation", "Category name is required.")
            return False
        return True

    def apply(self):
        data = {
            "name": self.name_var.get().strip(),
            "description": self.desc_text.get("1.0", "end").strip() or None
        }
        # remove None
        self.result = {k: v for k, v in data.items() if v is not None}


class ManageCategoriesView(tk.Frame):
    """Admin UI: Add/Edit/Delete categories."""

    def __init__(self, parent, go_back=None):
        super().__init__(parent)
        self.parent = parent
        self.go_back = go_back
        self.client = CategoriesClient()

        self.pack(fill="both", expand=True)
        self._row_map = {}

        self.build_ui()
        self.load_categories()

    def build_ui(self):
        header = tk.Frame(self)
        header.pack(fill="x", padx=10, pady=8)

        tk.Label(header, text="Manage Categories", font=("Arial", 16, "bold")).pack(side="left")

        btn_frame = tk.Frame(header)
        btn_frame.pack(side="right")

        tk.Button(btn_frame, text="Add Category", command=self.add_category).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Edit Category", command=self.edit_selected).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Delete Category", command=self.delete_selected).pack(side="left", padx=4)

        if self.go_back:
            tk.Button(btn_frame, text="Back", command=self.go_back).pack(side="left", padx=4)

        cols = ("category_id", "name", "description")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")

        for c in cols:
            self.tree.heading(c, text=c.replace("_", " ").title())
            self.tree.column(c, width=200, anchor="w")

        self.tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.tree.bind("<Double-1>", self.on_double)

        # Scrollbar
        sy = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        sy.place(relx=0.985, rely=0.12, relheight=0.75)
        self.tree.configure(yscrollcommand=sy.set)

    def load_categories(self):
        self.tree.delete(*self.tree.get_children())
        self._row_map.clear()

        cats = self.client.get_all() or []
        for c in cats:
            vals = (c.get("category_id"), c.get("name", ""), c.get("description", ""))
            iid = self.tree.insert("", "end", values=vals)
            self._row_map[iid] = c

    def get_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No selection", "Please select a category.")
            return None, None
        iid = sel[0]
        return iid, self._row_map.get(iid)

    def add_category(self):
        dlg = CategoryFormDialog(self, title="Add Category")
        if getattr(dlg, "result", None):
            created = self.client.add(dlg.result)
            if created:
                messagebox.showinfo("Success", "Category added.")
                self.load_categories()
            else:
                messagebox.showerror("Error", "Failed to add category.")

    def edit_selected(self):
        iid, record = self.get_selected()
        if not record:
            return

        initial = {
            "name": record.get("name"),
            "description": record.get("description", "")
        }

        dlg = CategoryFormDialog(self, title="Edit Category", initial=initial)
        if getattr(dlg, "result", None):
            updated = self.client.update(record.get("category_id"), dlg.result)
            if updated:
                messagebox.showinfo("Success", "Category updated.")
                self.load_categories()
            else:
                messagebox.showerror("Error", "Failed to update category.")

    def delete_selected(self):
        iid, record = self.get_selected()
        if not record:
            return

        if not messagebox.askyesno("Confirm", f"Delete category '{record.get('name')}'?"):
            return

        res = self.client.delete(record.get("category_id"))
        if res:
            messagebox.showinfo("Deleted", "Category deleted.")
            self.load_categories()
        else:
            messagebox.showerror("Error", "Failed to delete category.")

    def on_double(self, event):
        iid = self.tree.identify_row(event.y)
        if not iid:
            return
        record = self._row_map.get(iid)
        if not record:
            return

        try:
            DetailsPopup(self, "Categories", record)
        except Exception:
            self.edit_selected()
