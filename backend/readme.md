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

| Method                               | Description                   | Parameters                                                             | Returns                  |
| ------------------------------------ | ----------------------------- | ---------------------------------------------------------------------- | ------------------------ |
| `get_all()`                         | Fetch all categories.         | NONE         | List of JSON-serializable dictionaries of all categories |
| `get_by_id(category_id)`             | Fetch a single category by ID | `category_id`                                                          | JSON-serializable dictionary of categotry details|
| `add(category_data)`                 | Add a new category            | `category_data`: `{name: str (required), description: str (optional)}` |JSON-serializable dictionary of the new category   |
| `update(category_id, category_data)` | Update category fields        | `category_id`, `category_data`                                         | JSON-serializable dictionary of the updated category         |
| `delete(category_id)`                | Delete a category             | `category_id`                                                          | category id of the deleted category|

---

## 2. **CustomersAPI**

Manage customers.

| Method                                        | Description                               | Parameters                                                                                               | Returns                    |
| --------------------------------------------- | ----------------------------------------- | -------------------------------------------------------------------------------------------------------- | -------------------------- |
| `get_all(search=None, city=None, state=None)` | Fetch all customers | NONE                                                                     | List of JSON-serializable dictionaries of all customers|
| `get_by_id(customer_id)`                      | Fetch a customer by ID                    | `customer_id`                                                                                            |JSON-serializable dictionary of the customer details|
| `add(customer_data)`                          | Add a new customer                        | `customer_data`: `{full_name: str (required), email, phone, address, city, state, country, postal_code}` | JSON-serializable dictionary of the newly created customer details     |
| `update(customer_id, customer_data)`          | Update customer information               | `customer_id`, `customer_data`                                                                           | JSON-serializable dictionary of details of the updated customer           |
| `delete(customer_id)`                         | Delete a customer                         | `customer_id`                                                                                            | Customer_id of deleted customer|
| `search_customers(by="any", value=None)`      | Flexible search                           | `by`: either of `'full_name'`, `'email'`, `'city'`, `'state'`, `'any'`; `value`| List of JSON-serializable dictionaries of matching customers |

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

| Method                                 | Description             | Parameters                                                                 | Returns                     |
| -------------------------------------- | ----------------------- | -------------------------------------------------------------------------- | --------------------------- |
| `get_all()`| Fetch all publishers| NONE|List of JSON-serializable dictionaries of all publishers|
| `get_by_id(publisher_id)`| Fetch a publisher by ID | `publisher_id`| Publisher object|
| `add(publisher_data)`| Add a new publisher| `publisher_data`: `{name: str (required), location, contact_email, phone}`| Newly created publisher|
| `update(publisher_id, publisher_data)`| Update publisher|`publisher_id`, `publisher_data`| Updated publisher|
| `delete(publisher_id)`| Delete a publisher| `publisher_id`| Success message|
| `search_by(field, query)`| Dynamic search| `field`: `'name'`, `'location'`, `'contact_email'`, `'phone'`; `query`| List of matching publishers |

---

## 6. **ReportsAPI**

Access reports for frontend visualization.

| Method                            | Description                 | Parameters             | Returns                  |
| --------------------------------- | --------------------------- | ---------------------- | ------------------------ |
| `get_daily_sales()`               | Daily sales data            | None                   | Daily sales summary      |
| `get_daily_sales_plot_data()`     | Chart-ready sales data      | None                   | Plot data                |
| `get_top_selling_books(limit=10)` | Top-selling books           | `limit` (optional)     | List of top books        |
| `get_current_stock()`             | Current stock of all books  | None                   | List of books with stock |
| `get_low_stock(threshold=10)`     | Low-stock books             | `threshold` (optional) | List of low-stock books  |
| `get_category_stock_summary()`    | Category-wise stock summary | None                   | Summary by category      |

---

## 7. **StaffAPI**

Manage staff/admin users.

| Method                             | Description           | Parameters                                                   | Returns             |
| ---------------------------------- | --------------------- | ------------------------------------------------------------ | ------------------- |
| `get_all(role=None)`               | Fetch all staff users | `role` (optional)                                            | List of staff       |
| `get_by_id(staff_id)`              | Fetch a staff member  | `staff_id`                                                   | Staff object        |
| `add(staff_data)`                  | Add staff member      | `staff_data`: `{username, password, role, full_name, email}` | Newly created staff |
| `update(staff_id, staff_data)`     | Update staff          | `staff_id`, `staff_data`                                     | Updated staff       |
| `delete(staff_id)`                 | Delete staff          | `staff_id`                                                   | Success message     |
| `authenticate(username, password)` | Login authentication  | `username`, `password`                                       | Staff ID and role   |
| `search(by, query)`                | Dynamic search        | `'username', 'full_name', 'role', 'email'`; `query`          | Matching staff list |

---

## 8. **AuthorsAPI**

Manage authors.

| Method                           | Description        | Parameters                           | Returns              |
| -------------------------------- | ------------------ | ------------------------------------ | -------------------- |
| `get_all(search=None)`           | Fetch all authors  | `search` (optional)                  | List of authors      |
| `get_by_id(author_id)`           | Fetch author by ID | `author_id`                          | Author object        |
| `add(author_data)`               | Add author         | `{name: str (required), bio, email}` | Newly created author |
| `update(author_id, author_data)` | Update author      | `author_id`, `author_data`           | Updated author       |
| `delete(author_id)`              | Delete author      | `author_id`                          | Success message      |
| `search_by(field, query)`        | Dynamic search     | `'name', 'bio', 'email'`; `query`    | Matching authors     |

---

## 9. **BooksAPI**

Manage books.

| Method                                                   | Description      | Parameters                                                                                | Returns            |
| -------------------------------------------------------- | ---------------- | ----------------------------------------------------------------------------------------- | ------------------ |
| `get_all(search=None, category_id=None, author_id=None)` | Fetch all books  | Optional filters                                                                          | List of books      |
| `get_by_id(book_id)`                                     | Fetch a book     | `book_id`                                                                                 | Book object        |
| `add(book_data)`                                         | Add a new book   | `{title: str, category_id: int, author_id: int, price, stock, publisher_id, description}` | Newly created book |
| `update(book_id, book_data)`                             | Update book info | `book_id`, `book_data`                                                                    | Updated book       |
| `delete(book_id)`                                        | Delete a book    | `book_id`                                                                                 | Success message    |
| `search_by(field, query)`                                | Dynamic search   | `'title', 'description', 'isbn', 'publisher_id', 'author_id', 'category_id'`; `query`     | Matching books     |

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



