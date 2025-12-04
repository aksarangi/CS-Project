# frontend/views/home_search_view.py

import tkinter as tk
from tkinter import ttk

from frontend.api_client import (
    BooksClient, AuthorsClient, PublishersClient
)

from frontend.views.components.side_menu import SideMenu
from frontend.views.details_popup import DetailsPopup


class HomeSearchView(tk.Frame):
    """
    Universal Home/Search Page
    Displays books, authors, publishers based on search filters.
    """

    def __init__(self, root, user_role="customer", username="Guest"):
        super().__init__(root)

        self.root = root
        self.user_role = user_role
        self.username = username

        # API Clients
        self.books = BooksClient()
        self.authors = AuthorsClient()
        self.publishers = PublishersClient()

        # Full-record map: item_id → dict(record)
        self._row_data = {}

        # Layout
        self.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # --- SIDE MENU (staff/admin only) ---
        if self.user_role in ("staff", "admin"):
            self.side_menu = SideMenu(self, self.user_role, self.switch_page)
            self.side_menu.grid(row=0, column=0, sticky="nsw")
        else:
            self.side_menu = None

        # --- MAIN AREA ---
        self.main_area = tk.Frame(self)
        self.main_area.grid(row=0, column=1, sticky="nsew")
        self.main_area.columnconfigure(0, weight=1)
        self.main_area.rowconfigure(2, weight=1)
        self.active_page = None

        # Search fields per entity type
        self.search_fields = {
    "Books": ["title", "isbn", "genre", "language",
              "price", "description", "author", "publisher_name"],
    "Authors": ["full_name", "bio", "country"],
    "Publishers": ["name", "location", "contact_email", "phone"]
}


        # Table columns per entity type
        self.table_columns = {
            "Books": ["book_id", "title", "description", "author", "publisher_name", "genre", "price", "stock"],
            "Authors": ["author_id", "full_name", "country", "birth_year"],
            "Publishers": ["publisher_id", "name", "location", "contact_email"]
        }

        # Build UI
        self.build_header()
        self.build_search_panel()
        self.build_table()  # must come before column setup
        self.update_search_fields()  # sets columns and loads default data

    # ----------------------------------------------------
    # HEADER
    # ----------------------------------------------------
    def build_header(self):
        header = tk.Frame(self.main_area, pady=10)
        header.grid(row=0, column=0, sticky="ew")

        title = tk.Label(
            header,
            text=f"Book Shop Management — {self.username}",
            font=("Arial", 18, "bold")
        )
        title.pack(side="left", padx=10)

    # ----------------------------------------------------
    # SEARCH PANEL
    # ----------------------------------------------------
    def build_search_panel(self):
        panel = tk.Frame(self.main_area, pady=8)
        panel.grid(row=1, column=0, sticky="ew")
        panel.columnconfigure(5, weight=1)

        # Search For (entity)
        tk.Label(panel, text="Search For:").grid(row=0, column=0, padx=5)
        self.search_for_var = tk.StringVar(value="Books")
        self.search_for_menu = ttk.Combobox(
            panel, textvariable=self.search_for_var,
            values=["Books", "Authors", "Publishers"],
            state="readonly", width=14
        )
        self.search_for_menu.grid(row=0, column=1, padx=5)
        self.search_for_menu.bind("<<ComboboxSelected>>", lambda e: self.update_search_fields())

        # Search By (field)
        tk.Label(panel, text="Search By:").grid(row=0, column=2, padx=5)
        self.search_by_var = tk.StringVar()
        self.search_by_menu = ttk.Combobox(
            panel, textvariable=self.search_by_var,
            state="readonly", width=18
        )
        self.search_by_menu.grid(row=0, column=3, padx=5)

        # Search query input
        self.search_entry = ttk.Entry(panel, width=30)
        self.search_entry.grid(row=0, column=4, padx=5)

        # Search button
        ttk.Button(panel, text="Search", command=self.perform_search).grid(row=0, column=5, padx=5)

    # ----------------------------------------------------
    # TABLE
    # ----------------------------------------------------
    def build_table(self):
        container = tk.Frame(self.main_area)
        container.grid(row=2, column=0, sticky="nsew")
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)

        # Treeview
        self.tree = ttk.Treeview(container, columns=[], show="headings")
        self.tree.grid(row=0, column=0, sticky="nsew")

        # Scrollbar
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Double-click → Details popup
        self.tree.bind("<Double-1>", self.on_row_double_click)

    # ----------------------------------------------------
    # UPDATE SEARCH FIELDS
    # ----------------------------------------------------
    def update_search_fields(self):
        entity = self.search_for_var.get()
        fields = self.search_fields[entity]

        self.search_by_menu.configure(values=fields)
        self.search_by_var.set(fields[0])

        # Update table columns
        self.setup_table_columns(entity)

        # Load default listing
        self.load_default()

    # ----------------------------------------------------
    # SET TABLE COLUMNS
    # ----------------------------------------------------
    def setup_table_columns(self, entity):
        if not hasattr(self, "tree") or not self.tree:
            return  # safety check

        cols = self.table_columns[entity]
        self.tree.configure(columns=cols)

        for col in cols:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=140, anchor="w")

    # ----------------------------------------------------
    # LOAD DEFAULT LIST (Books by default)
    # ----------------------------------------------------
    def load_default(self):
        entity = self.search_for_var.get()

        if entity == "Books":
            data = self.books.get_all()
        elif entity == "Authors":
            data = self.authors.get_all()
        else:
            data = self.publishers.get_all()

        self.populate_table(data, entity)

    # ----------------------------------------------------
    # POPULATE TREEVIEW
    # ----------------------------------------------------
    def populate_table(self, records, entity):
        self._row_data.clear()
        for row in self.tree.get_children():
            self.tree.delete(row)

        if not records:
            return

        cols = self.table_columns[entity]

        for rec in records:
            values = [rec.get(col, "") for col in cols]
            iid = self.tree.insert("", "end", values=values)
            self._row_data[iid] = rec

    # ----------------------------------------------------
    # DOUBLE-CLICK → DETAILS POPUP
    # ----------------------------------------------------
    def on_row_double_click(self, event):
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return

        record = self._row_data.get(item_id)
        if not record:
            return

        entity = self.search_for_var.get()
        DetailsPopup(self, entity, record)

    # ----------------------------------------------------
    # PERFORM SEARCH
    # ----------------------------------------------------
    def perform_search(self):
        entity = self.search_for_var.get()
        field = self.search_by_var.get()
        query = self.search_entry.get().strip()

        if entity == "Books":
            data = self.books.search_by(field, query)
        elif entity == "Authors":
            data = self.authors.search_by(field, query)
        else:
            data = self.publishers.search_by(field, query)

        self.populate_table(data, entity)

    # ----------------------------------------------------
    # HANDLE PAGE SWITCH (from side menu)
    # ----------------------------------------------------
    def switch_page(self, page_id):
        """
        Called by SideMenu when user clicks a menu item.
        Swaps ONLY the main area, sidebar stays.
        """
        # 1. Clear main area
        for widget in self.main_area.winfo_children():
            widget.destroy()

        # 2. Load new page
        if page_id == "home":
            # reload search UI
            self.build_header()
            self.build_search_panel()
            self.build_table()
            self.update_search_fields()
            return

        elif page_id == "profile":
            from frontend.views.profile_view import ProfileView
            ProfileView(self.main_area, user={"role":self.user_role, "username":self.username}, go_back=self.go_back_to_home_area)

        elif page_id == "books":
            from frontend.views.admin.manage_books_view import ManageBooksView
            ManageBooksView(self.main_area, go_back=self.go_back_to_home_area)

        elif page_id == "authors":
            from frontend.views.admin.manage_authors_view import ManageAuthorsView
            ManageAuthorsView(self.main_area, go_back=self.go_back_to_home_area)

        elif page_id == "categories":
            from frontend.views.admin.manage_categories_view import ManageCategoriesView
            ManageCategoriesView(self.main_area, go_back=self.go_back_to_home_area)

        elif page_id == "reports":
            from frontend.views.reports_view import ReportsView
            ReportsView(self.main_area, user_role=self.user_role, go_back=self.go_back_to_home_area)

        elif page_id == "inventory":
            from frontend.views.admin.manage_inventory_view import ManageInventoryView
            ManageInventoryView(self.main_area, go_back=self.go_back_to_home_area)

        elif page_id == "publishers":
            from frontend.views.admin.manage_publishers_view import ManagePublishersView
            ManagePublishersView(self.main_area, go_back=self.go_back_to_home_area)

        else:
            tk.Label(self.main_area, text=f"Page '{page_id}' is not implemented.", font=("Arial", 16)).pack(pady=40)
                
    def go_back_to_home_area(self):
        """Used by subpages to return to the search screen."""
        self.switch_page("home")
