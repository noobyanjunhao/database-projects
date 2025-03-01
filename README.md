Flask E-Commerce Project
========================

IMPORTANT NOTE OF FIRST TIME USE
1. In first time running our app, you don't have to run the command line of this "$ flask --app flaskr init-db" becuase our database will automatically set up when you run the "flask -app flaskr run".
2. Also, in order to set up your configurations, please install all the dependecies our app need by running "pip install -r requirements.txt".

Overview
--------
This project is a web-based e-commerce application built using Flask. It supports user 
registration and login, product browsing, a shopping cart, and a checkout process that 
interacts with a backend SQLite database. The project has been developed with a focus on 
test-driven development and includes a suite of automated tests.

Team Members
------------
1. Team Lead: Yuqi (Dave) Wang
2. Backend Development Engineer 1: Bo Zhang
3. Backend Development Engineer 2: Junhao Yan
4. Test  Engineer: Ruohang Feng
5. Documentation Specialist: Boyu (Ethan) Shen

Testing and Development Approach
----------------------------------

1. conftest.py
### **Description of Tests**  
The `conftest.py` module provides the foundational test configuration for the Flask application. It sets up a controlled testing environment by initializing a temporary database, configuring the Flask test application, and providing reusable fixtures for authentication and request handling. These fixtures ensure that tests are isolated, consistent, and independent of the production database, enabling reliable execution of unit and integration tests.

### **Approach to Testing**  
1. **Flask Test Application Setup:**  
   - Uses a temporary SQLite database to ensure a clean and isolated test environment.  
   - Reads `data.sql` to populate the database with predefined test data.  
   - Configures the Flask app in testing mode with `"TESTING": True`.  

2. **Database Management:**  
   - Establishes a temporary database connection for each test session.  
   - Ensures the database is reset before and after each test to maintain consistency.  
   - Deletes the temporary database file after test execution.

3. **Test Client and CLI Runner:**  
   - Provides a `client` fixture that enables sending HTTP requests to the application without running the server.  
   - Uses a `runner` fixture to facilitate testing of Flask CLI commands.

4. **Authentication Fixtures:**  
   - `auth(client)`: A helper function that allows test cases to perform user logins.  
   - `auth_actions(client)`: A class-based fixture that simplifies login and logout operations for multiple tests.

5. **Isolation and Reproducibility:**  
   - Each test runs in a separate environment to prevent interference.  
   - Uses `pytest` fixtures to handle setup and teardown automatically.  
   - Ensures test results remain consistent and reproducible across different test runs.



2. test_app.py
### **Description of Tests**  
The `test_app.py` module ensures the correct functionality and accessibility of key pages and features within the Flask application. It verifies that pages load properly, user authentication works as expected, and the database is correctly managed. The tests cover rendering of essential pages, handling of shopping cart and checkout logic, authentication behavior, and database integrity. By simulating real user interactions through the Flask test client, these tests help maintain application stability and reliability.

### **Approach to Testing**  
1. **Page Rendering and Static Assets:**  
   - Sends `GET` requests to key pages (home, cart, checkout, products, orders, login, register).  
   - Checks for `200 OK` responses and verifies expected content in the HTML.  
   - Ensures static files like CSS are properly served.

2. **Shopping Cart and Checkout Logic:**  
   - Simulates scenarios where the cart is empty vs. contains items.  
   - Validates redirection when trying to access checkout with an empty cart.  
   - Tests adding items to the cart and proceeding to checkout successfully.

3. **User Authentication and Session Handling:**  
   - Uses `session_transaction()` to simulate logged-in and logged-out states.  
   - Tests login and logout endpoints to verify correct session behavior.  
   - Ensures logout redirects users to the login page.

4. **Database Testing:**  
   - Ensures the database is correctly initialized and contains expected test data.  
   - Tests that database connections close properly after each request.  
   - Uses `verify_database_content()` to validate data integrity.

5. **Error Handling and Edge Cases:**  
   - Tests behavior when accessing pages without authentication.  
   - Ensures invalid or unexpected user actions return proper responses.  
   - Uses `pytest.raises()` to verify that operations fail on closed database connections.



3. test_cart.py
### **Description of Tests**  
The `test_cart.py` module verifies the core functionality of the shopping cart feature in the Flask application. It ensures that users can add and remove items, view the cart contents, and handle session-based shopping behavior correctly. The tests also validate cart persistence, database integrity, and proper error handling when interacting with the cart. Additionally, the cleanup mechanism for old cart entries is tested to ensure that stale data does not persist beyond the expiration period.

### **Approach to Testing**  
1. **Cart Viewing and Rendering:**  
   - Tests whether an empty cart correctly displays no items.  
   - Verifies that cart contents are rendered properly when items are added.  

2. **Adding Items to the Cart:**  
   - Ensures items can be added with a valid `product_id` and `quantity`.  
   - Checks database entries to confirm correct quantity updates.  
   - Verifies that adding the same product multiple times increases the quantity appropriately.  
   - Ensures that adding an item without specifying a quantity defaults to `1`.  

3. **Removing Items from the Cart:**  
   - Confirms that items can be successfully removed from the cart.  
   - Validates that removing an item updates the UI and database correctly.  
   - Tests behavior when attempting to remove items without an active session.  

4. **Checkout and Session Handling:**  
   - Simulates different session states to verify that the cart persists correctly across requests.  
   - Tests session-based shopping behavior to ensure users can maintain cart data.  

5. **Database Integrity and Cleanup:**  
   - Ensures that database updates reflect cart modifications accurately.  
   - Verifies that old cart entries older than a specified time period are automatically removed.  

6. **Error Handling and Edge Cases:**  
   - Tests removing items when no session is set, ensuring a proper redirect.  
   - Checks for proper handling of invalid requests, such as attempting to remove non-existent items.  



4. test_checkout.py
### **Description of Tests**  
The `test_checkout.py` module verifies the checkout functionality of the Flask application. It ensures that users can successfully complete purchases while handling various scenarios, such as authentication requirements, empty carts, invalid sessions, and database integrity issues. The tests simulate real user behavior by testing login flows, cart interactions, and order storage mechanisms, ensuring that the checkout process is secure and error-free.

### **Approach to Testing**  
1. **Authentication and Access Control:**  
   - Ensures that only logged-in users can access the checkout page.  
   - Redirects unauthorized users to the login page.  

2. **Cart Validation and Checkout Flow:**  
   - Prevents checkout when the cart is empty, redirecting users to the cart page.  
   - Ensures that only valid sessions can proceed to checkout.  

3. **Database Integrity and Error Handling:**  
   - Simulates database failures, such as missing tables, and verifies correct error handling.  
   - Ensures that orders are stored correctly, with complete shipping details.  
   - Tests whether the cart is cleared after a successful checkout.  

4. **User Session and Redirection Handling:**  
   - Tests checkout with different session states (valid, invalid, missing).  
   - Ensures that users with missing authentication records are redirected appropriately.  

5. **Order Storage and Data Accuracy:**  
   - Validates that user orders are correctly stored in the database.  
   - Ensures different shipping options are properly recorded.  
   - Tests independent checkout flows for multiple users to prevent data conflicts.  

6. **Edge Cases and Unexpected Scenarios:**  
   - Tests scenarios where a user attempts checkout without confirming the order.  
   - Ensures proper redirection when required session variables are missing.  
   - Handles cases where user records are deleted from the database mid-session.  



5. test_db.py
### **Description of Tests**  
The `test_db.py` module verifies the correctness and reliability of the database functionality within the Flask application. It ensures that database connections are properly managed, the database schema is correctly initialized, and essential data is inserted as expected. The tests validate both the integrity of the database operations and the robustness of error handling when accessing or closing database connections.

### **Approach to Testing**  
1. **Database Connection Management:**  
   - Ensures that `get_db()` consistently returns the same connection within a request context.  
   - Tests that `close_db()` correctly closes the connection, preventing further queries.  

2. **Database Initialization and Schema Validation:**  
   - Verifies that `init_app()` registers the database teardown function properly.  
   - Ensures that calling `initialize_northwind()` correctly sets up essential tables and inserts default records.  

3. **Data Integrity and Verification:**  
   - Confirms that required tables and records exist in the database after initialization.  
   - Uses `verify_database_content()` to check the presence of predefined test data.  

4. **Error Handling and Edge Cases:**  
   - Tests that accessing the database after closing the connection raises a `sqlite3.ProgrammingError`.  
   - Ensures proper handling when attempting to initialize missing or dropped tables.  



6. test_factory.py
### **Description of Tests**  
The `test_factory.py` module verifies the correct configuration of the Flask application factory and the behavior of the `/hello` endpoint. It ensures that the application initializes with the appropriate settings and that a simple API route functions as expected. These tests validate the core setup of the application, confirming its ability to run in both default and testing modes.

### **Approach to Testing**  
1. **Application Configuration Validation:**  
   - Ensures that the application starts in the correct mode based on factory settings.  
   - Checks that `create_app()` does not enable testing mode by default.  
   - Confirms that the `app` fixture correctly initializes in testing mode.  

2. **Hello Endpoint Functionality:**  
   - Sends a `GET` request to `/hello` to verify its response.  
   - Ensures that the endpoint returns the expected `"Hello, World!"` response.  
   - Validates that the response data is returned as a byte string (`b"Hello, World!"`).  



7. test_helpers.py
### **Description of Tests**  
The `test_helpers.py` module contains utility functions to verify the integrity of the test database. The primary function, `verify_database_content()`, ensures that essential records exist in the `Customers` and `Products` tables. This function is used across multiple test modules to validate that the test database is correctly initialized with the expected data before running test cases.

### **Approach to Testing**  
1. **Customer Data Validation:**  
   - Queries the `Customers` table to check if `CustomerID = 'CUST1'` exists.  
   - Verifies that the corresponding `CompanyName` is `"Tech Solutions"`.  

2. **Product Data Validation:**  
   - Queries the `Products` table to check if `ProductName = 'Wireless Mouse'` exists.  
   - Ensures that the `UnitPrice` is `25.99`.  

3. **Assertion-Based Verification:**  
   - Uses `assert` statements to enforce database consistency.  
   - Provides clear error messages when data validation fails.  



8. test_landing.py
### **Description of Tests**  
The `test_landing.py` module verifies the correct functionality and error handling of the landing page. It ensures that the landing page renders successfully and contains the expected content. Additionally, it tests how the application behaves when the template is missing, validating the robustness of error handling.

### **Approach to Testing**  
1. **Landing Page Rendering:**  
   - Sends a `GET` request to `/` to verify the response status code is `200 OK`.  
   - Checks that the response contains the word `"Welcome"` to confirm proper rendering.  

2. **Handling Missing Templates:**  
   - Uses `monkeypatch` to simulate a missing `landing.html` template.  
   - Ensures that the application raises a `TemplateNotFound` exception when the template is unavailable.  


9. test_orders.py
### **Description of Tests**  
The `test_orders.py` module verifies the correct functionality of the order management system in the Flask application. It ensures that users can place orders, view their order history, and that the cart is properly cleared after a successful checkout. These tests also validate authentication enforcement, database consistency, and order display behavior.

### **Approach to Testing**  
1. **Authentication and Access Control:**  
   - Ensures users must be logged in to view the `/orders/` page.  
   - Redirects unauthenticated users to the login page when accessing order history.  

2. **Order Creation and Checkout Flow:**  
   - Tests that an order is successfully created when a user completes checkout.  
   - Verifies that after checkout, the user is redirected to the `/orders/` page.  

3. **Database Integrity and Data Storage:**  
   - Confirms that order details are correctly stored in the `Orders` table.  
   - Ensures that shipping details (name, address, shipping method) are properly recorded.  
   - Validates that orders are associated with the correct customer and employee ID.  

4. **Order History and Multiple Orders Handling:**  
   - Ensures users with no orders see an appropriate message (`"You have no orders yet"`).  
   - Verifies that multiple orders display correctly in the order history page.  
   - Checks that different shipping methods (Standard, Express) are displayed properly.  

5. **Shopping Cart Clearance:**  
   - Ensures that after a successful checkout, the cart is emptied in both the database and session.  
   - Prevents cart persistence across multiple orders to maintain consistency.  

6. **Edge Cases and Error Handling:**  
   - Tests order display behavior when no previous orders exist.  
   - Ensures that order creation correctly associates with an authenticated user session.  



10. test_products.py
### **Description of Tests**  
The `test_products.py` module verifies the functionality of the product listing and filtering system in the Flask application. It ensures that users can view available products, search for specific items, filter by category, and access product details. These tests help confirm that product data is displayed correctly and that search and filtering mechanisms function as expected.

### **Approach to Testing**  
1. **Product Listing and General Display:**  
   - Sends a `GET` request to `/products` to verify that the page loads correctly.  
   - Checks that expected elements like `"Our Products"`, search bars, and categories are present.  

2. **Search Functionality:**  
   - Searches for a specific product name (e.g., `"Wireless Mouse"`) and verifies it appears in the results.  
   - Ensures that searching for a non-existent product displays `"No matching products found"`.  
   - Tests behavior when an empty search string is submitted, ensuring all products are displayed.  

3. **Category Filtering:**  
   - Filters products by category and verifies that only relevant products appear.  
   - Tests combining search and category filters to ensure correct behavior.  
   - Ensures that an invalid category ID does not break functionality and that all products are displayed in such cases.  

4. **Product Details Verification:**  
   - Checks that key product attributes (stock availability, category, quantity, and purchase options) are displayed correctly.  



11. test_user.py
### **Description of Tests**  
The `test_user.py` module verifies the core functionality of user authentication and session management in the Flask application. It ensures that users can register, log in, and log out correctly, while also handling edge cases such as incorrect credentials, incomplete registration, and session inconsistencies. These tests confirm that authentication mechanisms are secure and robust.

### **Approach to Testing**  
1. **User Registration:**  
   - Tests successful registration and verifies that user credentials are correctly stored in the database.  
   - Ensures appropriate error handling for invalid inputs (e.g., empty username/password, incorrect username length).  
   - Prevents duplicate registrations by rejecting existing usernames.  

2. **User Login:**  
   - Verifies that users can log in successfully with correct credentials.  
   - Checks session persistence by confirming `user_id` is stored in the session upon login.  
   - Ensures incorrect credentials (wrong username/password) result in appropriate error messages.  

3. **Session Management and Logout:**  
   - Confirms that logging out correctly removes the session and redirects the user.  
   - Tests that different session IDs trigger session updates for shopping cart data.  

4. **Handling Incomplete Registration:**  
   - Ensures users that exist in the `Customers` table but not in `Authentication` are redirected to complete registration.  
   - Displays appropriate messages to guide users through the registration process.  

5. **Session and Authentication Consistency:**  
   - Ensures session updates occur when a user logs in with a new session ID.  
   - Validates that session-related authentication updates are correctly reflected in the database.  

6. **Edge Cases and Security:**  
   - Prevents login with empty credentials.  
   - Ensures that authentication checks enforce the required username length.  
   - Tests handling of users who attempt to log in but are missing from the database.  



Additional Information
----------------------------------

1. Pylint Test Aspects
In our conftest.py file, we must use the following comment:
# pylint: disable=redefined-outer-name
This is necessary because of how pytest’s fixture injection works. Pytest requires that fixtures be passed into test functions by matching parameter names, which leads to the same name appearing in multiple scopes. Although pylint flags this as "redefined-outer-name," it’s an expected behavior in pytest. Renaming the fixtures isn’t a viable solution, as it would either introduce new conflicts or break the dependency injection mechanism. Therefore, adding this comment is the best way to handle the warning without affecting our tests.


2. Enhanced Product Page Design
In our product page, we have adopted a more intuitive design, making significant improvements to the logical structure of the page layout. Instead of following the traditional approach where the main product page consists only of product links—requiring users to click each link to navigate to a separate detailed product information page—we have streamlined the experience by integrating all essential product details into a single page.  

This enhancement eliminates unnecessary steps for users. Rather than navigating through multiple pages, users can now browse product details, filter by category, search for specific products, and add items to their cart all within the same interface. The product page is no longer just a collection of links but a comprehensive display of product information, providing a more seamless, efficient, and intuitive shopping experience.



3. Databse Set Up Improvement
In aour assignment, it only requires to programatically setting up the database of employees realtion by adding a dommy employees "WEB" in it. However, we improve this, all the additional tables and this new line will be inserted and created programatically and automatically. User do not have to manulaly run the "flask --app flaskr init-db" to initialize our database. It can be more intutive and fluent in using process.







