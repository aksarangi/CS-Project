# frontend/views/admin/manage_authors_view.py

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from frontend.api_client import AuthorsClient
from frontend.views.details_popup import DetailsPopup  # optional; show on double click

class AuthorFormDialog(simpledialog.Dialog):
    """
    Modal dialog used for Add / Edit Author.
    After OK, `self.result` will contain the author data dict.
    """
    def __init__(self, parent, title="Author", initial=None):
        self.initial = initial or {}
        super().__init__(parent, title)

    def body(self, master):
        # layout labels + entries
        ttk.Label(master, text="Name:").grid(row=0, column=0, sticky="e", padx=6, pady=6)
        self.name_var = tk.StringVar(value=self.initial.get("name", ""))
        ttk.Entry(master, textvariable=self.name_var, width=48).grid(row=0, column=1, padx=6, pady=6)

        ttk.Label(master, text="Country:").grid(row=1, column=0, sticky="e", padx=6, pady=6)
        self.country_var = tk.StringVar(value=self.initial.get("country", ""))
        ttk.Entry(master, textvariable=self.country_var).grid(row=1, column=1, padx=6, pady=6)

        ttk.Label(master, text="Birth Year:").grid(row=2, column=0, sticky="e", padx=6, pady=6)
        self.birth_var = tk.StringVar(value=str(self.initial.get("birth_year", "") or ""))
        ttk.Entry(master, textvariable=self.birth_var).grid(row=2, column=1, padx=6, pady=6)

        ttk.Label(master, text="Email:").grid(row=3, column=0, sticky="e", padx=6, pady=6)
        self.email_var = tk.StringVar(value=self.initial.get("email", ""))
        ttk.Entry(master, textvariable=self.email_var).grid(row=3, column=1, padx=6, pady=6)

        ttk.Label(master, text="Bio:").grid(row=4, column=0, sticky="ne", padx=6, pady=6)
        self.bio_text = tk.Text(master, width=40, height=6)
        self.bio_text.grid(row=4, column=1, padx=6, pady=6)
        self.bio_text.insert("1.0", self.initial.get("bio", ""))

        return master

    def validate(self):
        # Basic validation
        if not self.name_var.get().strip():
            messagebox.showwarning("Validation", "Author name is required.")
            return False
        # birth year optional but if provided must be integer
        by = self.birth_var.get().strip()
        if by:
            try:
                int(by)
            except ValueError:
                messagebox.showwarning("Validation", "Birth year must be an integer.")
                return False
        return True

    def apply(self):
        data = {
            "name": self.name_var.get().strip(),
            "country": self.country_var.get().strip() or None,
            "birth_year": int(self.birth_var.get()) if self.birth_var.get().strip() else None,
            "email": self.email_var.get().strip() or None,
            "bio": self.bio_text.get("1.0", "end").strip() or None
        }
        # remove keys with None to avoid sending empty values
        self.result = {k: v for k, v in data.items() if v is not None}


class ManageAuthorsView(tk.Frame):
    """
    Admin UI to Manage Authors (list, add, edit, delete).
    """

    def __init__(self, parent, go_back=None):
        super().__init__(parent)
        self.parent = parent
        self.go_back = go_back
        self.client = AuthorsClient()

        self.pack(fill="both", expand=True)
        self._row_map = {}
        self.build_ui()
        self.load_authors()

    def build_ui(self):
        header = tk.Frame(self)
        header.pack(fill="x", padx=10, pady=8)

        tk.Label(header, text="Manage Authors", font=("Arial", 16, "bold")).pack(side="left")

        btn_frame = tk.Frame(header)
        btn_frame.pack(side="right")
        tk.Button(btn_frame, text="Add Author", command=self.add_author).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Edit Author", command=self.edit_selected).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Delete Author", command=self.delete_selected).pack(side="left", padx=4)
        if self.go_back:
            tk.Button(btn_frame, text="Back", command=self.go_back).pack(side="left", padx=4)

        # Treeview
        cols = ("author_id", "name", "country", "birth_year")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c.replace("_", " ").title())
            self.tree.column(c, width=140, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=10, pady=(0,10))

        # bind double-click
        self.tree.bind("<Double-1>", self.on_double)

        # scrollbar
        sy = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        sy.place(relx=0.985, rely=0.12, relheight=0.75)
        self.tree.configure(yscrollcommand=sy.set)

    def load_authors(self):
        self.tree.delete(*self.tree.get_children())
        self._row_map.clear()
        authors = self.client.get_all() or []
        for a in authors:
            vals = (
                a.get("author_id"),
                a.get("full_name", ""),
                a.get("country", ""),
                a.get("birth_year", "")
            )
            iid = self.tree.insert("", "end", values=vals)
            self._row_map[iid] = a

    def get_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No selection", "Please select an author.")
            return None, None
        iid = sel[0]
        return iid, self._row_map.get(iid)

    def add_author(self):
        dlg = AuthorFormDialog(self, title="Add Author")
        if getattr(dlg, "result", None):
            created = self.client.add(dlg.result)
            if created:
                messagebox.showinfo("Success", "Author added.")
                self.load_authors()
            else:
                messagebox.showerror("Error", "Failed to add author.")

    def edit_selected(self):
        iid, record = self.get_selected()
        if not record:
            return
        initial = {
            "name": record.get("name"),
            "country": record.get("country"),
            "birth_year": record.get("birth_year"),
            "email": record.get("email"),
            "bio": record.get("bio")
        }
        dlg = AuthorFormDialog(self, title="Edit Author", initial=initial)
        if getattr(dlg, "result", None):
            updated = self.client.update(record.get("author_id"), dlg.result)
            if updated:
                messagebox.showinfo("Success", "Author updated.")
                self.load_authors()
            else:
                messagebox.showerror("Error", "Failed to update author.")

    def delete_selected(self):
        iid, record = self.get_selected()
        if not record:
            return
        if not messagebox.askyesno("Confirm", f"Delete author '{record.get('name')}'?"):
            return
        res = self.client.delete(record.get("author_id"))
        if res:
            messagebox.showinfo("Deleted", "Author deleted.")
            self.load_authors()
        else:
            messagebox.showerror("Error", "Failed to delete author.")

    def on_double(self, event):
        iid = self.tree.identify_row(event.y)
        if not iid:
            return
        record = self._row_map.get(iid)
        if not record:
            return
        # show details popup if available
        try:
            DetailsPopup(self, "Authors", record)
        except Exception:
            # fallback to edit
            self.edit_selected()
