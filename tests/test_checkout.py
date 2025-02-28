import pytest
from flaskr.db import get_db
from typing import Any

@pytest.fixture
def auth(client: Any) -> Any:
    class AuthActions:
        def login(self, username: str, password: str) -> Any:
            return client.post("/user/login", data={"username": username, "password": password})

        def logout(self) -> Any:
            return client.get("/user/logout")

    return AuthActions()


def test_checkout_requires_login(client: Any, auth: Any, app: Any) -> None:
    """Ensure users must be logged in to access checkout."""
    response = client.get("/checkout/")
    assert response.status_code == 302
    assert response.headers["Location"] == "/user/login"

    client.post("/user/register", data={"username": "NEWUS", "password": "newpassword"})
    response = auth.login("NEWUS", "newpassword")
    assert response.status_code == 302
    assert response.headers["Location"] == "/products"


def test_checkout_empty_cart(client: Any, auth: Any) -> None:
    """Ensure users cannot checkout with an empty cart."""
    client.post("/user/register", data={"username": "NEWUS", "password": "newpassword"})
    auth.login("NEWUS", "newpassword")
    response = client.get("/checkout/")
    assert response.status_code == 302
    assert response.headers["Location"] == "/cart/"


def test_checkout_invalid_session(client: Any, auth: Any) -> None:
    """Ensure users with invalid sessions are redirected to login."""
    auth.login("NEWUS", "newpassword")
    with client.session_transaction() as sess:
        sess["session_id"] = "fake-session-xyz"
    response = client.get("/checkout/")
    assert response.status_code == 302
    assert response.headers["Location"] == "/user/login"


def test_checkout_database_error(client: Any, auth: Any, app: Any) -> None:
    """Ensure database errors during checkout are handled correctly."""
    client.post("/user/register", data={"username": "NEWUS", "password": "newpassword"})
    auth.login("NEWUS", "newpassword")
    client.post("/cart/add/", data={"product_id": "42", "quantity": "2"})

    with app.app_context():
        db = get_db()
        db.execute("DROP TABLE Orders")  # Induce a DB error
        db.commit()

    response = client.post("/checkout/", data={
        "ship_name": "John Doe",
        "ship_address": "123 Main St",
        "ship_city": "Anytown",
        "ship_country": "USA",
        "place_order": "true"
    })

    assert response.status_code == 302
    assert response.headers["Location"] == "/cart/"


def test_checkout_get_request(client: Any, auth: Any) -> None:
    """Ensure GET requests to checkout page return the correct template."""
    client.post("/user/register", data={"username": "NEWUS", "password": "newpassword"})
    auth.login("NEWUS", "newpassword")

    client.post("/cart/add/", data={"product_id": "1", "quantity": "1"})

    response = client.get("/checkout/")
    assert response.status_code == 200
    assert b"Checkout" in response.data


def test_successful_checkout_clears_cart(client: Any, auth: Any, app: Any) -> None:
    """Ensure successful checkout clears the cart."""
    client.post("/user/register", data={"username": "NEWUS", "password": "newpassword"})
    auth.login("NEWUS", "newpassword")

    client.post("/cart/add/", data={"product_id": "1", "quantity": "1"})

    response = client.post("/checkout/", data={
        "ship_name": "John Doe",
        "ship_address": "123 Main St",
        "ship_city": "Anytown",
        "ship_country": "USA",
        "place_order": "true"
    })
    assert response.status_code == 302
    assert response.headers["Location"] == "/orders/"

    # Get the session_id
    with client.session_transaction() as sess:
        session_id = sess["session_id"]

    with app.app_context():
        db = get_db()
        cart_count = db.execute(
            "SELECT COUNT(*) FROM Shopping_cart WHERE ShopperID = ?",
            (session_id,)
        ).fetchone()[0]
        assert cart_count == 0


def test_order_is_correctly_stored(client: Any, auth: Any, app: Any) -> None:
    """Ensure order details are correctly stored in the database."""
    client.post("/user/register", data={"username": "NEWUS", "password": "newpassword"})
    auth.login("NEWUS", "newpassword")

    client.post("/cart/add/", data={"product_id": "1", "quantity": "1"})

    response = client.post("/checkout/", data={
        "ship_name": "John Doe",
        "ship_address": "123 Main St",
        "ship_city": "Anytown",
        "ship_country": "USA",
        "place_order": "true"
    })
    assert response.status_code == 302
    assert response.headers["Location"] == "/orders/"

    with app.app_context():
        db = get_db()
        order = db.execute(
            "SELECT * FROM Orders WHERE CustomerID = ?",
            ("NEWUS",)
        ).fetchone()
        assert order is not None
        assert order["ShipName"] == "John Doe"
        assert order["ShipAddress"] == "123 Main St"
        assert order["ShipCity"] == "Anytown"
        assert order["ShipCountry"] == "USA"


def test_checkout_with_different_shipping_options(client: Any, auth: Any, app: Any) -> None:
    """Ensure different shipping options are correctly stored."""
    client.post("/user/register", data={"username": "NEWUS", "password": "newpassword"})
    auth.login("NEWUS", "newpassword")

    client.post("/cart/add/", data={"product_id": "1", "quantity": "1"})

    response = client.post("/checkout/", data={
        "ship_name": "Alice Smith",
        "ship_address": "456 Elm St",
        "ship_city": "Smalltown",
        "ship_region": "CA",
        "ship_postal_code": "12345",
        "ship_country": "USA",
        "ship_via": "2",
        "place_order": "true"
    })
    assert response.status_code == 302
    assert response.headers["Location"] == "/orders/"

    with app.app_context():
        db = get_db()
        order = db.execute(
            "SELECT * FROM Orders WHERE CustomerID = ?",
            ("NEWUS",)
        ).fetchone()
        assert order is not None
        assert order["ShipName"] == "Alice Smith"
        assert order["ShipAddress"] == "456 Elm St"
        assert order["ShipCity"] == "Smalltown"
        assert order["ShipRegion"] == "CA"
        assert order["ShipPostalCode"] == "12345"
        assert order["ShipCountry"] == "USA"
        assert order["ShipVia"] == 2


def test_multiple_users_checkout_separately(client: Any, auth: Any, app: Any) -> None:
    """Ensure multiple users can checkout independently without conflicts."""
    client.post("/user/register", data={"username": "USER1", "password": "pass1"})
    auth.login("USER1", "pass1")
    client.post("/cart/add/", data={"product_id": "1", "quantity": "2"})

    # Switch user
    client.post("/user/register", data={"username": "USER2", "password": "pass2"})
    auth.login("USER2", "pass2")
    client.post("/cart/add/", data={"product_id": "2", "quantity": "1"})

    response1 = client.post("/checkout/", data={
        "ship_name": "User One",
        "ship_address": "111 First St",
        "ship_city": "CityA",
        "ship_country": "USA",
        "place_order": "true"
    })

    response2 = client.post("/checkout/", data={
        "ship_name": "User Two",
        "ship_address": "222 Second St",
        "ship_city": "CityB",
        "ship_country": "Canada",
        "place_order": "true"
    })

    assert response1.status_code == 302
    assert response2.status_code == 302



def test_checkout_no_place_order(client: Any, auth: Any, app: Any) -> None:
    """
    Test the code path where the user does not provide 'place_order',
    which should trigger the 'else' path returning redirect to 'cart.view_cart'.
    """
    client.post("/user/register", data={"username": "NEWUS", "password": "newpassword"})
    auth.login("NEWUS", "newpassword")

    client.post("/cart/add/", data={"product_id": "1", "quantity": "1"})

    response = client.post("/checkout/", data={
        # Notice we are NOT including 'place_order'
        "ship_name": "No Order",
        "ship_address": "111 AAA St",
        "ship_city": "CityX",
        "ship_country": "USA"
    })
    # The code path leads to: else: return redirect(url_for("cart.view_cart"))
    assert response.status_code == 302
    assert response.headers["Location"] == "/cart/"


def test_checkout_missing_employee(client: Any, auth: Any, app: Any) -> None:
    """
    Test scenario when the 'WEB' employee record is missing,
    we expect the code to raise an Exception or handle it,
    thus covering that part of the 'try/except' block.
    """
    # Remove the 'WEB' employee from Employees (ID=999999) if it exists
    with app.app_context():
        db = get_db()
        db.execute("DELETE FROM Employees WHERE EmployeeID = 999999 AND LastName = 'WEB'")
        db.commit()

    client.post("/user/register", data={"username": "NEWUS", "password": "newpassword"})
    auth.login("NEWUS", "newpassword")

    client.post("/cart/add/", data={"product_id": "1", "quantity": "1"})

    response = client.post("/checkout/", data={
        "ship_name": "John Missing",
        "ship_address": "123 NoEmployee Rd",
        "ship_city": "Nowhere",
        "ship_country": "USA",
        "place_order": "true"
    })
    # We expect an error to happen in the 'try' block when trying to fetch employee["EmployeeID"]
    # The code then goes to 'except Exception as e' -> rollback -> flash -> redirect
    assert response.status_code == 302
    assert response.headers["Location"] == "/cart/"



def test_checkout_no_cart_found_alt(client: Any, auth: Any) -> None:
    """
    Alternative approach to trigger 'if not cart_id:' branch,
    ensuring user_id is still in session but cart_id is None.
    """
    # 1. Register & log in
    client.post("/user/register", data={"username": "ALTUSER", "password": "altpass"})
    auth.login("ALTUSER", "altpass")

    # 2. Force session_id to None, but also ensure user_id = 'ALTUSER' is still there
    with client.session_transaction() as sess:
        sess["user_id"] = "ALTUSER"      # 🔑 强行确保 user_id 依旧存在
        sess["session_id"] = None        # 🔑 session_id 置空

    # 3. 访问 /checkout/
    response = client.get("/checkout/")

    # 期望命中：if not cart_id => redirect(url_for('cart.view_cart'))
    assert response.status_code == 302
    assert response.headers["Location"] == "/cart/"


def test_checkout_post_no_user_in_session(client: Any, auth: Any) -> None:
    """If request.method == 'POST' but 'user_id' or 'session_id' not in session => /user/login."""
    # 先登录
    client.post("/user/register", data={"username": "NOUSER", "password": "pass123"})
    auth.login("NOUSER", "pass123")

    # 删除 user_id, session_id（如果存在的话）
    with client.session_transaction() as sess:
        sess.pop("user_id", None)
        sess.pop("session_id", None)

    # 发送 POST /checkout/
    response = client.post("/checkout/", data={
        "ship_name": "NoUser",
        "ship_address": "999 Nowhere",
        "ship_city": "Invisible",
        "ship_country": "USA",
        "place_order": "true"
    })

    assert response.status_code == 302
    assert response.headers["Location"] == "/user/login"


def test_checkout_post_user_not_in_db(client: Any, auth: Any, app: Any) -> None:
    """
    If user_id/session_id exist in session, but database has no record for them,
    user_row is None => code returns redirect('/user.login').
    """
    # 注册 + 登录 => session 有 user_id, session_id
    client.post("/user/register", data={"username": "MISSINGUSER", "password": "pass456"})
    auth.login("MISSINGUSER", "pass456")

    with app.app_context():
        db = get_db()
        # 在 Authentication 中删除这条用户 => 下次查 user_row => None
        db.execute("DELETE FROM Authentication WHERE UserID = ?", ("MISSINGUSER",))
        db.commit()

    # 确保 session_transaction 不删除 session_id
    # 这样 'user_id' & 'session_id' 在 session 中还存在
    with client.session_transaction() as sess:
        # user_id = MISSINGUSER, session_id 保持原样
        pass

    # 发起 POST => code查看 user_row = None => redirect /user.login
    response = client.post("/checkout/", data={
        "ship_name": "Missing DB",
        "ship_address": "101 Ghost Ln",
        "ship_city": "Nonexistent",
        "ship_country": "USA",
        "place_order": "true"
    })

    # 期望 /user.login
    assert response.status_code == 302
    assert response.headers["Location"] == "/user/login"
