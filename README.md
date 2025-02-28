Flask E-Commerce Project
========================

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
Semit Test-Driven Development:
  - We started with writing majority of the functionalities as much as we could so that our project has a basic form of structure.
  - We then wrote tests for each feature to further complete all functionalities.
  - Our test suite covers user authentication, shopping cart operations, checkout 
    flow, orders, and overall error handling.

Features
--------
User Authentication:
  - Secure registration and login with case-insensitive user IDs (converted to uppercase).

Database Enhancements:
  - The Authentication table is integrated with the Customers table for streamlined 
    user management.

Robust Checkout Flow:
  - The checkout route redirects to the cart page if the shopping cart is empty.
  - If a database error occurs during order placement (e.g., the Orders table is missing), the error is caught, the transaction is rolled back, and the user is redirected back to the cart with an appropriate error message.

Modular Design:
  - The application is organized using Flask blueprints (for user authentication, products, cart, checkout, and orders), making it easier to maintain and extend.

Testing Coverage:
  - Extensive tests for both positive and negative scenarios ensure that the solution is robust and reliable.

Feedback
--------
We welcome feedback and suggestions for further improvements. Thank you for reviewing our project!
