# frontend/views/admin/manage_inventory_view.py

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from frontend.api_client import BooksClient, ReportsClient
from frontend.utils import format_currency
from frontend.views.details_popup import DetailsPopup


class ManageInventoryView(tk.Frame):
    """
    Inventory management view for Admin/Staff.
    Shows:
      - Current stock of all books
      - Low-stock filter
      - Ability to adjust stock levels
      - Book detail popup
    """

    def __init__(self, parent, go_back=None):
        super().__init__(parent)
        self.parent = parent
        self.go_back = go_back

        # API Clients
        self.reports = ReportsClient()   # For reading inventory & stock reports
        self.books = BooksClient()       # For updating stock

        self._row_map = {}

        self.pack(fill="both", expand=True)
        self.build_ui()
        self.load_stock()

    # ----------------------------------------------------------------------
    # UI SETUP
    # ----------------------------------------------------------------------
    def build_ui(self):
        # Top control bar
        control_frame = tk.Frame(self)
        control_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(control_frame, text="Inventory Management", font=("Helvetica", 16, "bold"))\
            .pack(side="left")

        # Buttons: Refresh / Low Stock / Back
        btn_frame = tk.Frame(control_frame)
        btn_frame.pack(side="right")

        ttk.Button(btn_frame, text="Refresh", command=self.load_stock).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Low Stock", command=self.show_low_stock).pack(side="left", padx=5)
        if self.go_back:
            ttk.Button(btn_frame, text="Back", command=self.go_back).pack(side="left", padx=5)

        # Table container
        table_frame = tk.Frame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("book_id", "title", "category", "publisher", "stock", "price")

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=20
        )

        self.tree.heading("book_id", text="ID")
        self.tree.heading("title", text="Title")
        self.tree.heading("category", text="Category")
        self.tree.heading("publisher", text="Publisher")
        self.tree.heading("stock", text="Stock")
        self.tree.heading("price", text="Price")

        self.tree.column("book_id", width=50, anchor="center")
        self.tree.column("title", width=200)
        self.tree.column("category", width=120)
        self.tree.column("publisher", width=120)
        self.tree.column("stock", width=80, anchor="center")
        self.tree.column("price", width=80, anchor="e")

        self.tree.pack(fill="both", expand=True)

        # Events
        self.tree.bind("<Double-1>", self.on_double_click)

    # ----------------------------------------------------------------------
    # DATA LOADING
    # ----------------------------------------------------------------------
    def load_stock(self):
        """Load full inventory using ReportsAPI."""
        self.tree.delete(*self.tree.get_children())
        self._row_map.clear()

        items = self.reports.get_current_stock() or []

        for item in items:
            iid = self.tree.insert(
                "",
                "end",
                values=(
                    item["book_id"],
                    item["title"],
                    item.get("category", ""),
                    item.get("publisher", ""),
                    item.get("stock", ""),
                    format_currency(item.get("price", 0)),
                )
            )
            self._row_map[iid] = item

    def show_low_stock(self):
        """Display only low-stock items using ReportsAPI."""
        threshold = simpledialog.askinteger(
            "Low Stock Threshold",
            "Show items with stock below:",
            minvalue=1,
            initialvalue=10
        )
        if threshold is None:
            return

        self.tree.delete(*self.tree.get_children())
        self._row_map.clear()

        items = self.reports.get_low_stock(threshold) or []

        for item in items:
            iid = self.tree.insert(
                "",
                "end",
                values=(
                    item["book_id"],
                    item["title"],
                    item.get("category", ""),
                    item.get("publisher", ""),
                    item.get("stock", ""),
                    format_currency(item.get("price", 0)),
                )
            )
            self._row_map[iid] = item

    # ----------------------------------------------------------------------
    # EVENTS & ACTIONS
    # ----------------------------------------------------------------------
    def on_double_click(self, event):
        """Open detail popup with option to adjust stock."""
        selected = self.tree.focus()
        if not selected:
            return

        record = self._row_map[selected]

        popup = DetailsPopup(
            self,
            title=f"Book: {record['title']}",
            fields=record,
            extra_actions=[("Adjust Stock", lambda: self.adjust_stock(record))]
        )
        popup.wait_window()

    def adjust_stock(self, record):
        """Open input dialog to update stock."""
        new = simpledialog.askinteger(
            "Adjust Stock",
            f"Enter new stock for '{record['title']}':",
            initialvalue=record.get("stock", 0),
            minvalue=0
        )
        if new is None:
            return

        updated = self.books.update(record["book_id"], {"stock": new})
        if not updated:
            messagebox.showerror("Error", "Failed to update stock.")
            return

        messagebox.showinfo("Success", "Stock updated successfully.")
        self.load_stock()
