# frontend/views/details_popup.py

import tkinter as tk
from tkinter import ttk, scrolledtext

class DetailsPopup(tk.Toplevel):
    """
    Universal details popup for entities: Books, Authors, Publishers (and more).
    Usage:
        DetailsPopup(parent, entity_type, record_dict)
    entity_type: "Books" | "Authors" | "Publishers" (string)
    record_dict: dictionary returned by api_client for that row
    """

    # Nice human-readable column labels for common fields
    FIELD_LABELS = {
        "book_id": "Book ID",
        "title": "Title",
        "author_name": "Author",
        "author_id": "Author ID",
        "publisher_name": "Publisher",
        "publisher_id": "Publisher ID",
        "price": "Price",
        "stock": "Stock",
        "copies_available": "Available",
        "copies_total": "Total Copies",
        "description": "Description",
        "isbn": "ISBN",
        "genre": "Genre",
        "publication_year": "Publication Year",
        "author_id": "Author ID",
        "author_name": "Author",
        "author_bio": "Bio",
        "author_country": "Country",
        "author_birth_year": "Birth Year",
        "author_death_year": "Death Year",
        "author_email": "Email",
        "publisher_id": "Publisher ID",
        "publisher_name": "Publisher",
        "location": "Location",
        "contact_email": "Contact Email",
        "phone": "Phone",
        "category_id": "Category ID",
        "name": "Name",
        "full_name": "Full Name"
    }

    def __init__(self, parent, entity, record):
        super().__init__(parent)
        self.parent = parent
        self.entity = entity
        self.record = record or {}
        self.title(f"{entity} Details")

        # Make modal (grab) so user must close it
        self.transient(parent)
        self.grab_set()

        # Basic sizing and centering
        width, height = 600, 420
        self.geometry(f"{width}x{height}")
        try:
            # center on parent if possible
            px = parent.winfo_rootx()
            py = parent.winfo_rooty()
            pw = parent.winfo_width()
            ph = parent.winfo_height()
            x = px + (pw - width) // 2
            y = py + (ph - height) // 2
            self.geometry(f"+{x}+{y}")
        except Exception:
            pass

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.build_ui()

    def build_ui(self):
        frame = ttk.Frame(self, padding=(12, 12, 12, 12))
        frame.grid(sticky="nsew", padx=6, pady=6)
        frame.columnconfigure(1, weight=1)

        # Header
        heading = ttk.Label(frame, text=f"{self.entity} Details", font=("Arial", 16, "bold"))
        heading.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

        # We'll display fields in two columns (label / value).
        # Description-like fields get a scrolledtext widget.
        row = 1
        for key, value in self._sorted_fields():
            label = self.FIELD_LABELS.get(key, key.replace("_", " ").title())
            if key in ("description", "bio"):
                ttk.Label(frame, text=label + ":", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky="nw", pady=6)
                txt = scrolledtext.ScrolledText(frame, height=8, wrap="word")
                txt.grid(row=row, column=1, sticky="nsew", pady=6)
                txt.insert("1.0", str(value or ""))
                txt.configure(state="disabled")
            else:
                ttk.Label(frame, text=label + ":", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky="w", pady=4, padx=(0,8))
                val = ttk.Label(frame, text=str(value) if value is not None else "")
                val.grid(row=row, column=1, sticky="w", pady=4)
            row += 1

        # Footer - Close button
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=row, column=0, columnspan=2, sticky="e", pady=(12,0))
        ttk.Button(btn_frame, text="Close", command=self.close).pack()

    def _sorted_fields(self):
        """
        Decide which fields to show and ordering.
        Prefer common identity fields first.
        Returns list of (key, value) tuples.
        """
        preferred_order = [
            "book_id", "title", "author_name", "author_id", "publisher_name", "publisher_id",
            "price", "stock", "copies_available", "copies_total", "isbn", "genre", "publication_year",
            "name", "full_name", "author_bio", "bio", "country", "birth_year", "location", "contact_email",
            "phone", "description"
        ]

        # Build list of keys present in record
        keys = [k for k in preferred_order if k in self.record]
        # add any other keys not in preferred_order
        other_keys = [k for k in self.record.keys() if k not in keys]
        keys.extend(other_keys)

        return [(k, self.record.get(k)) for k in keys]

    def close(self):
        self.grab_release()
        self.destroy()
