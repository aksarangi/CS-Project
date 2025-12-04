# frontend/views/reports_view.py

import tkinter as tk
from tkinter import ttk, messagebox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from frontend.api_client import (
    ReportsClient,
    BooksClient,
    SalesClient
)


class ReportsView(tk.Frame):
    """
    Reports Dashboard for staff/admin.
    Provides:
        - Summary metrics
        - Top selling books chart
        - Revenue last 7 days chart
        - Top selling books table
        - Recent sales table
    """

    def __init__(self, root, user_role, go_back):
        super().__init__(root)

        self.root = root
        self.user_role = user_role
        self.go_back = go_back

        # API Clients
        self.reports = ReportsClient()
        self.books = BooksClient()
        self.sales = SalesClient()

        # Configure layout
        self.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1)

        self.rowconfigure(1, weight=0)   # Summary row
        self.rowconfigure(2, weight=1)   # Charts row
        self.rowconfigure(3, weight=2)   # Tables row

        # Build UI
        self.build_header()
        self.build_summary_cards()
        self.build_charts()
        self.build_tables()

        # Load dynamic data
        self.load_reports()

    # ==========================================================
    #  HEADER SECTION
    # ==========================================================
    def build_header(self):
        header = tk.Frame(self, bg="#f0f0f0", pady=15)
        header.grid(row=0, column=0, sticky="ew")

        tk.Label(
            header,
            text="📊 Reports & Analytics",
            font=("Arial", 22, "bold"),
            bg="#f0f0f0"
        ).pack(side="left", padx=20)

        ttk.Button(header, text="← Back", command=self.go_back)\
            .pack(side="right", padx=20)

    # ==========================================================
    #  SUMMARY CARDS
    # ==========================================================
    def build_summary_cards(self):
        self.summary_frame = tk.Frame(self, padx=15, pady=10)
        self.summary_frame.grid(row=1, column=0, sticky="ew")

        # 6 equal-size columns
        for i in range(6):
            self.summary_frame.columnconfigure(i, weight=1)

        card_specs = [
            ("Total Books", "total_books"),
            ("Total Authors", "total_authors"),
            ("Total Publishers", "total_publishers"),
            ("Total Sales", "total_sales"),
            ("Today's Revenue", "today_revenue"),
            ("Low Stock Items", "low_stock"),
        ]

        self.cards = {}

        for col, (title, key) in enumerate(card_specs):
            card = tk.Frame(
                self.summary_frame,
                bg="white",
                bd=1,
                relief="solid",
                padx=10,
                pady=10
            )
            card.grid(row=0, column=col, padx=5, pady=5, sticky="nsew")

            tk.Label(card, text=title, font=("Arial", 11, "bold"), bg="white")\
                .pack()
            value_lbl = tk.Label(
                card, text="0", font=("Arial", 16, "bold"), fg="#333", bg="white"
            )
            value_lbl.pack(pady=5)
            self.cards[key] = value_lbl

    # ==========================================================
    #  CHARTS SECTION
    # ==========================================================
    def build_charts(self):
        self.charts_frame = tk.Frame(self, padx=20, pady=10)
        self.charts_frame.grid(row=2, column=0, sticky="nsew")

        self.charts_frame.columnconfigure(0, weight=0)
        self.charts_frame.columnconfigure(1, weight=0)

        self.sales_chart_canvas = None

    # ==========================================================
    #  TABLE SECTION
    # ==========================================================
    def build_tables(self):
        container = tk.Frame(self)
        container.grid(row=3, column=0, sticky="nsew", padx=15, pady=10)

        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(1, weight=1)

        tk.Label(container, text="Top Selling Books", font=("Arial", 15, "bold"))\
            .grid(row=0, column=0, sticky="w", pady=5)

        self.top_books_tree = self.create_table(container)
        self.top_books_tree.grid(row=1, column=0, sticky="nsew", padx=5)

    def create_table(self, parent):
        tree = ttk.Treeview(parent, columns=[], show="headings", height=14)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)

        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=5, sticky="ns")

        return tree

    # ==========================================================
    #  LOAD ALL DATA
    # ==========================================================
    def load_reports(self):
        # Load summary metrics
        summary = self.reports.get_summary()

        if not summary:
            messagebox.showerror("Error", "Failed to load report summary.")
            return

        for key, lbl in self.cards.items():
            for data in summary:
                lbl.config(text=data.get(key, "0") )

        # Load charts
        self.draw_sales_chart()

        # Load tables
        top_books = self.reports.get_top_books()
        self.populate_table(
            self.top_books_tree,
            ["book_id", "title", "author_name", "total_sold"],
            top_books
        )


    # ==========================================================
    #  CHART GENERATORS
    # ==========================================================
    def draw_sales_chart(self):
        """
        Bar chart: Top 5 selling books.
        """
        data = self.reports.get_top_books()[:5]

        titles = [d["title"] for d in data]
        units = [d["total_sold"] for d in data]

        fig = Figure(figsize=(3.5, 2.2), dpi=100)
        ax = fig.add_subplot(111)

        ax.bar(titles, units)
        ax.set_title("Top 5 Selling Books")
        ax.set_ylabel("Units Sold")
        ax.tick_params(axis="x", rotation=30)

        if self.sales_chart_canvas:
            self.sales_chart_canvas.get_tk_widget().destroy()

        self.sales_chart_canvas = FigureCanvasTkAgg(fig, master=self.charts_frame)
        self.sales_chart_canvas.draw()
        self.sales_chart_canvas.get_tk_widget()\
            .grid(row=0, column=0, sticky="nsew", padx=10)

    
    # ==========================================================
    #  TABLE POPULATION
    # ==========================================================
    def populate_table(self, tree, columns, records):
        tree["columns"] = columns

        for col in columns:
            tree.heading(col, text=col.upper())
            tree.column(col, width=140, anchor="w")

        for row in tree.get_children():
            tree.delete(row)

        for record in records:
            tree.insert("", "end", values=[record.get(c, "") for c in columns])
