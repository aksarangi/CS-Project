# frontend/views/admin/manage_books_view.py

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from frontend.api_client import BooksClient
from frontend.utils import format_currency, truncate_text

class BookFormDialog(simpledialog.Dialog):
    """
    Generic modal dialog for Add / Edit Book.
    On OK, self.result is a dict of book data (not containing book_id for Add).
    """
    def __init__(self, parent, title="Book", initial=None):
        self.initial = initial or {}
        super().__init__(parent, title)

    def body(self, master):
        # Build form fields
        ttk.Label(master, text="Title:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.title_var = tk.StringVar(value=self.initial.get("title", ""))
        ttk.Entry(master, textvariable=self.title_var, width=50).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(master, text="Author ID:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.author_id_var = tk.StringVar(value=str(self.initial.get("author_id", "") or ""))
        ttk.Entry(master, textvariable=self.author_id_var).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(master, text="Publisher ID:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.publisher_id_var = tk.StringVar(value=str(self.initial.get("publisher_id", "") or ""))
        ttk.Entry(master, textvariable=self.publisher_id_var).grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(master, text="Category ID:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.category_id_var = tk.StringVar(value=str(self.initial.get("category_id", "") or ""))
        ttk.Entry(master, textvariable=self.category_id_var).grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(master, text="Price:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        self.price_var = tk.StringVar(value=str(self.initial.get("price", "") or "0.0"))
        ttk.Entry(master, textvariable=self.price_var).grid(row=4, column=1, padx=5, pady=5)

        ttk.Label(master, text="Stock:").grid(row=5, column=0, sticky="e", padx=5, pady=5)
        self.stock_var = tk.StringVar(value=str(self.initial.get("stock", "") or "0"))
        ttk.Entry(master, textvariable=self.stock_var).grid(row=5, column=1, padx=5, pady=5)

        ttk.Label(master, text="ISBN:").grid(row=6, column=0, sticky="e", padx=5, pady=5)
        self.isbn_var = tk.StringVar(value=self.initial.get("isbn", ""))
        ttk.Entry(master, textvariable=self.isbn_var).grid(row=6, column=1, padx=5, pady=5)

        ttk.Label(master, text="Description:").grid(row=7, column=0, sticky="ne", padx=5, pady=5)
        self.desc_text = tk.Text(master, width=40, height=6)
        self.desc_text.grid(row=7, column=1, padx=5, pady=5)
        self.desc_text.insert("1.0", self.initial.get("description", ""))

        return master

    def validate(self):
        # Basic validation
        if not self.title_var.get().strip():
            messagebox.showwarning("Validation", "Title is required.")
            return False
        try:
            float(self.price_var.get())
            int(self.stock_var.get())
        except Exception:
            messagebox.showwarning("Validation", "Price must be number and stock must be integer.")
            return False
        return True

    def apply(self):
        # Build result dict
        data = {
            "title": self.title_var.get().strip(),
            "author_id": int(self.author_id_var.get()) if self.author_id_var.get().strip() else None,
            "publisher_id": int(self.publisher_id_var.get()) if self.publisher_id_var.get().strip() else None,
            "category_id": int(self.category_id_var.get()) if self.category_id_var.get().strip() else None,
            "price": float(self.price_var.get()),
            "stock": int(self.stock_var.get()),
            "isbn": self.isbn_var.get().strip(),
            "description": self.desc_text.get("1.0", "end").strip()
        }
        # Remove None values to avoid sending nulls where not desired
        self.result = {k: v for k, v in data.items() if v is not None}


class ManageBooksView(tk.Frame):
    """
    Admin view to list/add/edit/delete books.
    """

    def __init__(self, parent, go_back=None):
        super().__init__(parent)
        self.parent = parent
        self.go_back = go_back
        self.client = BooksClient()

        self.pack(fill="both", expand=True)
        self.build_ui()
        self.load_books()

    def build_ui(self):
        # Header + actions
        header = tk.Frame(self)
        header.pack(fill="x", padx=10, pady=8)
        tk.Label(header, text="Manage Books", font=("Arial", 16, "bold")).pack(side="left")
        btn_frame = tk.Frame(header)
        btn_frame.pack(side="right")

        tk.Button(btn_frame, text="Add Book", command=self.add_book).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Edit Book", command=self.edit_selected).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Delete Book", command=self.delete_selected).pack(side="left", padx=5)
        if self.go_back:
            tk.Button(btn_frame, text="Back", command=self.go_back).pack(side="left", padx=5)

        # Table
        cols = ("book_id", "title", "author_name", "publisher_name", "price", "stock")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c.replace("_", " ").title())
            self.tree.column(c, width=140, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=10, pady=(0,10))

        # store row mapping
        self._row_map = {}

        # double click opens details (reuse existing detail popup if you have it)
        self.tree.bind("<Double-1>", self.on_double)

        # Scrollbars
        sy = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        sy.place(relx=0.985, rely=0.12, relheight=0.75)
        self.tree.configure(yscrollcommand=sy.set)

    def load_books(self):
        self.tree.delete(*self.tree.get_children())
        books = self.client.get_all() or []
        for b in books:
            vals = (
                b.get("book_id"),
                truncate_text(b.get("title", ""), 60),
                b.get("author_name", ""),
                b.get("publisher_name", ""),
                format_currency(b.get("price", 0)),
                b.get("copies_available", 0)
            )
            iid = self.tree.insert("", "end", values=vals)
            self._row_map[iid] = b

    def get_selected_record(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No selection", "Please select a book.")
            return None, None
        iid = sel[0]
        return iid, self._row_map.get(iid)

    def add_book(self):
        dlg = BookFormDialog(self, title="Add Book")
        if getattr(dlg, "result", None):
            created = self.client.add(dlg.result)
            if created:
                messagebox.showinfo("Success", "Book added.")
                self.load_books()
            else:
                messagebox.showerror("Error", "Failed to add book.")

    def edit_selected(self):
        iid, record = self.get_selected_record()
        if not record:
            return
        # Provide initial data shaped for the form
        initial = {
            "title": record.get("title"),
            "author_id": record.get("author_id"),
            "publisher_id": record.get("publisher_id"),
            "category_id": record.get("category_id"),
            "price": record.get("price"),
            "stock": record.get("copies_available") or record.get("stock") or 0,
            "isbn": record.get("isbn"),
            "description": record.get("description")
        }
        dlg = BookFormDialog(self, title="Edit Book", initial=initial)
        if getattr(dlg, "result", None):
            updated = self.client.update(record.get("book_id"), dlg.result)
            if updated:
                messagebox.showinfo("Success", "Book updated.")
                self.load_books()
            else:
                messagebox.showerror("Error", "Failed to update book.")

    def delete_selected(self):
        iid, record = self.get_selected_record()
        if not record:
            return
        if not messagebox.askyesno("Confirm", f"Delete book '{record.get('title')}'?"):
            return
        res = self.client.delete(record.get("book_id"))
        # backend returns deleted id or None; coerce to truthy
        if res:
            messagebox.showinfo("Deleted", "Book deleted.")
            self.load_books()
        else:
            messagebox.showerror("Error", "Failed to delete book.")

    def on_double(self, event):
        # open details or edit depending on role
        iid = self.tree.identify_row(event.y)
        if not iid:
            return
        record = self._row_map.get(iid)
        if not record:
            return
        # if you have DetailsPopup, show it; else open edit form
        try:
            from frontend.views.details_popup import DetailsPopup
            DetailsPopup(self, "Books", record)
        except Exception:
            # fallback to edit
            self.edit_selected()
