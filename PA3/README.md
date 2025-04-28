# Rent Management System

## 1. Project Overview

The **Rent Management System** is designed to help landlords and property managers efficiently manage rental units, bills, and payments. The system provides a centralized dashboard where users can create and manage bills, track tenant payments, view unit information, and export data when needed.

**Target Audience:**

- Property Managers
- Landlords
- Real Estate Administrative Staff

This system provides a simple, efficient, and user-friendly interface to handle common rental management tasks.

---

## 2. Team Members and Their Roles

| Name             | Role                         | Responsibilities                                                                          |
| ---------------- | ---------------------------- | ----------------------------------------------------------------------------------------- |
| **Dave Wang**    | Team Leader                  | Database design, back-end development, front-end styling                                  |
| **Junhao Yan**   | Backend Development Engineer | Backend feature development, test case writing                                            |
| **Ruohang Feng** | Backend Development Engineer | Backend feature development, test case writing                                            |
| **Bo Zhang**     | Test Engineer                | Conducting all tests (pytest, mypy, pylint), ensuring quality assurance                   |
| **Boyu Shen**    | Documentation Specialist     | Drafting and maintaining project documentation including README.md, front-end development |

---

## 3. Local Installation and Startup Guide

### Environment Setup

1. **Navigate to project folder**

   ```bash
   cd PA3
   ```

2. **Check Python version**

   ```bash
   python3 --version
   ```

   - **Required Version:** Python **3.10.8**
   - If your version is not 3.10.8, you must switch or install this version.
   - Download it here: [Python 3.10.8 - Oct. 11, 2022](https://www.python.org/downloads/macos/)

3. **Set up virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

5. **Run the Flask application**

   ```bash
   flask --app flaskr run
   ```

   - This command will automatically create the necessary database and populate it with **dummy data**.

---

## 4. Testing Description and Approach

### General Testing Strategy

We adopted a thorough **Test-Driven Development (TDD)** approach for this project, ensuring code quality, correctness, and style consistency.

Our testing layers include:

- **Unit Testing:** Validates small units of logic.
- **Integration Testing:** Validates end-to-end workflows.
- **Static Type Checking:** Using `mypy` for type correctness.
- **Linting:** Using `pylint` to ensure code style and maintainability.

### How to Run All Tests

1. Make sure the virtual environment is activated:

   ```bash
   source venv/bin/activate
   ```

2. Run **pytest** for unit and integration tests:

   ```bash
   pytest
   ```

   ```bash
   coverage run -m pytest
   ```

   ```bash
   coverage report -m
   ```
   
3. Run **mypy** for static type checking:

   ```bash
   mypy flaskr tests
   ```

4. Run **pylint** for style checking:

   ```bash
   pylint flaskr tests
   ```

---

### Detailed Test Descriptions

#### `tests/test_main.py`

- `test_index_route(client)`
  - Verifies that the index (home) page loads successfully with HTTP 200 status. Also ensures the page contains basic HTML structure by checking for `<html>` tag.

- `test_dashboard_route(client)`
  - Ensures that the dashboard page loads correctly and returns an HTTP 200 response. Confirms that HTML content is properly rendered by checking for the `<html>` tag.

#### `tests/test_export.py`

- `test_export_units_excel_response(monkeypatch, client)`
  - Tests that exporting units returns a valid Excel file with the correct content type and file name. Ensures the file structure matches expected format.

#### `tests/test_db.py`

- `test_get_db_returns_same_connection(app)`
  - Ensures that multiple calls to `get_db()` within the same application context return the same database connection object, confirming correct connection caching behavior.

- `test_close_db_removes_and_closes(app)`
  - Tests that calling `close_db()` correctly closes and removes the database connection from the app context, and raises an error if the closed connection is accessed.

- `test_init_db_with_string_content(app)`
  - Mocks database initialization with a simple SQL schema string. Verifies that a test table is properly created, ensuring `init_db` can handle different schema content.

#### `tests/test_bill.py`

- `test_bill_payment_dashboard_filters(monkeypatch, client, qs)`
  - Tests various filtering scenarios on the bill-payment dashboard using dummy data. It verifies that filtering by ownership type, tenant name, and special unit status works as expected.

- `test_create_and_detail_and_payment_paths(monkeypatch, client)`
  - This comprehensive test covers bill creation, bill detail retrieval, payment creation, and payment detail retrieval under different scenarios, including missing data, database errors, and successful transactions.

#### `tests/test_unit.py`

- `test_units_overview_branches(monkeypatch, client, qs)`
  - Tests the units overview page under different search and filter query parameters. Verifies that relevant unit data appears correctly.

- `test_unit_detail_and_balance(monkeypatch, client)`
  - Tests the unit detail page, including correct balance calculation even when invalid JSON for charges is encountered.

- `test_update_lease_paths(monkeypatch, client)`
  - Tests lease update functionality, covering both missing lease record handling and successful lease update with proper commitment.

- `test_dummydb_commit_sets_flag()`
  - Verifies that calling `commit()` on the dummy database correctly sets a committed flag, ensuring mock database behavior consistency.

#### `tests/test_init.py`

- `test_create_app_defaults(app)`
  - Verifies that the default configuration of the Flask app includes testing mode enabled, a default secret key, and the presence of the database file.

- `test_init_db_command(runner)`
  - Confirms that running the custom CLI command `init-db` initializes the database successfully, and outputs the expected success message.

- `test_create_app_with_test_config()`
  - Tests that `create_app` properly accepts and applies a given test configuration dictionary, overriding the default settings.

#### `tests/conftest.py`

- `app(tmp_path)`
  - Creates a new isolated Flask app instance configured for testing, using a temporary SQLite database and injecting dummy data for consistent test conditions.

- `client(app)`
  - Provides a Flask test client used to simulate HTTP requests during testing, enabling easy endpoint validation.

- `runner(app)`
  - Supplies a CLI runner that allows for testing command-line interactions with the Flask app.

---

### Additional Notes

- All the test cases are organized to ensure modularity and easy maintenance.
- Tests are idempotent: running them multiple times will not affect the database or application state.
- The `conftest.py` file provides reusable fixtures such as dummy database connections and test clients.

---

# Thank you for using the Rent Management System!

For any issues, feel free to open an issue ticket.

