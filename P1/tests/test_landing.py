"""测试 landing 页面功能的模块."""

from typing import Any  # 标准库导入
from jinja2 import TemplateNotFound
import pytest
from flask.testing import FlaskClient


def test_landing_page(client: FlaskClient) -> None:
    """测试 landing 页面是否返回状态码 200 并包含 'Welcome' 字样."""
    response = client.get("/")
    assert response.status_code == 200
    # 如果 landing 页面中包含 "Welcome" 文本:
    assert b"Welcome" in response.data


def test_missing_template(client: FlaskClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """测试当模板缺失时 landing 页面的异常情况."""
    # 模拟模板缺失的场景
    def mock_render_template(*args: Any, **kwargs: Any) -> None:
        raise TemplateNotFound("landing.html")

    monkeypatch.setattr("flaskr.landing.render_template", mock_render_template)

    with pytest.raises(TemplateNotFound):
        client.get("/")
