"""Module tests for product functionality."""

from flask import Flask
from flask.testing import FlaskClient


def test_list_products(client: FlaskClient) -> None:
    """Test basic product listing without filters."""
    response = client.get("/products")
    assert response.status_code == 200
    html = response.get_data(as_text=True)

    # Check if some expected elements are present.
    assert "Our Products" in html
    assert "Search products..." in html
    assert "All Categories" in html


# pylint: disable=unused-argument
def test_search_products(client: FlaskClient, app: Flask) -> None:
    """Test product search functionality."""
    # Test search for "Wireless".
    response = client.get("/products?search=Wireless")
    assert response.status_code == 200
    html = response.get_data(as_text=True)

    # Should find "Wireless Mouse" from test data.
    assert "Wireless Mouse" in html
    assert "$25.99" in html  # Price from test data.

    # Test search with no results.
    response = client.get("/products?search=NonexistentProduct")
    assert response.status_code == 200
    html = response.get_data(as_text=True)  # Get the new HTML response.
    assert "No matching products found" in html


# pylint: disable=unused-argument
def test_category_filter(client: FlaskClient, app: Flask) -> None:
    """Test category filtering."""
    # Test category 1 (from test data).
    response = client.get("/products?category=1")
    assert response.status_code == 200
    html = response.get_data(as_text=True)

    # Should show products from category 1.
    assert "Wireless Mouse" in html
    assert "Keyboard" in html


def test_combined_search_and_category(client):
    """Test combining search and category filters."""
    response = client.get("/products?search=Wireless&category=1")
    assert response.status_code == 200
    html = response.get_data(as_text=True)

    # Should only show Wireless Mouse in category 1.
    assert "Wireless Mouse" in html
    assert "Keyboard" not in html


def test_invalid_category(client):
    """Test handling of invalid category ID."""
    response = client.get("/products?category=invalid")
    assert response.status_code == 200
    html = response.get_data(as_text=True)

    # Should show all products when category is invalid.
    assert "Wireless Mouse" in html
    assert "Keyboard" in html


def test_empty_search(client: FlaskClient) -> None:
    """Test empty search string behavior."""
    response = client.get("/products?search=")
    assert response.status_code == 200
    html = response.get_data(as_text=True)

    # Should show all products.
    assert "Wireless Mouse" in html
    assert "Keyboard" in html


def test_product_details_display(client: FlaskClient) -> None:
    """Test if product details are correctly displayed."""
    response = client.get("/products")
    assert response.status_code == 200
    html = response.get_data(as_text=True)

    # Check if product details are present.
    assert "Stock" in html
    assert "Category" in html
    assert "Quantity(Unit)" in html
    assert "Add to Cart" in html
