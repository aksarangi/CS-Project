# 📚 Bookstore Backend API Documentation

All API classes return JSON objects with a standard structure:

```json
{
  "status": "success|error",
  "message": "Descriptive message",
  "data": {} , []
}
```
errors return only
```json
{
  "status": "error",
  "message": "Error message"
}
```
---

## 1. **CategoriesAPI**

Manage book categories.  
Returns refers to the `data:` value in the standard json return statement.

| Method                               | Description                   | Parameters                                                             | Returns                  | Response format |
| ------------------------------------ | ----------------------------- | ---------------------------------------------------------------------- | ------------------------ | ---------- |
| `get_all()`                         | Fetch all categories.         | NONE         | List of JSON-serializable dictionaries of all categories |`[{"category_id": 1,"name": "Fiction","description": "Fictional books"}]`|
| `get_by_id(category_id)`             | Fetch a single category by ID | `category_id`                                                          | JSON-serializable dictionary of categotry details|`{"category_id": 3,"name": "Science","description": "Science-related books"}`|
| `add(category_data)`                 | Add a new category            | `category_data`: `{name: str (required), description: str (optional)}` |JSON-serializable dictionary of the new category   |`{"category_id": 12,"name": "Philosophy","description": "Books about philosophy"}`|
| `update(category_id, category_data)` | Update category fields        | `category_id`, `category_data`                                         | JSON-serializable dictionary of the updated category|`{"category_id": 12,"name": "Philosophy","description": "Books about philosophy"}`|
| `delete(category_id)`                | Delete a category             | `category_id`                                                          | category id of the deleted category|`12`|

---

## 2. **CustomersAPI**

Manage customers.

| Method                                        | Description                               | Parameters                                                                                               | Returns                    |Response Format|
| --------------------------------------------- | ----------------------------------------- | -------------------------------------------------------------------------------------------------------- | -------------------------- | ------------- |
| `get_all(search=None, city=None, state=None)` | Fetch all customers | NONE| List of JSON-serializable dictionaries of all customers|`[{"customer_id": 101,"full_name": "John Doe","email": "john@example.com","phone": "9876543210","address": "123 Street, City","created_at": "2025-01-10 14:22:00"}]`|
| `get_by_id(customer_id)`                      | Fetch a customer by ID                    | `customer_id`|JSON-serializable dictionary of the customer details|`{"customer_id": 101,"full_name": "John Doe","email": "john@example.com","phone": "9876543210","address": "123 Street, City","created_at": "2025-01-10 14:22:00"}`|
| `add(customer_data)`                          | Add a new customer                        | `customer_data`: `{full_name: str (required), email, phone, address, city, state, country, postal_code}` | JSON-serializable dictionary of the newly created customer details     |`{"customer_id": 101,"full_name": "John Doe","email": "john@example.com","phone": "9876543210","address": "123 Street","city": "Mumbai","state": "MH","country": "India","postal_code": "400001"}`|
| `update(customer_id, customer_data)`          | Update customer information               | `customer_id`, `customer_data`                                                                           | JSON-serializable dictionary of details of the updated customer|`{"customer_id": 101,"full_name": "John Doe","email": "john@example.com","phone": "9876543210","address": "123 Street","city": "Mumbai","state": "MH","country": "India","postal_code": "400001"}`|
| `delete(customer_id)`                         | Delete a customer                         | `customer_id`| Customer_id of deleted customer|`1`|
| `search_customers(by="any", value=None)`      | Flexible search                           | `by`: either of `'full_name'`, `'email'`, `'city'`, `'state'`, `'any'`; `value`| List of JSON-serializable dictionaries of matching customers |`[{"customer_id": 101,"full_name": "John Doe","email": "john@example.com","phone": "9876543210","address": "123 Main St","city": "Mumbai","state": "Maharashtra","country": "India","postal_code": "400001"},{"customer_id": 102,"full_name": "Jane Smith","email": "jane@example.com","phone": "9123456780","address": "456 Park Ave","city": "Delhi","state": "Delhi","country": "India","postal_code": "110001"}]`|

---

## 3. **OrdersAPI**

Manage orders.

| Method                                   | Description          | Parameters                                                                                       | Returns                 |
| ---------------------------------------- | -------------------- | ------------------------------------------------------------------------------------------------ | ----------------------- |
| `get_all()` | Fetch all orders     | NONE| List of JSON-serializable dictionaries of all orders|
| `get_by_id(order_id)`                    | Fetch a single order | `order_id`                                                                                       |JSON-serializable dictionary of order|
| `add(order_data)`                        | Add a new order      | `order_data`: `{customer_id: int, total_amount: float (optional), order_status: str (optional)}` |JSON-serializable dictionary of the newly created order|
| `update(order_id, updates)`              | Update order fields  | `order_id`, `updates`                                                                            | JSON-serializable dictionary of details of the updated order |
| `delete(order_id)`                       | Delete an order      | `order_id`                                                                                       | order id deleted order  |
| `search(by, query)`                      | Search orders        | `by`: either of `'order_id'`, `'customer_id'`, `'order_status'`, `'order_date'`; `query`                   | List of JSON-serializable dictionaries of matching orders |

---

## 4. **PaymentsAPI**

Manage payments.

| Method                                      | Description           | Parameters                                                                                       | Returns                      |
| ------------------------------------------- | --------------------- | ------------------------------------------------------------------------------------------------ | ---------------------------- |
| `search(field=None, value=None)`            | Search payments       | `field`: any payment column; `value`|List of JSON-serializable dictionaries of all payments|
| `add(payment_data)`                         | Add a new payment     | `payment_data`: `{order_id: int, amount: float, payment_method, payment_status, transaction_id}` | JSON-serializable dictionary of the newly created orderJSON-serializable dictionary of the newly created payment|
| `update_status(payment_id, payment_status)`| Update payment status | `payment_id`, `payment_status`: `'Success', 'Pending', 'Failed', 'Cancelled'`| JSON-serializable dictionary of details of the updated payment status|
| `delete(payment_id)`| Delete a payment| `payment_id`|payment id of payment order|

---

## 5. **PublishersAPI**

Manage publishers.

| Method                              | Description             | Parameters      | Returns    |
| ----------------------------------- | ----------------------- | --------------- | ---------- |
| `get_all()`                         | Fetch all publishers   | NONE            |List of JSON-serializable dictionaries of all publishers|
| `get_by_id(publisher_id)`| Fetch a publisher by ID | `publisher_id`|JSON-serializable dictionary of publisher|
| `add(publisher_data)`| Add a new publisher| `publisher_data`: `{name: str (required), location, contact_email, phone}`|JSON-serializable dictionary of newly created publisher|
| `update(publisher_id, publisher_data)`| Update publisher|`publisher_id`, `publisher_data`| JSON-serializable dictionary of updated publisher|
| `delete(publisher_id)`| Delete a publisher| `publisher_id`| publisher id of deleted publisher|
| `search_by(field, query)`| Dynamic search| `field`: either of `'name'`, `'location'`, `'contact_email'`, `'phone'`; `query`| List of JSON-serializable dictionaries of matching publishers |

---

## 6. **ReportsAPI**

Access reports for frontend visualization.  
**Note:** This API returns in a non standard format from that described above

| Method                            | Description                 | Parameters             | Returns                  | Response Format |
| --------------------------------- | --------------------------- | ---------------------- | ------------------------ | --------------- |
| `get_daily_sales()`               | Daily sales data            | None                   | JSON-serializable dictionary where each key is a date (YYYY-MM-DD), and the value contains a dictionary of the total number of orders and total sales for that date.| `{"2025-11-10": {"num_orders": 12, "total_sales": 3490.75},"2025-11-11": {"num_orders": 8, "total_sales": 2150.00},"2025-11-12": {"num_orders": 15, "total_sales": 5020.50}}`|
| `get_daily_sales_plot_data()`     | Chart-ready sales data      | None                   |Returns a tuple (or JSON array) containing two lists - A list of date strings and a list of total sales (floats) corresponding to each date.|`{"dates": ["2025-11-10", "2025-11-11", "2025-11-12"],"sales": [3490.75, 2150.00, 5020.50]}`|
| `get_top_selling_books(limit=10)` | Top-selling books           | `limit` (optional)     | Returns a list of the top-selling books ranked by total quantity soldReturns a list of the top-selling books ranked by total quantity sold |`[{"title": "Atomic Habits", "total_sold": 245},{"title": "The Alchemist", "total_sold": 198},{"title": "1984", "total_sold": 150},{"title": "Deep Work", "total_sold": 110},{"title": "Sapiens", "total_sold": 95}]`
| `get_current_stock()`             | Current stock of all books  | None                   | Returns a list of dictionaries, where each dictionary represents a book and includes its ID, title, stock quantity, category, publisher, and price. |`[{"book_id": 1, "title": "Atomic Habits", "stock": 45, "category": "Self-Help", "publisher": "Penguin", "price": 15.99},{"book_id": 2, "title": "The Alchemist", "stock": 32, "category": "Fiction", "publisher": "HarperCollins", "price": 12.50},{"book_id": 3, "title": "Sapiens", "stock": 20, "category": "History", "publisher": "Vintage", "price": 18.75}]`|
| `get_low_stock(threshold=10)`     | Low-stock books             | `threshold` (optional) | Returns a list of dictionaries, where each dictionary represents a book whose stock quantity is below the given threshold. The default threshold is 10. | `[{"book_id": 5, "title": "Deep Work", "stock": 7, "category": "Productivity", "publisher": "Grand Central", "price": 14.99},{"book_id": 9, "title": "Educated", "stock": 3, "category": "Memoir", "publisher": "Random House", "price": 13.50}]`|
| `get_category_stock_summary()`    | Category-wise stock summary | None | Returns a list of dictionaries, where each dictionary represents a book category with its total number of books and total stock count. | `[{"category": "Fiction", "num_books": 25, "total_stock": 320},{"category": "Self-Help", "num_books": 18, "total_stock": 210},{"category": "History", "num_books": 10, "total_stock": 95}]`|

---

## 7. **StaffAPI**

Manage staff/admin users.

| Method                             | Description           | Parameters| Returns|Response format|
| ---------------------------------- | --------------------- | -------------------------------|----------------------------- | ------------------- |
| `get_all()`| Fetch all staff users | NONE| list of dictionaries, where each dictionary represents a staff member’s details such as ID, username, full name, role, email, and creation date.|`[{"staff_id": 1, "username": "admin", "full_name": "Alice Johnson", "role": "Manager", "email": "alice@example.com", "created_at": "2024-09-15T10:20:00"},{"staff_id": 2, "username": "jdoe", "full_name": "John Doe", "role": "Sales", "email": "john@example.com", "created_at": "2024-10-05T14:30:00"}]` |
| `get_by_id(staff_id)`| Fetch a staff member  | `staff_id`| JSON-serializable dictionary containing the details of a single staff member identified by the given staff_id|`{"staff_id": 2,"username": "jdoe","full_name": "John Doe","role": "Sales","email": "john@example.com","created_at": "2024-10-05T14:30:00"}`|
| `add(staff_data)`| Add staff member| `staff_data`: `{username, password, role, full_name, email}` | JSON-serializable dictionary containing the newly created staff record. |`{"staff_id": 7,"username": "msmith","full_name": "Mary Smith","role": "Clerk","email": "mary@example.com","created_at": "2024-11-13T09:20:00"}`|
| `update(staff_id, staff_data)`     | Update staff          | `staff_id`, `staff_data`| JSON-serializable dictionary containing the updated staff record.|`{"staff_id": 7,"username": "msmith","full_name": "Mary Smith","role": "Manager","email": "mary@example.com","created_at": "2024-11-13T09:20:00"}`|
| `delete(staff_id)`                 | Delete staff          | `staff_id`| staff id of deleted staff|`7`|
| `authenticate(username, password)` | Login authentication  | `username`, `password`| JSON-serializable dictionary containing the staff ID and role upon successful authentication.   |`{"staff_id": 2,"role": "Manager"}`|
| `search(by, query)`| Dynamic search        | `by`:either of `'username', 'full_name', 'role', 'email'`; `query`          | list of dictionaries, where each dictionary contains details of a matching staff member.|`[{"staff_id": 2, "username": "jdoe", "full_name": "John Doe", "role": "Sales", "email": "john@example.com", "created_at": "2024-10-05T14:30:00"},{"staff_id": 5, "username": "johnny", "full_name": "Johnny Harper", "role": "Support", "email": "johnny@example.com", "created_at": "2024-09-22T11:15:00"}]`|

---

## 8. **AuthorsAPI**

Manage authors.

| Method                           | Description        | Parameters                           | Returns              |Response format|
| -------------------------------- | ------------------ | ------------------------------------ | -------------------- | ------------- |
| `get_all()`                      | Fetch all authors  | None                                 | list of dictionaries, where each dictionary represents an author’s details.|`[{"author_id": 1, "name": "George Orwell", "country": "United Kingdom", "birth_year": 1903},{"author_id": 2, "name": "Jane Austen", "country": "United Kingdom", "birth_year": 1775}]`|
| `get_by_id(author_id)`           | Fetch author by ID | `author_id`                          | JSON-serializable dictionary containing the author’s details |`{"author_id": 1,"name": "George Orwell","country": "United Kingdom","birth_year": 1903}`|
| `add(author_data)`               | Add author         | `{name: str (required), bio, email}` | JSON-serializable dictionary containing the newly added author's information |`{"author_id": 12,"full_name": "Haruki Murakami","country": "Japan","birth_year": 1949,"death_year": null,"bio": "Japanese writer known for surreal and contemporary fiction."}`|
| `update(author_id, author_data)` | Update author      | `author_id`, `author_data`           | JSON-serializable dictionary containing the updated author's information |`{"author_id": 12,"full_name": "Haruki Murakami","country": "Japan","birth_year": 1949,"death_year": null,"bio": "Renowned Japanese novelist, essayist, and translator."}`|
| `delete(author_id)`              | Delete author      | `author_id`                          | author id of deleted author |`7`|
| `search_by(field, query)`        | Dynamic search     | `'name', 'bio', 'email'`; `query`    | list of dictionaries, where each dictionary represents an author record. |`[{"author_id": 5,"full_name": "Vikram Seth","country": "India","birth_year": 1952,"death_year": null,"bio": "Indian novelist and poet, author of 'A Suitable Boy'."},{"author_id": 9,"full_name": "Vikram Chandra","country": "India","birth_year": 1961,"death_year": null,"bio": "Indian-American writer known for 'Sacred Games'."}]`|

---

## 9. **BooksAPI**

Manage books.

| Method                                                   | Description      | Parameters| Returns  |Response format|
| -------------------------------------------------------- | ---------------- | ------------------------------------ | --------------|---|
| `get_all()` | Fetch all books  | NONE   | list of dictionaries, where each dictionary represents a book’s details.|`[{"book_id": 12,"title": "A Suitable Boy","author_id": 5,"publisher_id": 3,"year_published": 1993,"genre": "Fiction","copies_total": 10,"copies_available": 4,"author_name": "Vikram Seth","publisher_name": "Penguin Books"},{"book_id": 18,"title": "The Guide","author_id": 7,"publisher_id": 4,"year_published": 1958,"genre": "Novel","copies_total": 6,"copies_available": 2,"author_name": "R. K. Narayan","publisher_name": "Indian Thought Publications"}]`|
| `get_by_id(book_id)`                                     | Fetch a book by ID     | `book_id`          | JSON-serializable dictionary containing the book details        |`{"book_id": 12,"title": "A Suitable Boy","author_id": 5,"publisher_id": 3,"year_published": 1993,"genre": "Fiction","copies_total": 10,"copies_available": 4,"author_name": "Vikram Seth","publisher_name": "Penguin Books"}`|
| `add(book_data)`                                         | Add a new book   | `{title: str, category_id: int, author_id: int, price, stock, publisher_id, description}` | JSON-serializable dictionary containing the newly added book information |`{"book_id": 42,"title": "The God of Small Things","author_id": 7,"publisher_id": 4,"price": 299.0,"isbn": "9780670083389","genre": "Fiction","publication_year": 1997,"language": "English","stock": 12,"description": "A novel by Arundhati Roy."}`|
| `update(book_id, book_data)`                             | Update book info | `book_id`, `book_data`                  | JSON-serializable dictionary containing the updated author's information|`{"book_id": 42,"title": "Updated Title","author_id": 7,"publisher_id": 4,"price": 350.0,"isbn": "9780670083389","genre": "Fiction","publication_year": 1997,"language": "English","stock": 15,"description": "Revised description."}`|
| `delete(book_id)`                                        | Delete a book    | `book_id`                                | book id of deleted book    |`88`|
| `search_by(field, query)`                                | Dynamic search   | `'title', 'description', 'isbn', 'publisher_id', 'author_id', 'category_id'`; `query`     | list of dictionaries, where each dictionary represents an book record |`[{"book_id": 12,"title": "Python Basics","isbn": "9781234567890","author_id": 3,"publisher_id": 5,"genre": "Programming","publication_year": 2021,"language": "English","price": 499.0,"stock": 12,"description": "Introductory Python book","author_name": "John Doe","publisher_name": "TechBooks Publishing"}]`|

---

## 💡 Notes for Frontend Developers

1. **Consistent JSON structure**: Every response includes `status`, `message`, and `data`, but errors include only `status` and `message`.
2. **Search endpoints** support partial matches hence query string can be passed plain.
3. **Dates and prices** are formatted for easy display.
4. **Foreign key fields** (`category_id`, `author_id`, `publisher_id`) must match existing records.
5. **Staff authentication** returns `staff_id` and `role`, useful for role-based access.
6. **Payments** are validated to prevent overpayment.
7. **ReportsAPI** provides precomputed datasets for charts, dashboards, and summaries.

---

This documentation provides a **complete roadmap** for building a GUI frontend: forms, tables, filters, reports, and dashboards for books, authors, categories, orders, payments, publishers, staff, and inventory management.

It’s beginner-friendly, yet detailed enough for professional use.





