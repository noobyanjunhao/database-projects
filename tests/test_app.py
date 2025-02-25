import pytest

def test_homepage(client):
    """
    测试首页是否正确渲染
    """
    response = client.get("/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Welcome to TJ's Shopping" in html  # 确保首页包含标题
    assert "Start Shopping" in html  # 确保按钮文本存在

def test_static_assets(client):
    """
    测试静态资源是否可以正确加载（如 CSS 文件）
    """
    response = client.get("/static/style.css")
    assert response.status_code == 200

def test_cart_page(client):
    """
    测试购物车页面是否可访问
    """
    response = client.get("/cart/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Shopping Cart" in html  # 确保购物车页面正确渲染

def test_checkout_page_from_empty_cart(client):
    """
    测试结账页面是否可访问 when cart is empty.
    """
    # Simulate a logged-in user by setting session variables.
    with client.session_transaction() as sess:
        sess['user_id'] = 'SOMEUSER'
        sess['session_id'] = 'some-session'
    
    # Option A: If the cart is empty, expect a redirect to /cart/
    response = client.get("/checkout/")
    assert response.status_code == 302
    assert response.headers['Location'] == '/cart/'

def test_checkout_page_from_non_empty_cart(client):
    """
    测试结账页面是否可访问 when cart is not empty.
    """
    # Simulate a logged-in user by setting session variables.
    with client.session_transaction() as sess:
        sess['user_id'] = 'SOMEUSER'
        sess['session_id'] = 'some-session'
    
    # Add an item to the cart so the cart is not empty.
    client.post('/cart/add/', data={'product_id': '1', 'quantity': '1'})
    
    # Now, GET the checkout page.
    response = client.get("/checkout/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Checkout" in html  # 确保结账页面正确渲染



def test_products_page(client):
    """
    测试产品页面是否可访问
    """
    response = client.get("/products")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Products" in html  # 确保产品页面正确渲染

def test_orders_page(client):
    """
    测试订单页面是否可访问
    """
    # Simulate a logged-in user
    with client.session_transaction() as sess:
        sess['user_id'] = 'NEWUS'
        sess['session_id'] = 'test-session-123'
    
    response = client.get("/orders/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Orders" in html  # 确保订单页面正确渲染


def test_login_page(client):
    """
    测试登录页面是否可访问
    """
    response = client.get("/user/login")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Log In" in html  # 确保登录页面正确渲染

def test_register_page(client):
    """
    测试注册页面是否可访问
    """
    response = client.get("/user/register")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Register" in html  # 确保注册页面正确渲染

def test_logout_redirect(client):
    """
    测试注销后是否正确重定向
    """
    response = client.get("/user/logout", follow_redirects=True)
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Log In" in html  # 注销后应该回到登录页面

def test_hello_route(client):
    """
    测试 `/hello` 端点是否返回正确的字符串
    """
    response = client.get("/hello")
    assert response.status_code == 200
    assert response.data == b"Hello, World!"

