# frontend/orders_view.py

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from frontend.api_client import OrdersClient, BooksClient
from frontend.app_state import AppState

class OrdersView(ttk.Frame):
    """
    Staff/Admin Orders View with cart persistence across page changes.
    """
    def __init__(self, parent,go_back):
        super().__init__(parent)
        self.app_state = AppState.get_instance()
        self.orders_api = OrdersClient()
        self.books_api = BooksClient()
        self.cart = self.app_state.cart  # Reference shared cart
        self.go_back=go_back

        self.pack(fill=tk.BOTH, expand=True)
        self.create_widgets()
        self.refresh_orders()

    def create_widgets(self):
        # Top buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="Add Order", command=self.add_order_popup).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="View Cart", command=self.view_cart_popup).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Refresh Orders", command=self.refresh_orders).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Back", command=self.go_back).pack(side=tk.LEFT, padx=5)
        ttk.Button(popup, text="Record Payment", command=submit_payment).pack(pady=10)
        ttk.Button(popup, text="Close", command=popup.destroy).pack(pady=5)


        # Orders table
        self.tree = ttk.Treeview(self, columns=("OrderID","Customer","Date","Total","Status"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor=tk.CENTER)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=5)

    def refresh_orders(self):
        self.tree.delete(*self.tree.get_children())
        response = self.orders_api.get_all()
        if response["status"] == "success":
            for order in response["data"]:
                self.tree.insert("", tk.END, values=(
                    order["order_id"],
                    order["customer_id"],
                    order["order_date"],
                    order["total_amount"],
                    order["status"]
                ))
        else:
            messagebox.showerror("Error", response.get("message","Failed to fetch orders"))

    def add_order_popup(self):
        popup = tk.Toplevel(self)
        popup.title("Add Order")
        popup.geometry("400x400")

        books = self.books_api.get_all()
        if not books:
            messagebox.showerror("Error", books.get("message","Failed to fetch books"))
            popup.destroy()
            return

        # List of books
        book_listbox = tk.Listbox(popup)
        book_map = {}  # index → book
        for idx, book in enumerate(books):
            book_listbox.insert(tk.END, f"{book['title']} (₹{book['price']}) [{book['stock']} in stock]")
            book_map[idx] = book
        book_listbox.pack(fill=tk.BOTH, expand=True, pady=5)

        def add_to_cart():
            selection = book_listbox.curselection()
            if not selection:
                messagebox.showwarning("Select Book", "Please select a book to add to cart.")
                return
            idx = selection[0]
            book = book_map[idx]
            quantity = simpledialog.askinteger("Quantity", f"Enter quantity for '{book['title']}' (max {book['stock']}):", minvalue=1, maxvalue=book['stock'])
            if quantity:
                if book["book_id"] in self.cart:
                    self.cart[book["book_id"]]["quantity"] += quantity
                else:
                    self.cart[book["book_id"]] = {
                        "title": book["title"],
                        "price": float(book["price"]),
                        "quantity": quantity
                    }
                messagebox.showinfo("Cart", f"Added {quantity} x {book['title']} to cart.")

        ttk.Button(popup, text="Add Selected to Cart", command=add_to_cart).pack(pady=5)
        ttk.Button(popup, text="Close", command=popup.destroy).pack(pady=5)

    def view_cart_popup(self):
        popup = tk.Toplevel(self)
        popup.title("Cart")
        popup.geometry("400x400")

        tree = ttk.Treeview(popup, columns=("Book","Price","Quantity","Subtotal"), show="headings")
        for col in tree["columns"]:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor=tk.CENTER)
        tree.pack(fill=tk.BOTH, expand=True, pady=5)

        def refresh_cart():
            tree.delete(*tree.get_children())
            total = 0
            for book_id, item in self.cart.items():
                subtotal = item["price"] * item["quantity"]
                tree.insert("", tk.END, values=(item["title"], item["price"], item["quantity"], subtotal))
                total += subtotal
            total_label.config(text=f"Total: ₹{total:.2f}")

        def remove_selected():
            selection = tree.selection()
            if not selection:
                return
            for sel in selection:
                title = tree.item(sel, "values")[0]
                for bid, item in list(self.cart.items()):
                    if item["title"] == title:
                        del self.cart[bid]
            refresh_cart()

        def finalize_order():
            if not self.cart:
                messagebox.showwarning("Cart Empty", "Cannot place an empty order.")
                return
            customer_id = simpledialog.askinteger("Customer ID", "Enter Customer ID for this order:")
            if not customer_id:
                return
            order_items = []
            total_amount = 0
            for book_id, item in self.cart.items():
                order_items.append({
                    "book_id": book_id,
                    "quantity": item["quantity"],
                    "price_each": item["price"]
                })
                total_amount += item["price"] * item["quantity"]

            order_data = {
                "customer_id": customer_id,
                "total_amount": total_amount,
                "order_status": "Pending",
                "items": order_items
            }
            response = self.orders_api.add(order_data)
            if response["status"] == "success":
                messagebox.showinfo("Success", f"Order {response['data']['order_id']} created successfully!")
                self.cart.clear()  # Clear shared cart
                refresh_cart()
                self.refresh_orders()
            else:
                messagebox.showerror("Error", response.get("message","Failed to create order"))

        total_label = ttk.Label(popup, text="Total: ₹0.00")
        total_label.pack(pady=5)
        refresh_cart()

        btn_frame = ttk.Frame(popup)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Remove Selected", command=remove_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Place Order", command=finalize_order).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Close", command=popup.destroy).pack(side=tk.LEFT, padx=5)

    def record_payment_popup(self):
        """
        Popup to record a payment for a selected order.
        """
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Select Order", "Please select an order first.")
            return

        # For simplicity, take the first selected order
        order_values = self.tree.item(selection[0], "values")
        order_id = int(order_values[0])
        order_total = float(order_values[3])  # total_amount

        popup = tk.Toplevel(self)
        popup.title(f"Record Payment for Order {order_id}")
        popup.geometry("300x250")

        ttk.Label(popup, text=f"Order ID: {order_id}").pack(pady=5)
        ttk.Label(popup, text=f"Order Total: ${order_total:.2f}").pack(pady=5)

        # Payment amount
        ttk.Label(popup, text="Payment Amount:").pack(pady=5)
        amount_var = tk.DoubleVar(value=order_total)
        amount_entry = ttk.Entry(popup, textvariable=amount_var)
        amount_entry.pack(pady=5)

        # Payment method
        ttk.Label(popup, text="Payment Method:").pack(pady=5)
        method_var = tk.StringVar(value="UPI")
        method_combo = ttk.Combobox(popup, textvariable=method_var, values=["UPI", "Card", "NetBanking", "Cash"], state="readonly")
        method_combo.pack(pady=5)

        # Transaction ID (optional)
        ttk.Label(popup, text="Transaction ID (optional):").pack(pady=5)
        txn_var = tk.StringVar()
        txn_entry = ttk.Entry(popup, textvariable=txn_var)
        txn_entry.pack(pady=5)

    def submit_payment():
        amount = amount_var.get()
        method = method_var.get()
        txn_id = txn_var.get() or None

        if amount <= 0:
            messagebox.showerror("Invalid Amount", "Payment amount must be greater than 0.")
            return

        response = self.orders_api.record_payment(
            order_id=order_id,
            amount=amount,
            method=method,
            status="Success",  # For school project, always mark as success
            transaction_id=txn_id
        )

        if response["status"] == "success":
            messagebox.showinfo("Success", f"Payment recorded for Order {order_id}.")
            popup.destroy()
        else:
            messagebox.showerror("Error", response.get("message", "Failed to record payment"))

